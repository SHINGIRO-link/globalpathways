from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("opportunities", "0005_opportunity_deadline_note_opportunity_source_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="document_metadata",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
