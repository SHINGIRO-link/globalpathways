import hashlib
import json
import os
import unittest
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from unittest.mock import patch

from .intouchpay import IntouchPayClient, IntouchPayError, callback_payload, is_successful_status


class IntouchPayClientTests(unittest.TestCase):
    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/api/payments/intouchpay/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_request_payment_uses_sha256_credentials_and_expected_fields(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({"success": True, "status": "Pending", "responsecode": "1000"}).encode()
        result = IntouchPayClient().request_payment(amount=2000, mobile_phone="250788888888", request_transaction_id="GP-1-test")
        self.assertTrue(result["success"])
        request = mock_urlopen.call_args.args[0]
        payload = parse_qs(request.data.decode())
        expected = hashlib.sha256(f"sandbox-usersandbox-accountsandbox-password{payload['timestamp'][0]}".encode()).hexdigest()
        self.assertEqual(request.get_header("Content-type"), "application/x-www-form-urlencoded")
        self.assertEqual(payload["password"][0], expected)
        self.assertEqual(payload["mobilephone"][0], "250788888888")
        self.assertEqual(payload["accountno"][0], "sandbox-account")
        self.assertEqual(payload["callbackurl"][0], "https://example.com/api/payments/intouchpay/callback/")

    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_http_error_exposes_only_status_and_safe_response_code(self, mock_urlopen):
        secret_like_body = b'{"responsecode":"1100","message":"private account detail"}'
        mock_urlopen.side_effect = HTTPError(
            "https://provider.example/requestpayment/",
            401,
            "Unauthorized",
            hdrs=None,
            fp=BytesIO(secret_like_body),
        )

        with self.assertLogs("opportunities.intouchpay", level="ERROR") as logs:
            with self.assertRaises(IntouchPayError) as raised:
                IntouchPayClient().request_payment(
                    amount=2000,
                    mobile_phone="250788888888",
                    request_transaction_id="GP-http-error",
                )

        error = raised.exception
        self.assertEqual(error.category, "upstream_http")
        self.assertEqual(error.http_status, 401)
        self.assertEqual(error.provider_code, "1100")
        self.assertIn("HTTP 401", str(error))
        self.assertIn("1100", str(error))
        self.assertNotIn("private account detail", str(error))
        self.assertNotIn("private account detail", " ".join(logs.output))

    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_business_failure_response_maps_safe_code_without_raw_message(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({
            "success": False,
            "responsecode": "0005",
            "message": "private provider account details",
        }).encode()

        with self.assertLogs("opportunities.intouchpay", level="ERROR") as logs:
            with self.assertRaises(IntouchPayError) as raised:
                IntouchPayClient().request_payment(
                    amount=2000,
                    mobile_phone="250788888888",
                    request_transaction_id="GP-business-error",
                )

        self.assertEqual(raised.exception.category, "provider_rejected")
        self.assertEqual(raised.exception.provider_code, "0005")
        self.assertIn("rejected its credentials", str(raised.exception))
        self.assertNotIn("private provider account details", str(raised.exception))
        self.assertNotIn("private provider account details", " ".join(logs.output))

    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_network_error_reports_safe_category_not_raw_reason(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("sensitive-provider-internal-detail")

        with self.assertLogs("opportunities.intouchpay", level="ERROR") as logs:
            with self.assertRaises(IntouchPayError) as raised:
                IntouchPayClient().request_payment(
                    amount=2000,
                    mobile_phone="250788888888",
                    request_transaction_id="GP-network-error",
                )

        self.assertEqual(raised.exception.category, "transport")
        self.assertNotIn("sensitive-provider-internal-detail", str(raised.exception))
        self.assertNotIn("sensitive-provider-internal-detail", " ".join(logs.output))

    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "https://example.com/callback/",
    }, clear=False)
    @patch("opportunities.intouchpay.urlopen")
    def test_unreadable_success_response_is_classified_safely(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b"not-json"

        with self.assertLogs("opportunities.intouchpay", level="ERROR") as logs:
            with self.assertRaises(IntouchPayError) as raised:
                IntouchPayClient().request_payment(
                    amount=2000,
                    mobile_phone="250788888888",
                    request_transaction_id="GP-invalid-json",
                )

        self.assertEqual(raised.exception.category, "invalid_response")
        self.assertNotIn("not-json", " ".join(logs.output))

    def test_callback_and_success_helpers(self):
        payload = {"jsonpayload": {"requesttransactionid": "GP-1-test", "responsecode": "01", "status": "Successful"}}
        self.assertEqual(callback_payload(payload)["requesttransactionid"], "GP-1-test")
        self.assertTrue(is_successful_status(callback_payload(payload)))

    @patch.dict(os.environ, {
        "INTOUCHPAY_USERNAME": "sandbox-user",
        "INTOUCHPAY_ACCOUNT_NUMBER": "sandbox-account",
        "INTOUCHPAY_PARTNER_PASSWORD": "sandbox-password",
        "INTOUCHPAY_CALLBACK_URL": "",
    }, clear=False)
    def test_request_payment_requires_callback_url(self):
        with self.assertRaisesRegex(IntouchPayError, "callback URL"):
            IntouchPayClient().request_payment(amount=2000, mobile_phone="250788888888", request_transaction_id="GP-2-test")
