"""
Django settings for eduwiki project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# from __future__ import unicode_literals

import os

from mongoengine import connect


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


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
    'gunicorn',
    'autoassess',
    'exlabel',
)

MIDDLEWARE_CLASSES = (
    'eduwiki.ProfileMiddleware.ProfileMiddleware',
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


MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        # TODO:: session['tree'] does not work if ENGINE is dummy.
        # Fix this and set dummy.
        'ENGINE': 'django.db.backends.dummy',
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': DATABASE_PATH,
    }
}

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'
AUTH_USER_MODEL = 'mongo_auth.MongoUser'
#
SESSION_ENGINE = 'mongoengine.django.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'

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
STATIC_ROOT = '/var/www/eduwiki/static'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Used by the authentication system for all the applications.
# URL to use if the authentication system requires a user to log in.
LOGIN_URL = '/accounts/login/'
# Default URL to redirect to after a user logs in.
LOGIN_REDIRECT_URL = '/'
# REGISTER_REDIRECT_URL = '/accounts/activate/'


MONGODB_HOST = 'localhost'
MONGODB_USER = 'eduwiki'
MONGODB_PWD = 'eduwiki_2015-qi-guo'

connect('eduwiki_db', host=MONGODB_HOST)

# Following is added to for SSL
# # Web SSL PWD = "SSLcrowdTutor2015"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True