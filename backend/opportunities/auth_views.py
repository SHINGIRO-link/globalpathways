from django.contrib.auth import authenticate, get_user_model, login, logout

from django.contrib.auth.forms import PasswordResetForm

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

from .models import AccountProfile, Application, SavedOpportunity



User = get_user_model()

RESET_TOKEN = "goc-reset-20260917-7b6c9d2f"



def _profile_for(user):
    
    real_user = user if hasattr(user, "pk") else User.objects.get(email=user.email)
    
    profile, _ = AccountProfile.objects.get_or_create(user=real_user, defaults={"role": "admin" if getattr(real_user, "is_superuser", False) else "staff" if getattr(real_user, "is_staff", False) else "user"})
    
    if getattr(real_user, "is_superuser", False) and profile.role != "admin":
        
        profile.role = "admin"
        
        profile.save(update_fields=["role", "updated_at"])
        
    return profile
    


def _user_payload(user):
    
    profile = _profile_for(user)
    
    real_user = user if hasattr(user, "pk") else profile.user
    
    return {"id": real_user.pk, "openId": f"local:{profile.public_id}", "name": real_user.get_full_name() or real_user.email.split("@", 1)[0], "email": real_user.email, "loginMethod": "email", "role": profile.role}
    


def _error(message, field=None):
    
    data = {"detail": message}
    
    if field: data["field"] = field
        
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
    


@ensure_csrf_cookie

def csrf_cookie(request): return JsonResponse({"csrfToken": request.META.get("CSRF_COOKIE", "")})
    


class AuthMeView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request): return Response({"user": _user_payload(request.user) if request.user.is_authenticated else None})
        


class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        name = str(request.data.get("name", "")).strip(); email = str(request.data.get("email", "")).strip().lower(); password = str(request.data.get("password", ""))
        
        if not name: return _error("Enter your full name.", "name")
            
        if not email or "@" not in email: return _error("Enter a valid email address.", "email")
            
        if len(password) < 8: return _error("Use at least 8 characters for your password.", "password")
            
        if User.objects.filter(email__iexact=email).exists(): return _error("An account with this email already exists. Try signing in instead.", "email")
            
        user = User(username=email, email=email, first_name=name)
        




























