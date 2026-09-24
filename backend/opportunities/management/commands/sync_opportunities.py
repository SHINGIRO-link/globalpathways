import json
import os
from datetime import datetime, timezone as dt_timezone
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Fetch validated opportunity feeds and upsert active records."

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
    SYNC_FIELDS = {
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
            "--feed-url",
            action="append",
            dest="feed_urls",
            help="JSON feed URL; may be repeated. Defaults to OPPORTUNITY_FEED_URLS.",
        )
        parser.add_argument("--timeout", type=int, default=20)

    def handle(self, *args, **options):
        feed_urls = options.get("feed_urls") or [
            value.strip()
            for value in os.getenv("OPPORTUNITY_FEED_URLS", "").split(",")
            if value.strip()
        ]
        if not feed_urls:
            raise CommandError("No feed URLs configured. Set OPPORTUNITY_FEED_URLS or pass --feed-url.")

        validated = []
        for url in feed_urls:
            rows = self.fetch_feed(url, options["timeout"])
            validated.extend(
                self.validate_row(row, url, index)
                for index, row in enumerate(rows, start=1)
            )

        with transaction.atomic():
            for values in validated:
                slug = values.pop("slug")
                Opportunity.objects.update_or_create(slug=slug, defaults=values)

        self.stdout.write(
            self.style.SUCCESS(
                f"Fetched and upserted {len(validated)} opportunities from {len(feed_urls)} feed(s)."
            )
        )

    def fetch_feed(self, url, timeout):
        request = Request(url, headers={"User-Agent": "GlobalPathwaysOpportunitySync/1.0"})
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise CommandError(f"Could not fetch opportunity feed {url}: {exc}") from exc

        if isinstance(payload, dict):
            payload = payload.get("opportunities") or payload.get("items")
        if not isinstance(payload, list) or not payload:
            raise CommandError(
                f"Feed {url} must return a non-empty JSON list or an object with opportunities/items."
            )
        return payload

    def validate_row(self, row, source_url, row_number):
        if not isinstance(row, dict):
            raise CommandError(f"Feed {source_url} row {row_number} must be a JSON object.")
        missing = sorted(field for field in self.REQUIRED_FIELDS if not row.get(field))
        if missing:
            raise CommandError(
                f"Feed {source_url} row {row_number} is missing: {', '.join(missing)}"
            )
        if row["category"] not in dict(Opportunity.CATEGORY_CHOICES):
            raise CommandError(f"Unsupported category for {row['slug']}: {row['category']}")
        if row["status"] not in dict(Opportunity.STATUS_CHOICES):
            raise CommandError(f"Unsupported status for {row['slug']}: {row['status']}")

        deadline = parse_datetime(str(row["deadline"]))
        if deadline is None:
            raise CommandError(f"Invalid deadline for {row['slug']}")
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline, dt_timezone.utc)

        values = {key: value for key, value in row.items() if key in self.SYNC_FIELDS}
        values["deadline"] = deadline
        values.setdefault("source_url", source_url)
        values.setdefault("source_verified_at", datetime.now(dt_timezone.utc).date())
        values.setdefault("region", "Europe")
        values.setdefault("eligibility", [])
        values.setdefault("required_documents", [])
        values.setdefault("featured", False)
        return values
