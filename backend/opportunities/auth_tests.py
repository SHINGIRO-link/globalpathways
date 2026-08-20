from django.core import mail
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AccountProfile


User = get_user_model()


class LocalAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_profile_and_session(self):
        response = self.client.post("/api/auth/register/", {"name": "Amina Test", "email": "amina@example.com", "password": "SafePassword123!"}, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="amina@example.com")
        self.assertEqual(AccountProfile.objects.get(user=user).role, "user")
        self.assertEqual(self.client.get("/api/auth/me/").data["user"]["email"], "amina@example.com")
        self.assertEqual(self.client.get("/api/auth/me/").data["user"]["role"], "user")

    def test_login_and_logout_use_django_session(self):
        user = User.objects.create_user(username="staff@example.com", email="staff@example.com", password="SafePassword123!")
        AccountProfile.objects.create(user=user, role="staff")
        login = self.client.post("/api/auth/login/", {"email": "staff@example.com", "password": "SafePassword123!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data["user"]["role"], "staff")
        self.assertEqual(self.client.post("/api/auth/logout/", {}, format="json").status_code, 200)
        self.assertIsNone(self.client.get("/api/auth/me/").data["user"])

    def test_invalid_login_is_generic(self):
        User.objects.create_user(username="user@example.com", email="user@example.com", password="SafePassword123!")
        response = self.client.post("/api/auth/login/", {"email": "user@example.com", "password": "wrong-password"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "The email or password is not correct.")

    def test_password_reset_request_does_not_enumerate_accounts(self):
        User.objects.create_user(username="reset@example.com", email="reset@example.com", password="SafePassword123!")
        response = self.client.post("/api/auth/password-reset/", {"email": "reset@example.com"}, format="json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/reset-password?uid=", mail.outbox[0].body)
        unknown = self.client.post("/api/auth/password-reset/", {"email": "unknown@example.com"}, format="json")
        self.assertEqual(unknown.status_code, 202)
        self.assertEqual(len(mail.outbox), 1)


class AdminAccountManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin = User.objects.create_user(username="owner@example.com", email="owner@example.com", password="SafePassword123!")
        AccountProfile.objects.create(user=admin, role="admin")
        applicant = User.objects.create_user(username="applicant@example.com", email="applicant@example.com", password="SafePassword123!")
        AccountProfile.objects.create(user=applicant, role="user")
        self.client.force_authenticate(admin)

    def test_admin_can_list_and_change_account_role(self):
        response = self.client.get("/api/admin/accounts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["accounts"]), 2)
        applicant = User.objects.get(email="applicant@example.com")
        changed = self.client.patch(f"/api/admin/accounts/{applicant.account_profile.id}/", {"role": "staff"}, format="json")
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.data["role"], "staff")

    def test_admin_cannot_demote_self(self):
        admin = User.objects.get(email="owner@example.com")
        response = self.client.patch(f"/api/admin/accounts/{admin.account_profile.id}/", {"role": "user"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(admin.account_profile.role, "admin")

    def test_applicant_cannot_list_accounts(self):
        applicant = User.objects.get(email="applicant@example.com")
        self.client.force_authenticate(applicant)
        self.assertEqual(self.client.get("/api/admin/accounts/").status_code, 403)
