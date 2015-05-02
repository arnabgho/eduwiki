"""
Django settings for eduwiki project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from mongoengine import connect

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# TODO::remove this after removing the "cache"
PROJECT_PATH = os.path.abspath(BASE_DIR)
TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
DATABASE_PATH = os.path.join(PROJECT_PATH, 'eduwiki.db')
STATIC_PATH = os.path.join(PROJECT_PATH, 'static')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's(al*l$-tvbbdzlpddhf(e^*a@s2k$t)b8qf^m8u2p)g-yj3ez'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'mongoengine.django.mongo_auth',
    'mongonaut',
    'sslserver',

    'question_generation',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eduwiki.urls'

WSGI_APPLICATION = 'eduwiki.wsgi.application'

TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        # TODO:: session['tree'] does not work if ENGINE is dummy.
        # Fix this and set dummy.
        # 'ENGINE': 'django.db.backends.dummy',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/crowdTutor/static'

STATICFILES_DIRS = (
    STATIC_PATH,
)

MONGODB_HOST = 'localhost'
MONGODB_USER = 'eduwiki'
MONGODB_PWD = 'eduwiki_2015-qi-guo'

connect('eduwiki_db', host=MONGODB_HOST)

# Following is added to for SSL
# # Web SSL PWD = "SSLeduwiki2015"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True