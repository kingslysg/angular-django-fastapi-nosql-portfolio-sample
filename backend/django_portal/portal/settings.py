from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'demo-only-change-before-deployment'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
INSTALLED_APPS = ['django.contrib.contenttypes', 'rest_framework', 'portal_api']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]
ROOT_URLCONF = 'portal.urls'
TEMPLATES = []
WSGI_APPLICATION = 'portal.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer']}
