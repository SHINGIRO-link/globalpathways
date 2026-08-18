from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from opportunities.models import AccountProfile


class Command(BaseCommand):
    help = "Create or update a first-party Global Pathways account and role."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--name", default="")
        parser.add_argument("--role", choices=["user", "staff", "admin"], default="user")
        parser.add_argument("--password", required=False)

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        if not email or "@" not in email:
            raise CommandError("Provide a valid email address.")
        User = get_user_model()
        user, created = User.objects.get_or_create(username=email, defaults={"email": email})
        user.email = email
        if options["name"]:
            user.first_name = options["name"].strip()
        if options["password"]:
            user.set_password(options["password"])
        if options["role"] == "admin":
            user.is_staff = True
            user.is_superuser = True
        elif options["role"] == "staff":
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()
        profile, _ = AccountProfile.objects.get_or_create(user=user)
        profile.role = options["role"]
        profile.save(update_fields=["role", "updated_at"])
        self.stdout.write(self.style.SUCCESS(f"Local account {'created' if created else 'updated'} for {email} with role {profile.role}."))
