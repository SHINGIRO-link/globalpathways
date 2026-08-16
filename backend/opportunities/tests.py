from types import SimpleNamespace
from django.test import TestCase
from rest_framework.test import APIClient
from opportunities.models import Application, ApplicationStatusEvent, Opportunity, PaymentRecord, SavedOpportunity


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

    def test_application_creates_payment_required_state_and_dashboard_data(self):
        payload = {
            "opportunity": self.opportunity.id, "full_name": "Amina Test", "email": "amina@example.com",
            "statement": "I want to study abroad.", "consent_to_contact": True, "document_links": [],
        }
        response = self.client.post("/api/applications/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        application = Application.objects.get(email="amina@example.com")
        self.assertEqual(application.status, "payment_required")
        self.assertTrue(PaymentRecord.objects.filter(application=application, amount=2000, status="integration_pending").exists())
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
        PaymentRecord.objects.create(application=application, amount=2000, currency="TBD", status="integration_pending")
        payment = self.client.post("/api/payments/prepare/", {"email": "amina@example.com", "application": application.id, "provider": "momo"}, HTTP_X_DASHBOARD_EMAIL="amina@example.com", format="json")
        self.assertEqual(payment.status_code, 202)
        self.assertEqual(payment.data["payment"]["provider"], "momo")
        self.assertEqual(payment.data["payment"]["status"], "integration_pending")

    def test_application_status_endpoint_returns_history_and_payment(self):
        application = Application.objects.create(opportunity=self.opportunity, owner_open_id="test-user", full_name="Amina Test", email="amina@example.com", consent_to_contact=True, status="reviewing")
        ApplicationStatusEvent.objects.create(application=application, status="payment_required", note="Submitted")
        ApplicationStatusEvent.objects.create(application=application, status="reviewing", note="Advisor review started")
        PaymentRecord.objects.create(application=application, amount=2000, currency="TBD", status="integration_pending")
        response = self.client.get(f"/api/applications/{application.id}/status/?email=amina@example.com", HTTP_X_DASHBOARD_EMAIL="amina@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["application"]["status"], "reviewing")
        self.assertEqual(len(response.data["events"]), 2)
        self.assertEqual(response.data["payment"]["status"], "integration_pending")
