import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from opportunities.models import Opportunity
from opportunities.management.commands.seed_opportunities import VERIFIED_OVERRIDES
print({key: {field: value for field, value in override.items() if field in {"title", "category", "status"}} for key, override in VERIFIED_OVERRIDES.items()})
for item in Opportunity.objects.order_by("id"):
    print(item.slug, item.category, item.title, bool(item.source_url), item.source_name)
