import json
from datetime import timezone as dt_timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Validate and import the bundled opportunity catalogue atomically."

    REQUIRED_FIELDS = {
        "title",
        "slug",
        "category",
        "status",
        "country",
        "deadline",
        "summary",
        "description",
    }
    IMPORT_FIELDS = {
        "title",
        "slug",
        "category",
        "status",
        "country",
        "region",
        "deadline",
        "deadline_note",
        "source_name",
        "source_url",
        "source_verified_at",
        "summary",
        "description",
        "eligibility",
        "required_documents",
        "featured",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="opportunities/uploaded_opportunities.json",
            help="Catalogue path relative to the backend directory, or an absolute path.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Deprecated compatibility flag; matching slugs are always updated.",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        if not path.exists():
            raise CommandError(f"Import file not found: {path}")

        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Could not read import file {path}: {exc}") from exc
        if not isinstance(rows, list) or not rows:
            raise CommandError("Import file must contain a non-empty JSON list.")

        validated = [self.validate_row(row, index) for index, row in enumerate(rows, start=1)]
        with transaction.atomic():
            for values in validated:
                slug = values.pop("slug")
                Opportunity.objects.update_or_create(slug=slug, defaults=values)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(validated)} opportunities with update_or_create.")
        )

    def validate_row(self, row, row_number):
        if not isinstance(row, dict):
            raise CommandError(f"Row {row_number} must be a JSON object.")
        missing = sorted(field for field in self.REQUIRED_FIELDS if not row.get(field))
        if missing:
            raise CommandError(f"Row {row_number} is missing: {', '.join(missing)}")
        if row["category"] not in dict(Opportunity.CATEGORY_CHOICES):
            raise CommandError(f"Row {row_number} has an unsupported category: {row['category']}")
        if row["status"] not in dict(Opportunity.STATUS_CHOICES):
            raise CommandError(f"Row {row_number} has an unsupported status: {row['status']}")

        deadline = parse_datetime(str(row["deadline"]))
        if deadline is None:
            raise CommandError(f"Row {row_number} has an invalid deadline.")
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline, dt_timezone.utc)

        values = {key: value for key, value in row.items() if key in self.IMPORT_FIELDS}
        values["deadline"] = deadline
        values.setdefault("region", "Europe")
        values.setdefault("eligibility", [])
        values.setdefault("required_documents", [])
        values.setdefault("featured", False)
        return values
