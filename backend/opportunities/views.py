from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application, ApplicationStatusEvent, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, SuccessStory
from .serializers import ApplicationSerializer, ApplicationStatusEventSerializer, InquirySerializer, OpportunitySerializer, PaymentRecordSerializer, SavedOpportunitySerializer, SuccessStorySerializer


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
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        application = serializer.save(status="payment_required", owner_open_id=self.request.user.open_id)
        ApplicationStatusEvent.objects.create(application=application, status="payment_required", note="Application submitted. Payment integration will be enabled here.")
        PaymentRecord.objects.create(application=application, amount=2000, currency="TBD", status="integration_pending")


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
        payment, _ = PaymentRecord.objects.get_or_create(application=application, defaults={"amount": 2000, "currency": "TBD"})
        payment.provider = provider
        payment.status = "integration_pending"
        payment.save(update_fields=["provider", "status", "updated_at"])
        return Response({"payment": PaymentRecordSerializer(payment).data, "message": "Provider integration is not enabled yet. Your application remains safely recorded and payment can be completed when the service is connected."}, status=status.HTTP_202_ACCEPTED)


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
