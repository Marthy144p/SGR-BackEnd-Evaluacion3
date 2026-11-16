
"""
Configuración del proyecto SGR - Evaluación 2 de Back End.

Django 5.0.x
Base de datos: MySQL
Administración mediante Django Admin.
Despliegue en AWS con HTTPS.
"""

import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get(
    'DJANGO_DEBUG',
    'True'
).lower() in ('true', '1', 'yes')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise RuntimeError(
            'Debes configurar DJANGO_SECRET_KEY para producción.'
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        '127.0.0.1,localhost'
    ).split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'organizacion',
    'actividades',
    'agenda',
    'resultados',
    'gestion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sgr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sgr.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'sgr_db'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),

        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =====================================================
# SEGURIDAD HTTPS PARA PRODUCCIÓN EN AWS
# =====================================================

# Nginx informa a Django cuando una solicitud utiliza HTTPS.
# Esta configuración se utiliza únicamente en producción.
# El proxy debe establecer X-Forwarded-Proto de forma segura.

SECURE_PROXY_SSL_HEADER = (
    ('HTTP_X_FORWARDED_PROTO', 'https')
    if not DEBUG else None
)

# Obliga a utilizar HTTPS en producción.
SECURE_SSL_REDIRECT = not DEBUG

# Protege las cookies de sesión en producción.
SESSION_COOKIE_SECURE = not DEBUG

# Protege las cookies CSRF en producción.
CSRF_COOKIE_SECURE = not DEBUG

# HSTS se mantiene desactivado por el momento.
# AWS Academy Learner Lab puede cambiar la IP pública
# y utiliza un certificado de corta duración.

SECURE_HSTS_SECONDS = 0

# Configuración de la Evaluación 3: autenticación y sesiones
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'login'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# Configurar DJANGO_CSRF_TRUSTED_ORIGINS en producción si se usa host/proxy HTTPS.
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if u.strip()]
