"""
Configuración de Django para el proyecto config - Listo para Render
"""

from pathlib import Path
import os
import dj_database_url
import cloudinary

# Construir rutas dentro del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ADVERTENCIA DE SEGURIDAD: mantén la SECRET_KEY en secreto
SECRET_KEY = 'django-insecure-!y)9ou^1oahibb7bb=dohnlx6#%qgj=pbbg1guw(u^7nv3=n8j'

# Para desarrollo True, en Render se pone en False automáticamente
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Definición de aplicaciones
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

# ===== BASE DE DATOS =====
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
    # Desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===== VALIDACIÓN DE CONTRASEÑAS =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ===== INTERNACIONALIZACIÓN =====
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# ===== ARCHIVOS ESTÁTICOS =====
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

# ===== CORREO ELECTRÓNICO =====
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===== INTERFAZ ADMIN UNFOLD =====
UNFOLD = {
    "SITE_HEADER": "Universidad de Guayaquil",
    "SITE_TITLE": "Portal Administrativo",
    "INDEX_TITLE": "Sistema de Gestión Académica",
}

# ===== LLAVE PRIMARIA POR DEFECTO =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
