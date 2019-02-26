"""
WSGI config for microblog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import threading
import requests
import time

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microblog.settings')

application = get_wsgi_application()


# スリープ防止：デプロイしたWebサーバー自体が自分にアクセス
def awake():
    while True:
        try:
            print("Start Awaking")
            requests.get("https://anicolleblog.herokuapp.com/")
            print("End")
        except:
            print("error")
        time.sleep(300)


t = threading.Thread(target=awake)
t.start()
