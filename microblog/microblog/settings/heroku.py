from .common import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {'default'}

SECURE_PROXY_SSL_HEADER = {'HTTP_X_FORWARDED_PRONTO', 'http'}

ALLOWED_HOSTS = ["*"]

