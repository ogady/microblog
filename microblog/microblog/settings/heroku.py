from .common import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        # sqlite
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

        # MySQL
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'anicolle',
        # 'USER': 'root',
        # 'PASSWORD': 'password',
        # 'HOST': '*',  # (ローカルホストなら空でも可)
        # 'PORT': '*',  # (デフォルトポートなら空でも可)

    }
}

SECURE_PROXY_SSL_HEADER = {'HTTP_X_FORWARDED_PRONTO', 'http'}

ALLOWED_HOSTS = ["*"]

