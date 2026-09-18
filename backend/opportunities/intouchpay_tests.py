import hashlib
import json
import os
import unittest
from unittest.mock import patch

from .intouchpay import IntouchPayClient, callback_payload, is_successful_status


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
        payload = json.loads(request.data.decode())
        expected = hashlib.sha256(f"sandbox-usersandbox-accountsandbox-password{payload['timestamp']}".encode()).hexdigest()
        self.assertEqual(payload["password"], expected)
        self.assertEqual(payload["mobilephone"], "250788888888")
        self.assertEqual(payload["accountno"], "sandbox-account")
        self.assertEqual(payload["callbackurl"], "https://example.com/api/payments/intouchpay/callback/")

    def test_callback_and_success_helpers(self):
        payload = {"jsonpayload": {"requesttransactionid": "GP-1-test", "responsecode": "01", "status": "Successful"}}
        self.assertEqual(callback_payload(payload)["requesttransactionid"], "GP-1-test")
        self.assertTrue(is_successful_status(callback_payload(payload)))
