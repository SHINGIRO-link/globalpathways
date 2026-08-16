# Global Pathways architecture

Global Pathways now contains a **Django + Django REST Framework backend** under `backend/` and a **React frontend** under `client/`. The frontend calls the Django REST resources through `client/src/lib/api.ts`; the default base path is `/api`, and local development can point directly to a Django server with `VITE_API_BASE_URL=http://127.0.0.1:8000/api`.

| Area | Implementation |
| --- | --- |
| Opportunity discovery | `GET /api/opportunities/` with search, category, region, status, and ordering support |
| Opportunity details | `GET /api/opportunities/<slug>/` |
| Applications | `POST /api/applications/` with consent validation |
| Inquiries | `POST /api/inquiries/` |
| Success stories | `GET /api/success-stories/`, filtered to consent-confirmed published stories |
| Admin | `/admin/` for opportunities, applications, inquiries, and success stories |
| Frontend routes | `/`, `/opportunities`, `/opportunities/<slug>`, `/apply/<slug>` |

## Local development

Run the Django API from the project root:

```bash
pip install -r backend/requirements.txt
python3 backend/manage.py migrate
python3 backend/manage.py createsuperuser
python3 backend/manage.py runserver 8000
```

Run the React/managed frontend in another terminal:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api pnpm dev
```

The managed project preview remains available through its existing Node process. The Django service is intentionally kept as a real, independently runnable Python service rather than replacing it with a JavaScript imitation. A production deployment that hosts both services behind one public origin still needs an infrastructure-specific reverse-proxy or separate service configuration; the current project keeps this boundary explicit for safe follow-up work.

## Trust and content policy

The opportunity cards use clearly labeled sample discovery content for the interface and data model. The success-story UI does not invent testimonials or ratings. Django only exposes stories when both `published=True` and `consent_confirmed=True`, so editorial approval and permission are required before publication.


## Dashboard and deferred payment extension

The personalized workspace is available at `/dashboard`. It uses the signed-in user email as the current dashboard key and can also be previewed by entering an application email. The dashboard reads application summaries, saved opportunities, status history, and payment-ready records from Django.

| Area | Endpoint or model | Behavior |
| --- | --- | --- |
| Dashboard overview | `GET /api/dashboard/?email=...` | Returns applications and saved opportunities for the requested email |
| Saved opportunities | `POST /api/saved-opportunities/`, `DELETE /api/saved-opportunities/<opportunity_id>/?email=...` | Saves and removes opportunity shortlist entries |
| Application status | `GET /api/applications/<id>/status/?email=...` | Returns the current application, status events, and payment record |
| Payment-ready preparation | `POST /api/payments/prepare/` | Records MoMo/Airtel provider selection as `integration_pending`; it does not charge or claim payment |
| Application lifecycle | `Application.status` plus `ApplicationStatusEvent` | Starts at `payment_required`, then can move through received, reviewing, needs information, approved, or not approved |
| Payment record | `PaymentRecord` | Stores the 2,000 service-fee amount, provider selection, currency placeholder, status, and later provider reference |

Live MoMo and Airtel Money integration is intentionally deferred. Before enabling collection, configure the operating country, currency, merchant onboarding, server-side credentials, provider callback/status reconciliation, refund handling, and the final customer-facing fee terms. The current UI is explicit that no money has been received while integration is pending.


## Session ownership

Personalized endpoints now require the shared `app_session_id` Manus session or a bearer token validated with `JWT_SECRET` by `backend/opportunities/authentication.py`. The React dashboard sends the signed-in email as a consistency check, but the Django permission boundary first requires a validated authenticated session. Public discovery and application submission remain available without dashboard access; personalized reads, saves, status history, and payment-provider selection require authentication.
