import os
from types import SimpleNamespace
from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient
from opportunities.models import Application, ApplicationStatusEvent, Opportunity, PaymentRecord, SavedOpportunity, StaffNotification


class DashboardAndPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=SimpleNamespace(is_authenticated=True, open_id="test-user", app_id="test-app", name="Test User"))
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
        self.assertEqual(seeded.count(), 10)
        self.assertEqual(seeded.filter(region="Europe").count(), 5)
        self.assertEqual(seeded.filter(region="Asia").count(), 5)
        self.assertEqual(seeded.filter(category="scholarship").count(), 5)
        self.assertEqual(seeded.filter(category="visa").count(), 0)
        self.assertEqual(seeded.filter(category="job").count(), 5)
        self.assertEqual(seeded.filter(source_url__isnull=False).exclude(source_url="").count(), 10)
        self.assertEqual(seeded.filter(source_verified_at="2026-08-16").count(), 10)
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
