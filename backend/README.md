# Global Pathways Django API

This directory contains the Python/Django backend requested for Global Pathways. The React frontend communicates with the REST endpoints under `/api/`.

## Local setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

The API exposes public opportunity discovery and detail routes, plus authenticated-ready submission endpoints for applications and inquiries. The Django admin is available at `/admin/`.
