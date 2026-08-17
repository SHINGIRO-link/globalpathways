import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import Application, GuestAccessToken

STATUS_TTL = timedelta(days=14)
CLAIM_TTL = timedelta(days=14)


def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def issue_token(application: Application, purpose: str, ttl: timedelta) -> str:
    GuestAccessToken.objects.filter(application=application, purpose=purpose, used_at__isnull=True).update(used_at=timezone.now())
    raw_token = secrets.token_urlsafe(32)
    GuestAccessToken.objects.create(
        application=application,
        email=application.email.lower(),
        token_hash=_hash(raw_token),
        purpose=purpose,
        expires_at=timezone.now() + ttl,
    )
    return raw_token


def consume_token(raw_token: str, purpose: str) -> GuestAccessToken | None:
    if not raw_token:
        return None
    token = GuestAccessToken.objects.select_related("application", "application__opportunity").filter(token_hash=_hash(raw_token), purpose=purpose).first()
    if not token or token.used_at or token.expires_at <= timezone.now():
        return None
    return token


def create_guest_access(application: Application) -> dict[str, str]:
    """Issue capability links for guests without requiring email verification."""
    return {
        "status_token": issue_token(application, "status", STATUS_TTL),
        "claim_token": issue_token(application, "claim", CLAIM_TTL),
    }


def create_claim_token(application: Application) -> str:
    return issue_token(application, "claim", CLAIM_TTL)
