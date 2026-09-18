import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class IntouchPayError(Exception):
    """Raised when the IntouchPay sandbox request cannot be completed."""


class IntouchPayClient:
    def __init__(self):
        self.base_url = os.getenv("INTOUCHPAY_BASE_URL", "https://developer.intouchpay.co.rw/api/v1/sandbox").rstrip("/")
        self.username = os.getenv("INTOUCHPAY_USERNAME", "").strip()
        self.account_number = os.getenv("INTOUCHPAY_ACCOUNT_NUMBER", "").strip()
        self.partner_password = os.getenv("INTOUCHPAY_PARTNER_PASSWORD", "")
        self.callback_url = os.getenv("INTOUCHPAY_CALLBACK_URL", "").strip()
        self.timeout = int(os.getenv("INTOUCHPAY_TIMEOUT_SECONDS", "30"))

    @property
    def configured(self):
        return bool(self.username and self.account_number and self.partner_password)

    def _credentials(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        password_hash = hashlib.sha256(
            f"{self.username}{self.account_number}{self.partner_password}{timestamp}".encode("utf-8")
        ).hexdigest()
        return timestamp, password_hash

    def request_payment(self, *, amount: int, mobile_phone: str, request_transaction_id: str):
        if not self.configured:
            raise IntouchPayError("IntouchPay sandbox credentials are not configured.")
        if not self.callback_url:
            raise IntouchPayError("IntouchPay callback URL is not configured.")
        timestamp, password_hash = self._credentials()
        body = {
            "username": self.username,
            "timestamp": timestamp,
            "amount": amount,
            "password": password_hash,
            "mobilephone": mobile_phone,
            "requesttransactionid": request_transaction_id,
            "accountno": self.account_number,
        }
        body["callbackurl"] = self.callback_url
        request = Request(
            f"{self.base_url}/requestpayment/",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            raise IntouchPayError("The IntouchPay sandbox could not be reached.") from error
        return payload


def callback_payload(data):
    """Normalize IntouchPay's nested callback payload."""
    if isinstance(data, dict) and isinstance(data.get("jsonpayload"), dict):
        return data["jsonpayload"]
    return data if isinstance(data, dict) else {}


def is_successful_status(payload):
    code = str(payload.get("responsecode", ""))
    status = str(payload.get("status", "")).lower()
    return code == "01" or status in {"success", "successful", "completed", "paid"}


def is_failed_status(payload):
    code = str(payload.get("responsecode", ""))
    status = str(payload.get("status", "")).lower()
    return code not in {"", "1000"} and status not in {"pending", "processing"} or status in {"failed", "failure", "rejected", "cancelled"}
