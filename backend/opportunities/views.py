from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IsStaffUser
from .email_notifications import notify_new_application
from .models import Application, ApplicationStatusEvent, GuestAccessToken, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, StaffNotification, SuccessStory
from .guest_access import consume_token, create_claim_token
from .serializers import ApplicationSerializer, ApplicationStatusEventSerializer, InquirySerializer, OpportunitySerializer, PaymentRecordSerializer, SavedOpportunitySerializer, StaffNotificationSerializer, SuccessStorySerializer


class OpportunityListView(generics.ListAPIView):
    serializer_class = OpportunitySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "summary", "country", "category", "region"]
    ordering_fields = ["deadline", "title", "created_at"]

    def get_queryset(self):
        queryset = Opportunity.objects.all()
        for field in ["category", "region", "status"]:
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset


class OpportunityDetailView(generics.RetrieveAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    lookup_field = "slug"


class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        owner_open_id = getattr(self.request.user, "open_id", "") if getattr(self.request.user, "is_authenticated", False) else ""
        application = serializer.save(status="payment_required", owner_open_id=owner_open_id)
        ApplicationStatusEvent.objects.create(application=application, status="payment_required", note="Application submitted. Payment integration will be enabled here.")
        PaymentRecord.objects.create(application=application, amount=2000, currency="RWF", status="integration_pending")
        StaffNotification.objects.create(event_type="application_submitted", title="New application submitted", message=f"{application.full_name} submitted an application for {application.opportunity.title}.", application=application)
        notify_new_application(application)
        if not owner_open_id:
            from .email_notifications import notify_guest_access
            notify_guest_access(application, self.request.build_absolute_uri("/").rstrip("/"))


class GuestVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = consume_token(request.query_params.get("token", ""), "verify")
        if not token:
            return Response({"detail": "This verification link is invalid or expired."}, status=status.HTTP_410_GONE)
        token.used_at = timezone.now()
        token.save(update_fields=["used_at"])
        claim_token = create_claim_token(token.application)
        application = token.application
        return Response({
            "verified": True,
            "claim_token": claim_token,
            "application": {"id": application.id, "full_name": application.full_name, "email": application.email, "status": application.status, "status_label": application.get_status_display(), "opportunity_title": application.opportunity.title},
        })


class GuestStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = consume_token(request.query_params.get("token", ""), "status")
        if not token:
            return Response({"detail": "This status link is invalid or expired."}, status=status.HTTP_410_GONE)
        application = token.application
        return Response({
            "application": {"id": application.id, "full_name": application.full_name, "status": application.status, "status_label": application.get_status_display(), "opportunity_title": application.opportunity.title, "created_at": application.created_at, "updated_at": application.updated_at},
            "events": ApplicationStatusEventSerializer(application.status_events.all(), many=True).data,
        })


class GuestClaimApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = consume_token(str(request.data.get("claim_token", "")), "claim")
        if not token:
            return Response({"detail": "This claim request is invalid or expired."}, status=status.HTTP_410_GONE)
        application = token.application
        if application.owner_open_id and application.owner_open_id != request.user.open_id:
            return Response({"detail": "This application is already linked to another account."}, status=status.HTTP_409_CONFLICT)
        application.owner_open_id = request.user.open_id
        application.save(update_fields=["owner_open_id", "updated_at"])
        token.used_at = timezone.now()
        token.save(update_fields=["used_at"])
        return Response({"claimed": True, "application_id": application.id})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email", "").strip().lower()
        if not email:
            return Response({"detail": "An email address is required."}, status=status.HTTP_400_BAD_REQUEST)
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        owner_open_id = request.user.open_id
        applications = Application.objects.filter(owner_open_id=owner_open_id).select_related("opportunity").prefetch_related("status_events", "payment")
        saved = SavedOpportunity.objects.filter(owner_open_id=owner_open_id).select_related("opportunity")
        return Response({
            "email": email,
            "applications": ApplicationSerializer(applications, many=True).data,
            "saved_opportunities": SavedOpportunitySerializer(saved, many=True).data,
        })


class ApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        email = request.query_params.get("email", "").strip().lower()
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        application = get_object_or_404(Application, id=application_id, owner_open_id=request.user.open_id)
        return Response({
            "application": ApplicationSerializer(application).data,
            "events": ApplicationStatusEventSerializer(application.status_events.all(), many=True).data,
            "payment": PaymentRecordSerializer(getattr(application, "payment", None)).data if hasattr(application, "payment") else None,
        })


class SavedOpportunityListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email", "").strip().lower()
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        saved = SavedOpportunity.objects.filter(email__iexact=email).select_related("opportunity")
        return Response(SavedOpportunitySerializer(saved, many=True).data)

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        opportunity_id = request.data.get("opportunity")
        if not email or not opportunity_id:
            return Response({"detail": "Email and opportunity are required."}, status=status.HTTP_400_BAD_REQUEST)
        opportunity = get_object_or_404(Opportunity, id=opportunity_id)
        saved, _ = SavedOpportunity.objects.get_or_create(email=email, owner_open_id=request.user.open_id, opportunity=opportunity)
        return Response(SavedOpportunitySerializer(saved).data, status=status.HTTP_201_CREATED)


class SavedOpportunityDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, opportunity_id):
        email = request.query_params.get("email", "").strip().lower()
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        deleted, _ = SavedOpportunity.objects.filter(owner_open_id=request.user.open_id, opportunity_id=opportunity_id).delete()
        return Response({"deleted": bool(deleted)})


class PaymentPrepareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        if request.headers.get("X-Dashboard-Email", "").strip().lower() != email:
            return Response({"detail": "Dashboard identity could not be verified."}, status=status.HTTP_403_FORBIDDEN)
        provider = str(request.data.get("provider", "")).strip().lower()
        application_id = request.data.get("application")
        if provider not in {"momo", "airtel"}:
            return Response({"detail": "Choose MoMo or Airtel Money."}, status=status.HTTP_400_BAD_REQUEST)
        application = get_object_or_404(Application, id=application_id, owner_open_id=request.user.open_id)
        payment, _ = PaymentRecord.objects.get_or_create(application=application, defaults={"amount": 2000, "currency": "RWF"})
        payment.provider = provider
        payment.status = "integration_pending"
        payment.save(update_fields=["provider", "status", "updated_at"])
        StaffNotification.objects.create(event_type="payment_status", title="Payment provider selected", message=f"{application.full_name} selected {payment.get_provider_display()} for the 2,000 RWF service fee.", application=application)
        return Response({"payment": PaymentRecordSerializer(payment).data, "message": "Provider integration is not enabled yet. Your application remains safely recorded and payment can be completed when the service is connected."}, status=status.HTTP_202_ACCEPTED)


class StaffNotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request):
        queryset = StaffNotification.objects.select_related("application").all()
        event_type = request.query_params.get("event_type")
        read_filter = request.query_params.get("read", "all")
        if event_type in {choice[0] for choice in StaffNotification.EVENT_CHOICES}:
            queryset = queryset.filter(event_type=event_type)
        if read_filter == "unread":
            queryset = queryset.filter(is_read=False)
        elif read_filter == "read":
            queryset = queryset.filter(is_read=True)
        return Response({"unread_count": StaffNotification.objects.filter(is_read=False).count(), "notifications": StaffNotificationSerializer(queryset[:100], many=True).data})


class StaffNotificationReadView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def patch(self, request, notification_id):
        notification = get_object_or_404(StaffNotification, id=notification_id)
        notification.is_read = bool(request.data.get("is_read", True))
        notification.save(update_fields=["is_read"])
        return Response(StaffNotificationSerializer(notification).data)

    def delete(self, request, notification_id):
        notification = get_object_or_404(StaffNotification, id=notification_id)
        notification.delete()
        return Response({"deleted": True})


class StaffNotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def post(self, request):
        updated = StaffNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({"updated": updated, "unread_count": 0})


class InquiryCreateView(generics.CreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer


class SuccessStoryListView(generics.ListAPIView):
    serializer_class = SuccessStorySerializer

    def get_queryset(self):
        return SuccessStory.objects.filter(published=True, consent_confirmed=True)


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "globalpathways-django-api", "time": timezone.now()})
