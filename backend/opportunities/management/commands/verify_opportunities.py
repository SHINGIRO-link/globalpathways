from django.core.management.base import BaseCommand, CommandError

from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Verify opportunity counts and required fields after database initialization."

    def handle(self, *args, **options):
        total = Opportunity.objects.count()
        counts = {
            category: Opportunity.objects.filter(category=category).count()
            for category, _label in Opportunity.CATEGORY_CHOICES
        }
        missing = Opportunity.objects.filter(title="").count()
        invalid = Opportunity.objects.filter(slug="").count()

        self.stdout.write(f"total={total}")
        for category, count in counts.items():
            self.stdout.write(f"{category}={count}")

        if missing or invalid:
            raise CommandError(
                f"Invalid records found: blank_titles={missing}, blank_slugs={invalid}"
            )
        if total == 0:
            raise CommandError("The opportunity table is empty.")

        self.stdout.write(self.style.SUCCESS("Opportunity database verification passed."))
