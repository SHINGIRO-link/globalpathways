import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


class IntouchPayError(Exception):
    """Raised when an IntouchPay request cannot be completed safely."""

    def __init__(self, message, *, category="provider_error", http_status=None, provider_code=None):
        super().__init__(message)
        self.category = category
        self.http_status = http_status
        self.provider_code = provider_code


SAFE_PROVIDER_MESSAGES = {
    "0002": "The payment gateway is missing its merchant username. Check the configured sandbox account.",
    "0003": "The payment gateway is missing its authentication value. Check the configured sandbox credentials.",
    "0004": "The payment gateway rejected the request timestamp. Check the server clock and timestamp format.",
    "0005": "The payment gateway rejected its credentials. Confirm the sandbox username, account number, and partner password with IntouchPay.",
    "0006": "The IntouchPay merchant account is not active for collections. Confirm the account setup with IntouchPay.",
    "0007": "IntouchPay could not find the configured merchant account. Confirm the account number and credentials with IntouchPay.",
    "0008": "IntouchPay authentication failed. Confirm the account credentials and API access with IntouchPay.",
    "1002": "This phone number is not registered for mobile money. Check the number or choose another mobile-money account.",
    "1100": "This number is not supported on the selected mobile-money network. Check the number and provider.",
    "1200": "The mobile-money number is invalid. Enter a valid Rwanda mobile number.",
    "2100": "The requested payment amount is invalid.",
    "2200": "The requested amount is below IntouchPay's minimum. Confirm the minimum amount with IntouchPay.",
    "2300": "The requested amount exceeds IntouchPay's limit. Confirm the maximum amount with IntouchPay.",
    "2400": "IntouchPay received a duplicate request identifier. Please retry once; contact support if it persists.",
    "2500": "IntouchPay could not find the configured collection route. Confirm the merchant's sandbox route with IntouchPay.",
    "2600": "The merchant account is not permitted to collect this payment. Confirm collection permissions with IntouchPay.",
    "2700": "IntouchPay could not complete this request. Please retry later or contact the provider.",
    "1005": "The payment could not be completed because of insufficient funds or balance.",
    "1008": "IntouchPay could not complete this request. Please retry later or contact the provider.",
    "1300": "IntouchPay could not complete this request. Please retry later or contact the provider.",
}


def _provider_error_message(provider_code):
    return SAFE_PROVIDER_MESSAGES.get(
        provider_code,
        "IntouchPay rejected the payment request. Confirm the merchant setup with IntouchPay.",
    )


def _safe_provider_code(error):
    """Extract only a short response code; never retain or log the provider body."""
    try:
        body = error.read(4096)
        payload = json.loads(body.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    code = payload.get("responsecode") or payload.get("errorcode") or payload.get("code")
    if isinstance(code, int):
        code = str(code)
    if isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,16}", code):
        return code
    return None


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
            raise IntouchPayError(
                "IntouchPay sandbox credentials are not configured.",
                category="configuration",
            )
        if not self.callback_url:
            raise IntouchPayError(
                "IntouchPay callback URL is not configured.",
                category="configuration",
            )
        timestamp, password_hash = self._credentials()
        body = {
            "username": self.username,
            "timestamp": timestamp,
            "amount": amount,
            "password": password_hash,
            "mobilephone": mobile_phone,
            "requesttransactionid": request_transaction_id,
            "accountno": self.account_number,
            "callbackurl": self.callback_url,
        }
        request = Request(
            f"{self.base_url}/requestpayment/",
            data=urlencode(body).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read()
        except HTTPError as error:
            provider_code = _safe_provider_code(error)
            logger.error(
                "IntouchPay upstream HTTP error: status=%s provider_code=%s",
                error.code,
                provider_code or "unknown",
            )
            detail = f"{_provider_error_message(provider_code)} (response code {provider_code})" if provider_code else "Check the provider account, credentials, and API version."
            raise IntouchPayError(
                f"IntouchPay returned HTTP {error.code}. {detail}",
                category="upstream_http",
                http_status=error.code,
                provider_code=provider_code,
            ) from error
        except URLError as error:
            reason_type = type(error.reason).__name__
            logger.error("IntouchPay transport failure: reason_type=%s", reason_type)
            raise IntouchPayError(
                "IntouchPay could not be reached. Check provider connectivity and retry later.",
                category="transport",
            ) from error
        except TimeoutError as error:
            logger.error("IntouchPay request timed out.")
            raise IntouchPayError(
                "IntouchPay request timed out. Retry later.",
                category="timeout",
            ) from error

        try:
            payload = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            logger.error("IntouchPay returned an unreadable response.")
            raise IntouchPayError(
                "IntouchPay returned an unreadable response. Contact the payment provider if the problem persists.",
                category="invalid_response",
            ) from error
        if not isinstance(payload, dict):
            logger.error("IntouchPay returned a non-object JSON response.")
            raise IntouchPayError(
                "IntouchPay returned an unreadable response. Contact the payment provider if the problem persists.",
                category="invalid_response",
            )
        provider_code = payload.get("responsecode") or payload.get("errorcode") or payload.get("code")
        if isinstance(provider_code, int):
            provider_code = str(provider_code)
        if not isinstance(provider_code, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,16}", provider_code):
            provider_code = None
        success_value = payload.get("success")
        is_explicit_failure = success_value is False or (isinstance(success_value, str) and success_value.strip().lower() in {"false", "no", "0"})
        if is_explicit_failure or (provider_code and provider_code not in {"1000", "01"}):
            logger.error("IntouchPay rejected payment request: provider_code=%s", provider_code or "unknown")
            detail = _provider_error_message(provider_code)
            code_detail = f" (response code {provider_code})" if provider_code else ""
            raise IntouchPayError(
                f"IntouchPay rejected the payment request. {detail}{code_detail}",
                category="provider_rejected",
                provider_code=provider_code,
            )
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
