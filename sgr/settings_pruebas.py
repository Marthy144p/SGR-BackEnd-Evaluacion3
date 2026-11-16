"""Configuración aislada para ejecutar tests, sin conectarse a MySQL/AWS.

python manage.py test --settings=sgr.settings_pruebas
No usar esta configuración al desplegar la aplicación.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
SECRET_KEY = 'clave-solo-para-pruebas-locales-no-utilizar-en-produccion'
DEBUG = True
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
