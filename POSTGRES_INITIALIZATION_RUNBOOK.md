# PostgreSQL initialization and production verification

This runbook initializes the GlobalPathways catalogue on Render PostgreSQL and verifies that both the Render hostname and the custom domain serve the same data.

## Expected catalogue

The bundled catalogue is `backend/opportunities/uploaded_opportunities.json` and contains **104 records**: **37 scholarships** and **67 jobs**. The importer is idempotent and keys records by `slug`.

## Render configuration

Create or select a persistent PostgreSQL database in the same Render region as the web service. Set the database's **internal** connection string on the web service and cron service:

```text
DATABASE_URL=<Render internal PostgreSQL connection string>
DATABASE_SSL_REQUIRE=true
```

Never commit a connection string or secret to source control. The Django settings use PostgreSQL when `DATABASE_URL` is present and SQLite only as a local-development fallback.

## Initialization

The Docker startup command runs migrations and imports the bundled catalogue before starting Gunicorn:

```sh
cd /app/backend
python manage.py migrate --noinput
python manage.py import_uploaded_opportunities
python manage.py verify_opportunities
```

The expected verification output is:

```text
total=104
scholarship=37
visa=0
job=67
Opportunity database verification passed.
```

Both management commands are safe to rerun. The importer validates all rows before opening an atomic transaction, preventing a malformed row from leaving a partial import.

## Scheduled synchronization

The optional Render Cron Job is defined in `render.yaml` and runs every six hours:

```cron
0 */6 * * *
```

Configure `OPPORTUNITY_FEED_URLS` as a comma-separated list of trusted JSON feeds. Each feed must return a list, or an object with an `opportunities` or `items` list. The synchronizer validates required fields, supported categories/statuses, deadlines, and filters unknown fields before an atomic upsert.

## API verification

Run the repository script against the Render hostname:

```sh
python3 verify_api.py https://globalpathways-gglc.onrender.com
```

It must report `total=104`, `scholarships=37`, and `verification=passed`.

After the custom domain has been released from the old Render service and attached to `globalpathways`, run the same check against:

```sh
python3 verify_api.py https://globalopportunityconnect.com
```

The custom-domain response must match the Render hostname. If health is `ok` but the catalogue is empty, the domain is still routed to the wrong Render service or database.

## Domain and SSL checklist

1. Remove `globalopportunityconnect.com` from the old Render service.
2. Add it to `globalpathways` (`srv-damhmqijnfac73anfgdg`).
3. Keep the existing Namecheap records unchanged unless Render provides new target values.
4. Wait for Render's certificate status to become active.
5. Confirm HTTPS, `/api/health/`, 104 total records, and 37 scholarships.
