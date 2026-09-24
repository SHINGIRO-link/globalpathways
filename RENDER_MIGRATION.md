# GlobalPathways Render migration

## Current status

The `globalpathways` Render service is healthy at `https://globalpathways-gglc.onrender.com`. The requested custom domain could not be attached because Render reports that `globalopportunityconnect.com` already exists on another Render site. Remove the domain from the old Render site first, then add it to service `srv-damhmqijnfac73anfgdg`.

The repository changes in this bundle make Django use PostgreSQL whenever `DATABASE_URL` is present, while preserving SQLite as a local-development fallback.

## Database migration

1. Create a persistent Render Postgres database named `globalpathways-db` using a paid plan. Do not use the Free plan for production: Render documents a 30-day expiry and no backups for Free Postgres.
2. Attach the database's internal connection string to the web service as `DATABASE_URL`.
3. Add `DATABASE_SSL_REQUIRE=true`.
4. Deploy the code in this bundle.
5. The existing startup command runs migrations and imports `backend/opportunities/uploaded_opportunities.json`:

```sh
python manage.py migrate --noinput
python manage.py import_uploaded_opportunities
```

6. Verify:

```sh
curl https://globalopportunityconnect.com/api/health/
curl https://globalopportunityconnect.com/api/opportunities/
curl 'https://globalopportunityconnect.com/api/opportunities/?category=scholarship'
```

The expected catalogue is 104 records: 37 scholarships and 67 jobs.

## Scheduled sync

The new command reads one or more JSON feed URLs from `OPPORTUNITY_FEED_URLS` or repeated `--feed-url` arguments. Each feed must return either a JSON list or an object containing `opportunities` or `items`. It validates categories, statuses, deadlines, and required fields before using `update_or_create` by slug.

Example command:

```sh
python manage.py sync_opportunities --feed-url https://example.org/globalpathways-opportunities.json
```

A Render Cron Job can run it every six hours:

```cron
0 */6 * * *
```

Cron job command:

```sh
python manage.py migrate --noinput && python manage.py sync_opportunities
```

Set `DATABASE_URL`, `DATABASE_SSL_REQUIRE=true`, and `OPPORTUNITY_FEED_URLS` on both the web service and cron service. Render Cron Jobs have a minimum monthly charge of $1 per cron service.

## DNS

Current DNS observations:

```dns
@       A       216.24.57.16
@       A       216.24.57.18
www     CNAME   globalpathways-gglc.onrender.com.
```

These records already resolve through Render. The blocking issue is not the current DNS values; it is that Render has the domain attached to another site. After detaching it from the old site and adding it to `globalpathways`, recheck the records in Render's custom-domain panel before changing DNS.
