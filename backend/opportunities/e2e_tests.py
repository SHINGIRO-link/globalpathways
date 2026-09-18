import json
import unittest
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import Application, Opportunity, PaymentRecord


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", RESEND_API_KEY="")
class RegistrationPaymentE2ETests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.opportunity = Opportunity.objects.create(
            title="E2E Scholarship",
            slug="e2e-scholarship",
            category="scholarship",
            status="open",
            country="Rwanda",
            region="Africa",
            deadline="2026-12-31T23:59:00Z",
            summary="E2E test opportunity",
            description="E2E test opportunity",
            eligibility=["Degree"],
            required_documents=["Passport"],
        )

    @patch.dict("os.environ", {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/api/payments/intouchpay/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_registration_application_request_payment_and_callback(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.side_effect = [
            json.dumps({"success": True, "status": "Pending", "responsecode": "1000"}).encode(),
        ]
        registered = self.client.post("/api/auth/register/", {"email": "e2e@example.com", "password": "SafePassword123!"}, format="json")
        self.assertEqual(registered.status_code, 201)
        self.assertEqual(self.client.get("/api/auth/me/").data["user"]["email"], "e2e@example.com")

        application = self.client.post("/api/applications/", {
            "opportunity": self.opportunity.id,
            "full_name": "E2E Applicant",
            "email": "e2e@example.com",
            "statement": "E2E test application.",
            "consent_to_contact": True,
            "document_links": [],
        }, format="json")
        self.assertEqual(application.status_code, 201)
        application_id = application.data["id"]
        payment = self.client.post("/api/payments/prepare/", {
            "application": application_id,
            "provider": "intouchpay",
            "mobile_phone": "250788888888",
            "email": "e2e@example.com",
        }, format="json")
        self.assertEqual(payment.status_code, 202)
        self.assertEqual(payment.data["payment"]["status"], "pending")
        request_id = payment.data["payment"]["provider_reference"]

        callback = self.client.post("/api/payments/intouchpay/callback/", {
            "jsonpayload": {
                "requesttransactionid": request_id,
                "transactionid": "E2E-TX-1",
                "status": "Successful",
                "responsecode": "01",
            }
        }, format="json")
        self.assertEqual(callback.status_code, 200)
        self.assertEqual(PaymentRecord.objects.get(application_id=application_id).status, "paid")
        self.assertEqual(Application.objects.get(pk=application_id).status, "received")
        self.assertTrue(mail.outbox)
