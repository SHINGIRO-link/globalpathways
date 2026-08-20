import os
import io
from pathlib import Path
import shutil
import tempfile
import zipfile
from types import SimpleNamespace
from unittest.mock import patch
from django.conf import settings
from django.core.management import call_command
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from opportunities.email_notifications import notify_application_status, notify_internal_payment_status, notify_internal_status
from opportunities.models import Application, ApplicationStatusEvent, GuestAccessToken, Opportunity, PaymentRecord, SavedOpportunity, StaffNotification
from opportunities.guest_access import create_guest_access


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class DashboardAndPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="test-user", app_id="test-app", name="Test User", email="amina@example.com"))
        self.opportunity = Opportunity.objects.create(
            title="Test Scholarship", slug="test-scholarship", category="scholarship", status="open",
            country="Netherlands", region="Europe", deadline="2026-10-28T23:59:00Z",
            summary="Test route", description="Test description", eligibility=["Degree"], required_documents=["Passport"],
        )

    def test_dashboard_requires_authenticated_session(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/dashboard/?email=amina@example.com", HTTP_X_DASHBOARD_EMAIL="amina@example.com")
        self.assertEqual(response.status_code, 401)

    def test_public_application_submission_creates_payment_and_notification(self):
        self.client.force_authenticate(user=None)
        payload = {
            "opportunity": self.opportunity.id, "full_name": "Public Applicant", "email": "public@example.com",
            "statement": "I want to study abroad.", "consent_to_contact": True, "document_links": [],
        }
        response = self.client.post("/api/applications/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        application = Application.objects.get(email="public@example.com")
        self.assertEqual(application.owner_open_id, "")
        self.assertTrue(PaymentRecord.objects.filter(application=application, amount=2000, currency="RWF", status="integration_pending").exists())
        self.assertTrue(StaffNotification.objects.filter(application=application, event_type="application_submitted").exists())

    def test_submission_sends_internal_and_consented_applicant_emails(self):
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/applications/", {"opportunity": self.opportunity.id, "full_name": "Email Applicant", "email": "email@example.com", "statement": "I want to study abroad.", "consent_to_contact": True, "document_links": []}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 3)
        self.assertIn("/guest/claim?token=", mail.outbox[2].body)
        self.assertIn("/guest/status?token=", mail.outbox[2].body)
        self.assertIn("No email verification is required", mail.outbox[2].body)
        recipients = {recipient for message in mail.outbox for recipient in message.to}
        self.assertEqual(recipients, {"globalopportunityconnect@gmail.com", "email@example.com"})

    def test_guest_access_links_status_and_claim_without_verification(self):
        application = Application.objects.create(opportunity=self.opportunity, full_name="Guest Applicant", email="guest@example.com", consent_to_contact=False, status="reviewing")
        access = create_guest_access(application)
        self.assertNotIn("verification_token", access)
        claim_token = access["claim_token"]
        status_response = self.client.get(f"/api/guest/status/?token={access['status_token']}")
        self.assertEqual(status_response.status_code, 200)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post("/api/guest/claim/", {"claim_token": claim_token}, format="json").status_code, 401)
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="claimed-user", app_id="test-app", name="Claimed User"))
        claim_response = self.client.post("/api/guest/claim/", {"claim_token": claim_token}, format="json")
        self.assertEqual(claim_response.status_code, 200)
        self.assertEqual(Application.objects.get(pk=application.pk).owner_open_id, "claimed-user")
        self.assertEqual(self.client.post("/api/guest/claim/", {"claim_token": claim_token}, format="json").status_code, 410)

    def test_internal_status_and_payment_emails_are_addressed_to_staff(self):
        application = Application.objects.create(opportunity=self.opportunity, full_name="Staff Update", email="staff-update@example.com", consent_to_contact=False, status="reviewing")
        self.assertTrue(notify_internal_status(application, "received"))
        self.assertTrue(notify_internal_payment_status(application, "integration_pending", "paid"))
        self.assertEqual([message.to for message in mail.outbox], [["globalopportunityconnect@gmail.com"], ["globalopportunityconnect@gmail.com"]])

    def test_status_email_requires_contact_consent(self):
        application = Application.objects.create(opportunity=self.opportunity, full_name="No Consent", email="no-consent@example.com", consent_to_contact=False, status="reviewing")
        self.assertFalse(notify_application_status(application))
        self.assertEqual(len(mail.outbox), 0)
        application.consent_to_contact = True
        self.assertTrue(notify_application_status(application))
        self.assertEqual(mail.outbox[0].to, ["no-consent@example.com"])

    def test_application_persists_server_issued_document_metadata(self):
        payload = {
            "opportunity": self.opportunity.id, "full_name": "Document Applicant", "email": "documents@example.com",
            "statement": "I want to study abroad.", "consent_to_contact": True,
            "documents": [{"name": "diploma.pdf", "content_type": "application/pdf", "size": 1200, "category": "certificate", "key": "education-documents/certificate/abc-diploma.pdf", "url": "/manus-storage/education-documents/certificate/abc-diploma.pdf"}],
        }
        response = self.client.post("/api/applications/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        application = Application.objects.get(email="documents@example.com")
        self.assertEqual(application.document_links, ["/manus-storage/education-documents/certificate/abc-diploma.pdf"])
        self.assertEqual(application.document_metadata[0]["content_type"], "application/pdf")

    def test_application_rejects_external_document_references(self):
        payload = {
            "opportunity": self.opportunity.id, "full_name": "Unsafe Applicant", "email": "unsafe@example.com",
            "statement": "I want to study abroad.", "consent_to_contact": True,
            "documents": [{"name": "diploma.pdf", "content_type": "application/pdf", "size": 1200, "key": "external/diploma.pdf", "url": "https://example.com/diploma.pdf"}],
        }
        response = self.client.post("/api/applications/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("secure document uploader", str(response.data))

    def test_application_creates_payment_required_state_and_dashboard_data(self):
        payload = {
            "opportunity": self.opportunity.id, "full_name": "Amina Test", "email": "amina@example.com",
            "statement": "I want to study abroad.", "consent_to_contact": True, "document_links": [],
        }
        response = self.client.post("/api/applications/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        application = Application.objects.get(email="amina@example.com")
        self.assertEqual(application.status, "payment_required")
        self.assertTrue(PaymentRecord.objects.filter(application=application, amount=2000, currency="RWF", status="integration_pending").exists())
        self.assertTrue(StaffNotification.objects.filter(application=application, event_type="application_submitted").exists())
        self.assertTrue(ApplicationStatusEvent.objects.filter(application=application, status="payment_required").exists())
        dashboard = self.client.get("/api/dashboard/?email=amina@example.com", HTTP_X_DASHBOARD_EMAIL="amina@example.com")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(len(dashboard.data["applications"]), 1)

    def test_dashboard_and_saved_reads_ignore_forged_identity_values(self):
        own = SavedOpportunity.objects.create(email="amina@example.com", owner_open_id="test-user", opportunity=self.opportunity)
        SavedOpportunity.objects.create(email="other@example.com", owner_open_id="other-user", opportunity=self.opportunity)
        dashboard = self.client.get("/api/dashboard/?email=other@example.com", HTTP_X_DASHBOARD_EMAIL="other@example.com")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.data["email"], "amina@example.com")
        saved = self.client.get("/api/saved-opportunities/?email=other@example.com", HTTP_X_DASHBOARD_EMAIL="other@example.com")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual([item["id"] for item in saved.data], [own.id])

    def test_saved_opportunity_and_provider_selection_are_recorded_without_live_charge(self):
        saved = self.client.post("/api/saved-opportunities/", {"email": "amina@example.com", "opportunity": self.opportunity.id}, HTTP_X_DASHBOARD_EMAIL="amina@example.com", format="json")
        self.assertEqual(saved.status_code, 201)
        self.assertTrue(SavedOpportunity.objects.filter(email="amina@example.com", opportunity=self.opportunity).exists())
        removed = self.client.delete(f"/api/saved-opportunities/{self.opportunity.id}/?email=amina@example.com", HTTP_X_DASHBOARD_EMAIL="amina@example.com")
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(removed.data["deleted"], True)
        self.assertFalse(SavedOpportunity.objects.filter(email="amina@example.com", opportunity=self.opportunity).exists())
        application = Application.objects.create(opportunity=self.opportunity, owner_open_id="test-user", full_name="Amina Test", email="amina@example.com", consent_to_contact=True)
        PaymentRecord.objects.create(application=application, amount=2000, currency="RWF", status="integration_pending")
        payment = self.client.post("/api/payments/prepare/", {"email": "amina@example.com", "application": application.id, "provider": "momo"}, HTTP_X_DASHBOARD_EMAIL="amina@example.com", format="json")
        self.assertEqual(payment.status_code, 202)
        self.assertEqual(payment.data["payment"]["provider"], "momo")
        self.assertEqual(payment.data["payment"]["status"], "integration_pending")
        self.assertTrue(StaffNotification.objects.filter(application=application, event_type="payment_status").exists())

    def test_later_payment_status_change_creates_staff_notification(self):
        application = Application.objects.create(opportunity=self.opportunity, owner_open_id="test-user", full_name="Amina Test", email="amina@example.com", consent_to_contact=True)
        payment = PaymentRecord.objects.create(application=application, amount=2000, currency="RWF", status="integration_pending")
        payment.status = "paid"
        payment.save()
        self.assertTrue(StaffNotification.objects.filter(application=application, event_type="payment_status", message__icontains="paid").exists())

    def test_expanded_seed_catalog_covers_europe_and_asia(self):
        call_command("seed_opportunities")
        seeded = Opportunity.objects.exclude(slug="test-scholarship")
        self.assertEqual(seeded.count(), 30)
        self.assertEqual(seeded.filter(region="Europe").count(), 13)
        self.assertEqual(seeded.filter(region="Asia").count(), 17)
        self.assertEqual(seeded.filter(category="scholarship").count(), 23)
        self.assertEqual(seeded.filter(category="visa").count(), 0)
        self.assertEqual(seeded.filter(category="job").count(), 7)
        self.assertEqual(seeded.filter(source_url__isnull=False).exclude(source_url="").count(), 30)
        self.assertEqual(seeded.filter(source_verified_at="2026-08-16").count(), 30)
        chevening = seeded.get(title="Chevening Scholarship — 2027–2028")
        self.assertEqual(chevening.deadline.isoformat(), "2026-10-06T11:00:00+00:00")
        self.assertIn("Official deadline", chevening.deadline_note)
        un_role = seeded.get(title="UN Human Rights Representative — P-5")
        self.assertEqual(un_role.status, "open")
        self.assertEqual(un_role.source_name, "UN Careers")
        self.assertEqual(un_role.source_url, "https://careers.un.org/jobSearchDescription/281339")
        self.assertEqual(un_role.deadline.isoformat(), "2026-09-10T23:59:00+00:00")
        mext = seeded.get(title="MEXT Japanese Government Scholarship")
        self.assertEqual(mext.source_url, "https://www.studyinjapan.go.jp/en/planning/scholarships/mext-scholarships/")
        self.assertEqual(mext.source_verified_at.isoformat(), "2026-08-16")
        self.assertIn("varies", mext.deadline_note)
        eures = seeded.get(title="EURES Europe Job Search")
        self.assertEqual(eures.source_url, "https://eures.europa.eu/index_en")
        self.assertEqual(eures.source_verified_at.isoformat(), "2026-08-16")
        self.assertIn("Dynamic portal", eures.deadline_note)
        eiffel = seeded.get(slug="france-excellence-eiffel-scholarship")
        self.assertEqual(eiffel.source_url, "https://www.campusfrance.org/en/france-excellence-eiffel-scholarship-program")
        self.assertIn("Annual call", eiffel.deadline_note)
        gks = seeded.get(slug="global-korea-scholarship")
        self.assertEqual(gks.source_url, "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do")
        self.assertEqual(gks.region, "Asia")

    def test_staff_notification_center_filters_and_manages_alerts(self):
        StaffNotification.objects.create(event_type="application_submitted", title="New application", message="Application received.", is_read=False)
        StaffNotification.objects.create(event_type="payment_status", title="Payment update", message="Payment marked paid.", is_read=True)
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "test-user"}):
            unread = self.client.get("/api/staff/notifications/?read=unread")
            self.assertEqual(unread.status_code, 200)
            self.assertEqual(unread.data["unread_count"], 1)
            self.assertEqual(len(unread.data["notifications"]), 1)
            notification_id = unread.data["notifications"][0]["id"]
            marked = self.client.patch(f"/api/staff/notifications/{notification_id}/", {"is_read": True}, format="json")
            self.assertEqual(marked.status_code, 200)
            bulk = self.client.post("/api/staff/notifications/mark-all-read/")
            self.assertEqual(bulk.status_code, 200)
            archived = self.client.delete(f"/api/staff/notifications/{notification_id}/")
            self.assertEqual(archived.status_code, 200)

    def test_application_status_endpoint_returns_history_and_payment(self):
        application = Application.objects.create(opportunity=self.opportunity, owner_open_id="test-user", full_name="Amina Test", email="amina@example.com", consent_to_contact=True, status="reviewing")
        ApplicationStatusEvent.objects.create(application=application, status="payment_required", note="Submitted")
        ApplicationStatusEvent.objects.create(application=application, status="reviewing", note="Advisor review started")
        PaymentRecord.objects.create(application=application, amount=2000, currency="RWF", status="integration_pending")
        response = self.client.get(f"/api/applications/{application.id}/status/?email=amina@example.com", HTTP_X_DASHBOARD_EMAIL="amina@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["application"]["status"], "reviewing")
        self.assertEqual(len(response.data["events"]), 2)
        self.assertEqual(response.data["payment"]["status"], "integration_pending")


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StaffApplicationsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = SimpleNamespace(is_authenticated=True, open_id="staff-user", app_id="test-app", name="Staff User")
        self.client.force_authenticate(user=self.staff)
        self.opportunity = Opportunity.objects.create(
            title="Staff Review Route", slug="staff-review-route", category="scholarship", status="open",
            country="Germany", region="Europe", deadline="2026-12-01T23:59:00Z",
            summary="Staff route", description="Staff description", eligibility=["Degree"], required_documents=["Passport"],
        )
        self.application = Application.objects.create(
            opportunity=self.opportunity, full_name="Review Applicant", email="review@example.com",
            consent_to_contact=True, status="received", document_metadata=[{
                "name": "passport.pdf", "content_type": "application/pdf", "size": 2048,
                "category": "passport", "key": "education-documents/passport/review.pdf",
                "url": "/manus-storage/education-documents/passport/review.pdf",
            }],
        )
        self.payment = PaymentRecord.objects.create(application=self.application, amount=2000, currency="RWF", status="integration_pending")

    def test_staff_application_list_requires_owner_staff_session(self):
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "staff-user"}):
            response = self.client.get("/api/staff/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["applications"][0]["full_name"], "Review Applicant")
        self.assertEqual(response.data["applications"][0]["documents"][0]["download_url"], f"/api/staff/applications/{self.application.id}/documents/0/download/")
        self.assertEqual(response.data["summary"]["pending_payments"], 1)

    def test_staff_can_search_applications_by_name_or_email(self):
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "staff-user"}):
            by_name = self.client.get("/api/staff/applications/?q=Review%20Applicant")
            by_email = self.client.get("/api/staff/applications/?q=review@example.com")
        self.assertEqual([item["id"] for item in by_name.data["applications"]], [self.application.id])
        self.assertEqual([item["id"] for item in by_email.data["applications"]], [self.application.id])

    def test_non_staff_cannot_review_or_export_applications(self):
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "another-user"}):
            self.assertEqual(self.client.get("/api/staff/applications/").status_code, 403)
            self.assertEqual(self.client.get("/api/staff/applications/export/").status_code, 403)

    def test_staff_can_change_application_and_payment_statuses(self):
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "staff-user"}):
            application_response = self.client.patch(f"/api/staff/applications/{self.application.id}/status/", {"status": "reviewing", "note": "Initial review"}, format="json")
            payment_response = self.client.patch(f"/api/staff/payments/{self.payment.id}/status/", {"status": "paid", "provider_reference": "PAY-123"}, format="json")
        self.assertEqual(application_response.status_code, 200)
        self.assertEqual(application_response.data["status"], "reviewing")
        self.assertEqual(payment_response.status_code, 200)
        self.assertEqual(payment_response.data["payment"]["status"], "paid")
        self.assertTrue(ApplicationStatusEvent.objects.filter(application=self.application, status="reviewing", note="Initial review").exists())
        self.assertTrue(StaffNotification.objects.filter(application=self.application, event_type="application_status").exists())
        self.assertEqual(PaymentRecord.objects.get(pk=self.payment.pk).provider_reference, "PAY-123")

    def test_staff_export_is_csv_and_document_download_is_staff_gated(self):
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "staff-user"}):
            export = self.client.get("/api/staff/applications/export/")
            document = self.client.get(f"/api/staff/applications/{self.application.id}/documents/0/download/")
        self.assertEqual(export.status_code, 200)
        self.assertIn("text/csv", export["Content-Type"])
        self.assertIn("Review Applicant", export.content.decode())
        self.assertEqual(document.status_code, 302)
        self.assertIn("education-documents/passport/review.pdf", document["Location"])


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StaffDocumentsZipTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="zip-staff", app_id="test-app", name="ZIP Staff", role="staff"))
        opportunity = Opportunity.objects.create(
            title="ZIP Route", slug="zip-route", category="scholarship", status="open",
            country="Japan", region="Asia", deadline="2026-12-01T23:59:00Z",
            summary="ZIP route", description="ZIP description", eligibility=["Degree"], required_documents=["Passport"],
        )
        self.zip_document = Path(settings.MEDIA_ROOT) / "education-documents/passport/zip.pdf"
        self.zip_document.parent.mkdir(parents=True, exist_ok=True)
        self.zip_document.write_bytes(b"fake-pdf-bytes")
        Application.objects.create(
            opportunity=opportunity, full_name="Asha / Review", email="zip@example.com", consent_to_contact=True,
            document_metadata=[{
                "name": "passport copy.pdf", "content_type": "application/pdf", "size": 11,
                "category": "passport", "key": "education-documents/passport/zip.pdf",
                "url": "/manus-storage/education-documents/passport/zip.pdf",
            }],
        )

    def test_staff_zip_contains_document_and_manifest(self):
        class FakeStorageResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, _limit): return b"fake-pdf-bytes"

        with patch.dict(os.environ, {"OWNER_OPEN_ID": "zip-staff"}), patch("opportunities.staff_views.urllib.request.urlopen", return_value=FakeStorageResponse()):
            response = self.client.get("/api/staff/applications/documents/export/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            names = archive.namelist()
            self.assertIn("MANIFEST.tsv", names)
            document_names = [name for name in names if name != "MANIFEST.tsv"]
            self.assertEqual(len(document_names), 1)
            self.assertNotIn("/", document_names[0].split("applications/", 1)[-1].split("/", 1)[0])
            self.assertEqual(archive.read(document_names[0]), b"fake-pdf-bytes")
            self.assertIn("zip@example.com", archive.read("MANIFEST.tsv").decode())

    def test_zip_filters_by_status_and_created_date(self):
        class FakeStorageResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, _limit): return b"filtered-pdf"

        with patch.dict(os.environ, {"OWNER_OPEN_ID": "zip-staff"}), patch("opportunities.staff_views.urllib.request.urlopen", return_value=FakeStorageResponse()):
            included = self.client.get("/api/staff/applications/documents/export/?status=payment_required&date_from=2020-01-01&date_to=2030-01-01")
            excluded = self.client.get("/api/staff/applications/documents/export/?status=approved")
            invalid = self.client.get("/api/staff/applications/documents/export/?date_from=not-a-date")
        self.assertEqual(included.status_code, 200)
        self.assertEqual(excluded.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(included.content)) as archive:
            self.assertEqual(len([name for name in archive.namelist() if name != "MANIFEST.tsv"]), 1)
        with zipfile.ZipFile(io.BytesIO(excluded.content)) as archive:
            self.assertEqual([name for name in archive.namelist() if name != "MANIFEST.tsv"], [])
        self.assertEqual(invalid.status_code, 400)

    def test_non_staff_cannot_download_all_documents(self):
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="applicant-user", app_id="test-app", name="Applicant", role="user"))
        with patch.dict(os.environ, {"OWNER_OPEN_ID": "different-staff"}):
            response = self.client.get("/api/staff/applications/documents/export/")
        self.assertEqual(response.status_code, 403)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EducationDocumentUploadTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="globalpathways-test-media-")
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.client = APIClient()
        self.opportunity = Opportunity.objects.create(
            title="Upload Route", slug="upload-route", category="scholarship", status="open",
            country="Rwanda", region="Africa", deadline="2026-12-31T23:59:00Z",
            summary="Upload route", description="Upload route", eligibility=["Degree"], required_documents=["Certificate"],
        )

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_upload_returns_server_issued_metadata_and_persists_file(self):
        response = self.client.post(
            "/api/uploads/education-document",
            {"category": "certificate", "file": SimpleUploadedFile("diploma.pdf", b"%PDF-1.7\nreal-bytes", content_type="application/pdf")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["key"].startswith("education-documents/certificate/"))
        self.assertEqual(response.data["url"], f"/manus-storage/{response.data['key']}")
        self.assertTrue((self.media_root + "/" + response.data["key"]).endswith("diploma.pdf"))
        self.assertTrue((__import__("pathlib").Path(self.media_root) / response.data["key"]).is_file())

    def test_upload_rejects_mismatched_signature_and_oversized_file(self):
        mismatched = self.client.post(
            "/api/uploads/education-document",
            {"category": "certificate", "file": SimpleUploadedFile("fake.pdf", b"not-a-pdf", content_type="application/pdf")},
            format="multipart",
        )
        self.assertEqual(mismatched.status_code, 400)
        oversized = self.client.post(
            "/api/uploads/education-document",
            {"category": "certificate", "file": SimpleUploadedFile("large.pdf", b"%PDF-" + b"x" * (10 * 1024 * 1024), content_type="application/pdf")},
            format="multipart",
        )
        self.assertEqual(oversized.status_code, 400)

    def test_uploaded_metadata_can_be_attached_and_staff_file_is_protected(self):
        upload = self.client.post(
            "/api/uploads/education-document",
            {"category": "certificate", "file": SimpleUploadedFile("certificate.pdf", b"%PDF-1.7\nbytes", content_type="application/pdf")},
            format="multipart",
        )
        metadata = upload.data
        application = self.client.post(
            "/api/applications/",
            {"opportunity": self.opportunity.id, "full_name": "Attachment Applicant", "email": "attachment@example.com", "statement": "I want to study abroad.", "consent_to_contact": True, "documents": [metadata]},
            format="json",
        )
        self.assertEqual(application.status_code, 201)
        stored = Application.objects.get(email="attachment@example.com")
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(metadata["url"]).status_code, {401, 403})
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="staff-upload", app_id="test-app", name="Staff", role="staff"))
        self.assertEqual(self.client.get(metadata["url"]).status_code, 200)
        self.assertEqual(self.client.get(f"/api/staff/applications/{stored.id}/documents/0/download/").status_code, 302)
