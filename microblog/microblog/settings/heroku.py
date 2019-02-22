import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = { 'HTTP_X_FORWAREDED_PRONTO', 'http'}

ALLOWED_HOSTS = ["*"]

