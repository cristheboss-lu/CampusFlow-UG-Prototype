"""
Django settings for config project - Render Production Ready
"""

from pathlib import Path
import os
import dj_database_url
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!y)9ou^1oahibb7bb=dohnlx6#%qgj=pbbg1guw(u^7nv3=n8j'

# Para desarrollo True, en Render lo pondremos en False automático
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'plataforma',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===== DATABASE =====
# Usa PostgreSQL en Render, SQLite en desarrollo local
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# ===== STATIC FILES =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'plataforma' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===== CLOUDINARY =====
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD", ""),
    api_key=os.environ.get("CLOUDINARY_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_SECRET", "")
)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ===== EMAIL =====
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===== UNFOLD ADMIN INTERFACE =====
UNFOLD = {
    "SITE_HEADER": "Universidad de Guayaquil",
    "SITE_TITLE": "Portal Administrativo",
    "INDEX_TITLE": "Bienvenido al Sistema de Gestión Académica",
    "SITE_ICON": lambda request: "https://via.placeholder.com/32",
    "THEME": "dark",
    "COLORS": {
        "primary": {
            "50": "#f0f9ff",
            "100": "#e0f2fe",
            "200": "#bae6fd",
            "300": "#7dd3fc",
            "400": "#38bdf8",
            "500": "#0ea5e9",
            "600": "#0284c7",
            "700": "#0369a1",
            "800": "#075985",
            "900": "#0c3d66",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_navigation": True,
        "navigation_expand_all": False,
        "show_home_icon": True,
    },
    "TABS": {
        "default": {
            "permission": lambda request: request.user.is_staff,
        },
    },
}

# ===== DEFAULT PRIMARY KEY =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
