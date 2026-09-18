import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Import the validated uploaded opportunity catalogue using update_or_create."

    def add_arguments(self, parser):
        parser.add_argument("--file", default="opportunities/uploaded_opportunities.json")
        parser.add_argument("--replace", action="store_true", help="Allow replacing existing rows with matching slugs (default behavior).")

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        if not path.exists():
            raise CommandError(f"Import file not found: {path}")
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or not rows:
            raise CommandError("Import file must contain a non-empty JSON list.")
        imported = 0
        for row in rows:
            values = dict(row)
            values["deadline"] = parse_datetime(values["deadline"])
            if values["deadline"] is None:
                raise CommandError(f"Invalid deadline for {row.get('slug')}")
            slug = values.pop("slug")
            Opportunity.objects.update_or_create(slug=slug, defaults=values)
            imported += 1
        self.stdout.write(self.style.SUCCESS(f"Imported {imported} opportunities with update_or_create."))
