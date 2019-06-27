from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['feed-reader.com']


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rss_reader',
        'USER': 'rss_reader',
        'PASSWORD': 'password',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}
