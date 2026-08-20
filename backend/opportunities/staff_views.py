import csv
import io
import re
import urllib.request
import zipfile
from datetime import date
from urllib.parse import quote

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IsStaffUser
from .documents import local_document_path
from .email_notifications import notify_application_status, notify_internal_status
from .models import Application, ApplicationStatusEvent, PaymentRecord, StaffNotification
from .serializers import ApplicationSerializer, PaymentRecordSerializer


class StaffOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]


def application_row(application):
    payment = getattr(application, "payment", None)
    documents = application.document_metadata or []
    return {
        "id": application.id,
        "full_name": application.full_name,
        "email": application.email,
        "phone": application.phone,
        "nationality": application.nationality,
        "current_location": application.current_location,
        "education_level": application.education_level,
        "statement": application.statement,
        "opportunity": application.opportunity_id,
        "opportunity_title": application.opportunity.title,
        "status": application.status,
        "status_label": application.get_status_display(),
        "consent_to_contact": application.consent_to_contact,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
        "documents": [
            {
                "index": index,
                "name": document.get("name", "Document"),
                "category": document.get("category", "supporting"),
                "content_type": document.get("content_type", "application/octet-stream"),
                "size": document.get("size", 0),
                "download_url": f"/api/staff/applications/{application.id}/documents/{index}/download/",
            }
            for index, document in enumerate(documents)
        ],
        "payment": PaymentRecordSerializer(payment).data if payment else None,
    }


class StaffApplicationListView(StaffOnlyView):
    def get(self, request):
        queryset = Application.objects.select_related("opportunity", "payment").all()
        search = request.query_params.get("q", "").strip()
        application_status = request.query_params.get("status", "").strip()
        payment_status = request.query_params.get("payment_status", "").strip()
        if search:
            queryset = queryset.filter(full_name__icontains=search) | queryset.filter(email__icontains=search) | queryset.filter(opportunity__title__icontains=search)
        if application_status in dict(Application.STATUS_CHOICES):
            queryset = queryset.filter(status=application_status)
        if payment_status in dict(PaymentRecord.STATUS_CHOICES):
            queryset = queryset.filter(payment__status=payment_status)
        queryset = queryset.order_by("-created_at")
        applications = list(queryset[:250])
        counts = {
            "applications": Application.objects.count(),
            "payments": PaymentRecord.objects.count(),
            "pending_payments": PaymentRecord.objects.filter(status__in=["pending", "integration_pending"]).count(),
            "unread_notifications": StaffNotification.objects.filter(is_read=False).count(),
        }
        return Response({
            "summary": counts,
            "applications": [application_row(application) for application in applications],
            "statuses": [{"value": value, "label": label} for value, label in Application.STATUS_CHOICES],
            "payment_statuses": [{"value": value, "label": label} for value, label in PaymentRecord.STATUS_CHOICES],
        })


class StaffApplicationStatusView(StaffOnlyView):
    class InputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)
        note = serializers.CharField(required=False, allow_blank=True, max_length=240)

    def patch(self, request, application_id):
        application = get_object_or_404(Application.objects.select_related("opportunity"), id=application_id)
        payload = self.InputSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        next_status = payload.validated_data["status"]
        note = payload.validated_data.get("note", "")
        previous_status = application.status
        if previous_status != next_status:
            application.status = next_status
            application.save(update_fields=["status", "updated_at"])
            ApplicationStatusEvent.objects.create(application=application, status=next_status, note=note)
            StaffNotification.objects.create(
                event_type="application_status",
                title="Application status changed",
                message=f"{application.full_name}'s application moved from {previous_status.replace('_', ' ')} to {next_status.replace('_', ' ')}.",
                application=application,
            )
            notify_internal_status(application, previous_status)
            notify_application_status(application)
        return Response(application_row(application), status=status.HTTP_200_OK)


class StaffPaymentStatusView(StaffOnlyView):
    class InputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=PaymentRecord.STATUS_CHOICES)
        provider_reference = serializers.CharField(required=False, allow_blank=True, max_length=160)

    def patch(self, request, payment_id):
        payment = get_object_or_404(PaymentRecord.objects.select_related("application", "application__opportunity"), id=payment_id)
        payload = self.InputSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        updates = {"status": payload.validated_data["status"]}
        if "provider_reference" in payload.validated_data:
            updates["provider_reference"] = payload.validated_data["provider_reference"]
        payment.status = updates["status"]
        payment.provider_reference = updates.get("provider_reference", payment.provider_reference)
        payment.save(update_fields=["status", "provider_reference", "updated_at"])
        return Response(application_row(payment.application), status=status.HTTP_200_OK)


class StaffApplicationsExportView(StaffOnlyView):
    def get(self, request):
        queryset = Application.objects.select_related("opportunity", "payment").order_by("-created_at")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="globalpathways-applications.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "Applicant", "Email", "Phone", "Nationality", "Opportunity", "Application status", "Payment status", "Provider", "Amount", "Currency", "Documents", "Created", "Updated"])
        for application in queryset:
            payment = getattr(application, "payment", None)
            writer.writerow([
                application.id,
                application.full_name,
                application.email,
                application.phone,
                application.nationality,
                application.opportunity.title,
                application.get_status_display(),
                payment.get_status_display() if payment else "No payment record",
                payment.get_provider_display() if payment and payment.provider else "",
                payment.amount if payment else "",
                payment.currency if payment else "",
                len(application.document_metadata or []),
                application.created_at.isoformat(),
                application.updated_at.isoformat(),
            ])
        return response


class StaffAllDocumentsZipView(StaffOnlyView):
    MAX_ARCHIVE_BYTES = 100 * 1024 * 1024

    @staticmethod
    def safe_name(value):
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "document"))
        return cleaned.strip("._")[:100] or "document"

    def get(self, request):
        applications = Application.objects.select_related("opportunity").order_by("id")
        application_status = request.query_params.get("status", "").strip()
        date_from = request.query_params.get("date_from", "").strip()
        date_to = request.query_params.get("date_to", "").strip()
        if application_status and application_status not in dict(Application.STATUS_CHOICES):
            return Response({"detail": "Invalid application status filter."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if date_from:
                applications = applications.filter(created_at__date__gte=date.fromisoformat(date_from))
            if date_to:
                applications = applications.filter(created_at__date__lte=date.fromisoformat(date_to))
        except ValueError:
            return Response({"detail": "Dates must use YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)
        if date_from and date_to and date_from > date_to:
            return Response({"detail": "The start date must be before or equal to the end date."}, status=status.HTTP_400_BAD_REQUEST)
        if application_status:
            applications = applications.filter(status=application_status)
        archive_buffer = io.BytesIO()
        manifest = []
        total_bytes = 0
        with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for application in applications:
                applicant = self.safe_name(application.full_name)
                opportunity = self.safe_name(application.opportunity.title)
                for index, document in enumerate(application.document_metadata or []):
                    key = document.get("key", "")
                    source_url = document.get("url", "")
                    if not key.startswith("education-documents/") or not source_url.startswith("/manus-storage/"):
                        continue
                    target = local_document_path(key)
                    if target is None or not target.is_file():
                        continue
                    try:
                        with target.open("rb") as source:
                            contents = source.read(self.MAX_ARCHIVE_BYTES - total_bytes + 1)
                    except OSError:
                        continue
                    if total_bytes + len(contents) > self.MAX_ARCHIVE_BYTES:
                        break
                    filename = self.safe_name(document.get("name", f"document-{index + 1}"))
                    archive_path = f"applications/{application.id}-{applicant}/{opportunity}/{index + 1}-{filename}"
                    archive.writestr(archive_path, contents)
                    total_bytes += len(contents)
                    manifest.append(f"{archive_path}\t{application.email}\t{document.get('category', 'supporting')}\n")
            archive.writestr("MANIFEST.tsv", "Archive path\tApplicant email\tCategory\n" + "".join(manifest))
        response = HttpResponse(archive_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="globalpathways-application-documents.zip"'
        return response


class StaffApplicationDocumentDownloadView(StaffOnlyView):
    def get(self, request, application_id, document_index):
        application = get_object_or_404(Application, id=application_id)
        documents = application.document_metadata or []
        if document_index < 0 or document_index >= len(documents):
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        document = documents[document_index]
        key = document.get("key", "")
        if not key.startswith("education-documents/"):
            return Response({"detail": "Document reference is invalid."}, status=status.HTTP_404_NOT_FOUND)
        target = request.build_absolute_uri(f"/manus-storage/{quote(key)}")
        return HttpResponseRedirect(target)
