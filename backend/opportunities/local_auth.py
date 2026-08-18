from types import SimpleNamespace

from .models import AccountProfile


def _profile_for(user):
    profile, _ = AccountProfile.objects.get_or_create(
        user=user,
        defaults={"role": "admin" if user.is_superuser else "staff" if user.is_staff else "user"},
    )
    if user.is_superuser and profile.role != "admin":
        profile.role = "admin"
        profile.save(update_fields=["role", "updated_at"])
    return profile


class LocalSessionAuthentication:
    """Expose Django-session users as the application identity used by DRF views."""

    def authenticate(self, request):
        django_request = getattr(request, "_request", request)
        user = getattr(django_request, "user", None)
        if not user or not user.is_authenticated:
            return None
        profile = _profile_for(user)
        return SimpleNamespace(
            is_authenticated=True,
            open_id=f"local:{profile.public_id}",
            app_id="globalpathways-local",
            name=user.get_full_name() or user.email,
            email=user.email,
            role=profile.role,
        ), None

    def authenticate_header(self, request):
        return "Session"
