import json
import unittest
from unittest.mock import patch

from django.test import override_settings

from .email_notifications import _send


class ResendEmailTests(unittest.TestCase):
    @override_settings(
        RESEND_API_KEY="re_test_key",
        RESEND_FROM_EMAIL="noreply@example.com",
    )
    @patch("opportunities.email_notifications.urlopen")
    def test_send_uses_resend_api_when_configured(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.status = 200
        self.assertTrue(_send("Subject", "Body", "person@example.com"))
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.resend.com/emails")
        self.assertEqual(request.get_header("Authorization"), "Bearer re_test_key")
        payload = json.loads(request.data.decode())
        self.assertEqual(payload["from"], "noreply@example.com")
        self.assertEqual(payload["to"], ["person@example.com"])
        self.assertEqual(payload["subject"], "Subject")
        self.assertEqual(payload["text"], "Body")
