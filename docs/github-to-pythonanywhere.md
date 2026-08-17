# GitHub to PythonAnywhere: Global Pathways deployment

This procedure deploys the **Django API backend** from the private GitHub repository. The existing React frontend and Node/Express proxy are separate services. Deploying the backend alone does not publish the React website.

## Important security action first

The GitHub password previously shared in chat must be changed immediately. Do not enter it into PythonAnywhere, send it in chat, or commit it to GitHub. Use an SSH key or a GitHub fine-grained token instead. SSH is recommended.

## Part 1: Prepare GitHub access from PythonAnywhere

Open a PythonAnywhere Bash console.

Cancel any HTTPS clone that is asking for a username:

```bash
Ctrl+C
rm -rf ~/globalpathways
```

Check for an existing public SSH key:

```bash
ls -l ~/.ssh/*.pub 2>/dev/null
```

If a public key exists, display it:

```bash
cat ~/.ssh/id_ed25519.pub
```

If no key exists, create one. Accept the default path. For the passphrase, use one if you can safely unlock it in PythonAnywhere; otherwise follow PythonAnywhere's account security guidance:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "globalpathways-pythonanywhere" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

Copy only the single line beginning with `ssh-ed25519`. In GitHub, open **Settings → SSH and GPG keys → New SSH key**, give it a name such as `PythonAnywhere Global Pathways`, paste the public key, and save it. Never upload or share `~/.ssh/id_ed25519` without `.pub`; that is the private key.

Test the connection from PythonAnywhere:

```bash
ssh -T git@github.com
```

A successful test normally says that GitHub does not provide shell access but authentication succeeded. Then clone the private repository:

```bash
git clone git@github.com:SHINGIRO-link/globalpathways.git ~/globalpathways
cd ~/globalpathways
```

If SSH is impossible, create a GitHub fine-grained token with the minimum repository Contents read permission, use it only when prompted for the HTTPS clone, and do not save it in shell history. SSH is safer for repeated deployments.

## Part 2: Create the Python virtual environment

The existing PythonAnywhere account uses Python 3.10. Use the same version for the virtual environment and Web app:

```bash
mkvirtualenv --python=/usr/bin/python3.10 globalpathways-venv
workon globalpathways-venv
cd ~/globalpathways/backend
pip install -r requirements.txt
```

The requirements include Django, Django REST Framework, CORS headers, and `python-dotenv`.

## Part 3: Create a private production environment file

Create a private file that is not committed to Git:

```bash
nano ~/globalpathways/backend/.env
```

Use values appropriate for the PythonAnywhere hostname and the final frontend origin:

```text
DJANGO_SECRET_KEY=replace-with-a-long-random-production-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=globalopportunityconnect.pythonanywhere.com
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend-origin.example
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend-origin.example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-mailbox@example.com
SMTP_PASSWORD=your-mail-app-password
SMTP_FROM=your-mailbox@example.com
SMTP_STAFF_RECIPIENT=your-staff-recipient@example.com
```

Use the exact public frontend origin, including `https://` and no trailing path. If the frontend remains hosted on Manus, use its exact Manus domain. Do not use `CORS_ALLOW_ALL_ORIGINS` in production. The project enables that only when `DJANGO_DEBUG=true`.

Protect the file:

```bash
chmod 600 ~/globalpathways/backend/.env
```

## Part 4: Create the PythonAnywhere Web app

In PythonAnywhere, open **Web → Add a new web app**. Choose **Manual Configuration**, not the automatic Django option, and select Python 3.10.

For the existing app at `globalopportunityconnect.pythonanywhere.com`, set:

| Setting | Value |
|---|---|
| Source code | `/home/globalopportunityconnect/globalpathways/backend` |
| Working directory | `/home/globalopportunityconnect/globalpathways/backend` |
| Virtualenv | `/home/globalopportunityconnect/.virtualenvs/globalpathways-venv` |

Open the PythonAnywhere WSGI file shown in the Web tab, typically:

```text
/var/www/globalopportunityconnect_pythonanywhere_com_wsgi.py
```

Replace its contents with:

```python
import os
import sys
from pathlib import Path

project_path = Path.home() / "globalpathways" / "backend"
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

from dotenv import load_dotenv
load_dotenv(project_path / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Save the WSGI file. Do not use `runserver` as the public server on PythonAnywhere; the Web tab's WSGI process serves the site.

## Part 5: Run migrations, collect static files, and check deployment

In the PythonAnywhere Bash console:

```bash
workon globalpathways-venv
cd ~/globalpathways/backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

For the current project, SQLite is used by default. It is acceptable for a small initial deployment, but use a managed production database before significant traffic or concurrent staff operations.

In the PythonAnywhere Web tab, add or update the static mapping:

| URL | Directory |
|---|---|
| `/static/` | `/home/globalopportunityconnect/globalpathways/backend/staticfiles` |

Uploaded documents are not automatically safe to serve from a local media directory in this architecture. The application currently expects the configured Manus storage/proxy behavior; confirm storage integration before accepting real documents on PythonAnywhere.

## Part 6: Reload and test the backend

Click **Reload** for `globalopportunityconnect.pythonanywhere.com` in the Web tab.

Then test:

```bash
curl -i https://globalopportunityconnect.pythonanywhere.com/api/health/
curl -i https://globalopportunityconnect.pythonanywhere.com/api/opportunities/
```

Expected results are a JSON health response and a JSON opportunity-list response. If either fails, inspect the Web tab's error log and server log.

Test these application flows before directing users to the site:

1. Opportunity listing and detail pages.
2. Public application submission without an account.
3. Private guest status link and optional claim flow.
4. Email delivery to the applicant and staff recipient.
5. Document upload and staff document download.
6. Staff authorization, status updates, CSV export, and ZIP export.
7. OAuth login and automatic role-based dashboard routing.

## Part 7: Connect the React frontend

The React API client uses `VITE_API_BASE_URL`, defaulting to `/api` for the existing Manus same-origin proxy. If the frontend is hosted separately and should call PythonAnywhere directly, build it with:

```text
VITE_API_BASE_URL=https://globalopportunityconnect.pythonanywhere.com/api
```

The PythonAnywhere API must then allow the exact frontend origin through `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS`. The existing Node proxy also forwards Manus session identity headers; direct PythonAnywhere hosting will require an equivalent authentication integration or a deliberate change to the login architecture. Do not assume the existing Manus OAuth/session flow works automatically on a separate host.

## Part 8: Updating after future GitHub changes

From a PythonAnywhere Bash console:

```bash
workon globalpathways-venv
cd ~/globalpathways
git pull origin main
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the PythonAnywhere Web tab. Review logs after every reload.

## References

- [PythonAnywhere: Deploying an existing Django project](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [PythonAnywhere: Environment variables for web apps](https://help.pythonanywhere.com/pages/EnvironmentVariables/)
- [PythonAnywhere: Django setup and WSGI guidance](https://help.pythonanywhere.com/pages/FollowingTheDjangoTutorial/)
