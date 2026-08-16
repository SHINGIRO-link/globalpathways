import base64
import hashlib
import hmac
import json
import os
import time
from types import SimpleNamespace

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed


COOKIE_NAME = "app_session_id"


def _decode_part(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class ManusSessionAuthentication(BaseAuthentication):
    """Validate the shared HS256 Manus session without trusting browser-supplied identity headers."""

    def authenticate(self, request):
        token = request.COOKIES.get(COOKIE_NAME)
        if not token:
            authorization = get_authorization_header(request).split()
            if len(authorization) == 2 and authorization[0].lower() == b"bearer":
                token = authorization[1].decode("utf-8")
        if not token:
            return None
        try:
            header, payload, signature = token.split(".")
            if json.loads(_decode_part(header)).get("alg") != "HS256":
                raise ValueError("Unsupported algorithm")
            expected = hmac.new(os.environ.get("JWT_SECRET", "").encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _decode_part(signature)):
                raise ValueError("Invalid signature")
            claims = json.loads(_decode_part(payload))
            if not claims.get("openId") or not claims.get("appId") or not claims.get("name"):
                raise ValueError("Incomplete session")
            if claims.get("exp") and int(claims["exp"]) < int(time.time()):
                raise ValueError("Expired session")
            user = SimpleNamespace(is_authenticated=True, open_id=claims["openId"], app_id=claims["appId"], name=claims["name"])
            return user, token
        except Exception as exc:
            raise AuthenticationFailed("Invalid or expired session.") from exc

    def authenticate_header(self, request):
        return "Bearer"


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        owner_open_id = os.environ.get("OWNER_OPEN_ID", "")
        if not request.user or not getattr(request.user, "is_authenticated", False):
            return False
        return bool(owner_open_id and getattr(request.user, "open_id", "") == owner_open_id)
