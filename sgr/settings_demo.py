"""Solo para demostraciones locales aisladas. Nunca seleccionar en AWS."""
import os
import secrets
from .settings import *  # noqa
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or secrets.token_urlsafe(50)
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.environ.get('SGR_DEMO_DB', str(BASE_DIR / 'demo_local.sqlite3'))}}
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
