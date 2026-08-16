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
