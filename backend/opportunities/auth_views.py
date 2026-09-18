from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccountProfile

User = get_user_model()


def _profile_for(user):
    profile, _ = AccountProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": "admin" if getattr(user, "is_superuser", False)
            else "staff" if getattr(user, "is_staff", False)
            else "user"
        },
    )
    if getattr(user, "is_superuser", False) and profile.role != "admin":
        profile.role = "admin"
        profile.save(update_fields=["role", "updated_at"])
    return profile


def _user_payload(user):
    profile = _profile_for(user)
    return {
        "id": user.pk,
        "openId": f"local:{profile.public_id}",
        "name": user.get_full_name() or user.email.split("@", 1)[0],
        "email": user.email,
        "loginMethod": "email",
        "role": profile.role,
    }


def _error(message, field=None):
    data = {"detail": message}
    if field:
        data["field"] = field
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


@ensure_csrf_cookie
def csrf_cookie(request):
    return JsonResponse({"csrfToken": request.META.get("CSRF_COOKIE", "")})


class AuthMeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"user": _user_payload(request.user) if request.user.is_authenticated else None})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        email = str(request.data.get("email", "")).strip().lower()
        password = str(request.data.get("password", ""))
        if not name:
            return _error("Enter your full name.", "name")
        if not email or "@" not in email:
            return _error("Enter a valid email address.", "email")
        if len(password) < 8:
            return _error("Use at least 8 characters for your password.", "password")
        if User.objects.filter(email__iexact=email).exists():
            return _error("An account with this email already exists. Try signing in instead.", "email")
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        _profile_for(user)
        login(request, user)
        return Response({"user": _user_payload(user)}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = str(request.data.get("password", ""))
        user = authenticate(request, username=email, password=password)
        if not user:
            return _error("The email or password is not correct.")
        login(request, user)
        return Response({"user": _user_payload(user)})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"loggedOut": True})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                "Reset your Global Pathways password",
                f"Use this link to reset your password: /reset-password?uid={uid}&token={token}",
                None,
                [user.email],
                fail_silently=True,
            )
        return Response({"detail": "If an account exists for that email, we sent password reset instructions."}, status=status.HTTP_202_ACCEPTED)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        uid = str(request.data.get("uid", ""))
        token = str(request.data.get("token", ""))
        password = str(request.data.get("password", ""))
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return _error("This password reset link is invalid or expired.")
        if not default_token_generator.check_token(user, token):
            return _error("This password reset link is invalid or expired.")
        try:
            validate_password(password, user)
        except ValidationError as error:
            return _error(error.messages[0], "password")
        user.set_password(password)
        user.save(update_fields=["password"])
        login(request, user)
        return Response({"user": _user_payload(user)})
