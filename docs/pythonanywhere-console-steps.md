# PythonAnywhere console steps

Run these commands in a PythonAnywhere **Bash console**, one block at a time. Do not paste passwords, GitHub tokens, or private SSH keys into chat.

## 1. Cancel the blocked HTTPS clone

If the console currently says `Username for 'https://github.com':`, press **Ctrl+C** first:

```bash
Ctrl+C
rm -rf ~/globalpathways
```

## 2. Create SSH access for GitHub

Check whether a key already exists:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ls -l ~/.ssh/*.pub 2>/dev/null
```

If `~/.ssh/id_ed25519.pub` does not exist, create a key:

```bash
ssh-keygen -t ed25519 -C "globalpathways-pythonanywhere" -f ~/.ssh/id_ed25519
```

When asked for a passphrase, use one if you can manage it securely. Display the public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire one-line output beginning with `ssh-ed25519`. In GitHub, open **Settings → SSH and GPG keys → New SSH key**, name it `PythonAnywhere Global Pathways`, paste the public key, and save it.

Test GitHub authentication:

```bash
ssh -T git@github.com
```

If prompted to trust GitHub's host key, type `yes`. A success message says GitHub authenticated you but does not provide shell access.

## 3. Clone the private repository

```bash
git clone git@github.com:SHINGIRO-link/globalpathways.git ~/globalpathways
cd ~/globalpathways
```

Confirm the code is present:

```bash
ls
ls backend
```

You should see `manage.py`, `config`, `opportunities`, and `requirements.txt` inside `backend`.

## 4. Create and activate the virtual environment

The existing PythonAnywhere Web app uses Python 3.10:

```bash
mkvirtualenv --python=/usr/bin/python3.10 globalpathways-venv
workon globalpathways-venv
python --version
```

If the virtualenv already exists, the `mkvirtualenv` command may report that; continue with:

```bash
workon globalpathways-venv
```

## 5. Install dependencies

```bash
cd ~/globalpathways/backend
pip install -r requirements.txt
```

Confirm Django is available:

```bash
python -m django --version
```

## 6. Create the private environment file

Open the editor:

```bash
nano ~/globalpathways/backend/.env
```

Paste this template and replace every placeholder with your real deployment values:

```text
DJANGO_SECRET_KEY=replace-with-a-long-random-production-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=globalopportunityconnect.pythonanywhere.com
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend-domain.example
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-mailbox@example.com
SMTP_PASSWORD=your-mail-app-password
SMTP_FROM=your-mailbox@example.com
SMTP_STAFF_RECIPIENT=your-staff-recipient@example.com
```

In nano, save with **Ctrl+O**, press **Enter**, then exit with **Ctrl+X**. Protect the file:

```bash
chmod 600 ~/globalpathways/backend/.env
```

Do not commit this file or display it with `cat` after adding secrets.

## 7. Run Django setup commands

```bash
workon globalpathways-venv
cd ~/globalpathways/backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Warnings from `check --deploy` should be reviewed before production. Do not ignore security warnings without understanding them.

## 8. Configure the PythonAnywhere Web tab

Open **Web** in PythonAnywhere and configure the existing app `globalopportunityconnect.pythonanywhere.com`:

```text
Source code: /home/globalopportunityconnect/globalpathways/backend
Working directory: /home/globalopportunityconnect/globalpathways/backend
Virtualenv: /home/globalopportunityconnect/.virtualenvs/globalpathways-venv
```

Open the WSGI file shown by the Web tab, usually `/var/www/globalopportunityconnect_pythonanywhere_com_wsgi.py`, delete its contents, and paste:

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

Save the WSGI file.

## 9. Configure static files

In the Web tab, add this mapping:

```text
URL: /static/
Directory: /home/globalopportunityconnect/globalpathways/backend/staticfiles
```

Then click **Reload** for `globalopportunityconnect.pythonanywhere.com`.

## 10. Verify from the console

```bash
curl -i https://globalopportunityconnect.pythonanywhere.com/api/health/
curl -i https://globalopportunityconnect.pythonanywhere.com/api/opportunities/
```

The responses should be JSON. If you receive a 500 error, open the Web tab's error log and server log.

## 11. Updating later from GitHub

```bash
workon globalpathways-venv
cd ~/globalpathways
git pull origin main
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the PythonAnywhere Web tab.

## Important limitation

These commands deploy the Django API only. The React frontend currently uses `/api` through the Manus Node proxy. If the frontend remains on Manus, the proxy must be configured with the PythonAnywhere API URL. If the frontend is hosted elsewhere, set its build variable to:

```text
VITE_API_BASE_URL=https://globalopportunityconnect.pythonanywhere.com/api
```

Then set the exact frontend origin in `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS`, reload the backend, and test OAuth, uploads, email, guest status links, and staff tools.
