from pathlib import Path
import os
from dotenv import load_dotenv

# BASE DIRS
SETTINGS_DIR = Path(__file__).resolve().parent
BASE_DIR = SETTINGS_DIR.parent
ROOT_DIR = BASE_DIR.parent  # Sube un nivel hasta PharmStockRepo

# Carga el .env desde PharmStockRepo/.env
dotenv_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path)

print("✅ ENV loaded from:", dotenv_path)
print("DB_NAME:", os.getenv("DB_NAME"))

# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS") else []

# ==========================
# APPS
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'django_htmx',
    'stock',
]

# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'pharmstock_app.urls'

# ==========================
# TEMPLATES
# ==========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'pharmstock_app.wsgi.application'

# ==========================
# DATABASES
# ==========================
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME', '').strip(),
        'HOST': os.getenv('DB_HOST', '').strip(),
        'PORT': os.getenv('DB_PORT', '1433').strip(),
        'USER': os.getenv('DB_USER', '').strip(),
        'PASSWORD': os.getenv('DB_PASSWORD', '').strip(),
        'OPTIONS': {
            'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server').strip(),
            'extra_params': os.getenv('DB_EXTRA', 'TrustServerCertificate=yes;MARS_Connection=Yes;').strip(),
        },
    },
    'auth': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'auth_users.sqlite3',
    },
}

DATABASE_ROUTERS = ['stock.db_router.AuthRouter']

# ==========================
# AUTH
# ==========================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ==========================
# LANGUAGE / TIMEZONE
# ==========================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "America/Argentina/Cordoba")
USE_I18N = True
USE_TZ = True

# ==========================
# PASSWORD VALIDATORS
# ==========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================
# STATIC FILES
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ==========================
# DEFAULTS
# ==========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
