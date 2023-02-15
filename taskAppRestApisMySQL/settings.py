"""
Django settings for taskAppRestApisMySQL project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$l+-eud+50$j2zihhx$g51d(jg1buzcy=03ld#426ov!t=ce5x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'first',
    'rest_framework',
    'rest_framework.authtoken',
    'taskApp.apps.TaskappConfig',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8081',
    'https://testapp-ef6a8.web.app',
    'http://testapp-ef6a8.web.app ',
    'https://checkcheckgoose.com'
]

CORS_ORIGIN_WHITELIST = (
    'http://localhost:8081',
    'https://testapp-ef6a8.web.app',
    'http://testapp-ef6a8.web.app ',
    'https://checkcheckgoose.com'
)

ROOT_URLCONF = 'taskAppRestApisMySQL.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'taskAppRestApisMySQL.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'task_app_mgr',
        'ENGINE': 'mysql.connector.django',
        'USER': 'root',
        'PASSWORD': '12345',
        'OPTIONS': {
          'autocommit': True,
        },
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'zachburau@gmail.com'
EMAIL_HOST_PASSWORD = 'lnhjeeiqrhgttpcb'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# ANYMAIL = {
#     # (exact settings here depend on your ESP...)
#     "MAILGUN_API_KEY": "pubkey-b2e7bff8b93ed3daf705b8b1f2e39d72",
#     "MAILGUN_SENDER_DOMAIN": 'sandboxf7236d805396401daf8616c2cd32efa3.mailgun.org',  # your Mailgun domain, if needed
# }
# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"  # or sendgrid.EmailBackend, or...
# DEFAULT_FROM_EMAIL = "bigmlpiter@gmail.com"  # if you don't already have this in settings
# SERVER_EMAIL = "bigmlpiter@gmail.com"  # ditto (default from-email for Django errors)
#
MAILGUN_API_KEY = 'f616b7845db5f1ad4bdb4f9a6613c499-4534758e-678cb1b9'
MAILGUN_API_BASE_URL = 'https://api.mailgun.net/v3/sandboxf7236d805396401daf8616c2cd32efa3.mailgun.org/messages'

