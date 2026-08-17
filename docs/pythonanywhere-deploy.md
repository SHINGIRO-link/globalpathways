# Deploying Global Pathways on PythonAnywhere

This guide deploys the **Django API** under `backend/`. The existing React frontend and Node same-origin proxy are separate services. The frontend can remain on Manus and use `VITE_API_BASE_URL` only if it points directly to the PythonAnywhere API and the API allows that origin; otherwise deploy the frontend and proxy together on a compatible Node host.

## 1. Clone the private repository

In a PythonAnywhere Bash console, configure GitHub access, then run:

```bash
git clone https://github.com/SHINGIRO-link/globalpathways.git ~/globalpathways
cd ~/globalpathways/backend
```

Use an SSH key or GitHub credential method supported by PythonAnywhere. Do not place credentials in the repository.

## 2. Create the virtual environment

Use a Python version supported by the PythonAnywhere account and compatible with the pinned project dependencies:

```bash
mkvirtualenv --python=/usr/bin/python3.10 globalpathways-venv
workon globalpathways-venv
pip install -r ~/globalpathways/backend/requirements.txt
```

If the account offers a different supported Python version, use the same version when creating the Web app and virtual environment.

## 3. Configure private environment values

Create a private file outside Git tracking, for example `~/globalpathways/backend/.env`, and load it in the PythonAnywhere WSGI file before Django starts. At minimum configure:

```text
DJANGO_SECRET_KEY=<long-random-production-secret>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<pythonanywhere-hostname>
DJANGO_CORS_ALLOWED_ORIGINS=<frontend-origin>
DJANGO_CSRF_TRUSTED_ORIGINS=<https-frontend-origin>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<mailbox>
SMTP_PASSWORD=<mail-app-password>
SMTP_FROM=<verified-sender>
SMTP_STAFF_RECIPIENT=<staff-recipient>
```

Do not commit this file. If the frontend remains on Manus, the CORS and CSRF origin values must match the exact public Manus origin. If the API uses Manus session authentication or storage proxy services, those service credentials and callback configuration must also be available in the deployed architecture; PythonAnywhere alone does not automatically provide Manus runtime environment values.

## 4. Create the Web app

In the PythonAnywhere **Web** tab, create a new application using **Manual Configuration**, select the same Python version as the virtual environment, set the source and working directory to `~/globalpathways/backend`, and select the `globalpathways-venv` virtual environment.

Edit the PythonAnywhere-provided WSGI file. Replace its contents with the following, adjusting the username and private environment-file path:

```python
import os
import sys
from pathlib import Path

project_path = Path.home() / "globalpathways" / "backend"
sys.path.insert(0, str(project_path))

from dotenv import load_dotenv
load_dotenv(project_path / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Install `python-dotenv` in the virtual environment if you use the WSGI example:

```bash
workon globalpathways-venv
pip install python-dotenv
```

## 5. Initialize the database and static files

From a Bash console with the virtual environment active:

```bash
cd ~/globalpathways/backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Configure a static-files mapping in the PythonAnywhere Web tab from `/static/` to `~/globalpathways/backend/staticfiles/`, then reload the Web app. SQLite is suitable for a small initial deployment; use a managed MySQL/PostgreSQL service before high-volume production use.

## 6. Validate the API

After reload, check:

```bash
curl -i https://<pythonanywhere-hostname>/api/health/
curl -i https://<pythonanywhere-hostname>/api/opportunities/
```

Then test an application submission, document upload, guest status link, optional claim flow, staff authorization, email delivery, and CSV/ZIP exports. Review the PythonAnywhere error log after every reload.

## Important architecture constraint

PythonAnywhere deployment of `backend/` does **not** deploy the React frontend, Express proxy, Manus OAuth callback, or Manus storage proxy. Before switching production traffic, decide whether the frontend/proxy will remain on Manus or be hosted elsewhere, then configure API origin, OAuth callback, CORS, storage, and email accordingly.

## References

- [PythonAnywhere: Deploying an existing Django project](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [PythonAnywhere: Environment variables for web apps](https://help.pythonanywhere.com/pages/EnvironmentVariables/)
- [PythonAnywhere: Django setup and WSGI guidance](https://help.pythonanywhere.com/pages/FollowingTheDjangoTutorial/)
