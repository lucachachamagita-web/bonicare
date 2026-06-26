"""
Django settings for myHospital project.
"""

import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY', 'o!3$!vwqgdmd9+1#b^b((br!n$$rx5nhj7=n_=zaf1h7wx7#li')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1']
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://bonicare-clinic.up.railway.app',
    'https://*.up.railway.app',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'case.apps.CaseConfig',
    'appointments.apps.AppointmentsConfig',
    'reports.apps.ReportsConfig',
    'stock.apps.StockConfig',
    'bill.apps.BillConfig',
    'profiles.apps.ProfilesConfig',
    'home.apps.HomeConfig',
    'loginmodule.apps.LoginmoduleConfig',
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

ROOT_URLCONF = 'myHospital.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.role_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'myHospital.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:32578737Sm.@localhost:5432/myhospital',
        conn_max_age=600,
        ssl_require=False
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGIN_URL = '/login/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# M-Pesa API Integration Config (Replace with your Daraja app credentials)
MPESA_CONSUMER_KEY = 'xG7fGxZ8A7GZ9X5m7gG7wGA7dGZ7GA7A'
MPESA_CONSUMER_SECRET = 'yG7fGxZ8A7GZ9X5m'
MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_CALLBACK_URL = 'https://sandbox.safaricom.co.ke/mpesa/'
