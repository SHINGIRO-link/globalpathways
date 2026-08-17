# PythonAnywhere deployment notes

PythonAnywhere's official guidance for an existing Django project requires cloning the code, creating a Python virtual environment, installing requirements, creating a Web app with Manual Configuration, configuring the PythonAnywhere WSGI file to import the Django project, running migrations, and configuring static files. The PythonAnywhere WSGI file is separate from the project's internal `wsgi.py` file.

The Django app must use the PythonAnywhere hostname in `ALLOWED_HOSTS`, and environment variables used by the web worker must be loaded in the WSGI file or otherwise configured for the web app. PythonAnywhere's documentation recommends a virtual environment and notes that SQLite is the simplest supported database for a small deployment, while production static files should be configured explicitly.

For Global Pathways, the React frontend and Node same-origin proxy are separate from the Django backend. Deploying only `backend/` to PythonAnywhere will provide the API, not the existing React application or its proxy routes. A compatible deployment therefore needs either the existing Manus frontend/proxy to point to the PythonAnywhere API, or a separate frontend host plus CORS, upload-storage, OAuth callback, and email configuration.

References:

1. https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/ — Deploying an existing Django project on PythonAnywhere.
2. https://help.pythonanywhere.com/pages/EnvironmentVariables/ — PythonAnywhere web-app environment variables.
3. https://help.pythonanywhere.com/pages/FollowingTheDjangoTutorial/ — PythonAnywhere Django setup, WSGI, host, and static guidance.
