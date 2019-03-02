"""microblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog.views import BlogListView, BlogDetailView, BlogCreateView,BlogUpdateView, BlogDeleteView
from django.contrib.auth.views import LoginView, LogoutView
from blog import views

# 画像UL用
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('<URL>', views関数, ニックネーム(任意)),
    path('admin/', admin.site.urls),
    path('', BlogListView.as_view(), name="index"),

    # 受け取ったintをpkに代入する
    path('<int:pk>', BlogDetailView.as_view(), name="detail"),
    path('create', BlogCreateView.as_view(), name="create"),
    path('<int:pk>/update', BlogUpdateView.as_view(), name="update"),
    path('<int:pk>/delete', BlogDeleteView.as_view(), name="delete"),

    # defaultだとregistration/loginを探しにいくので、template_nameで指定する。
    path('login', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='logout.html'), name='logout'),

    # API呼び出し用viewとのルーティング
    path('search', views.api_call, name='search'),
]

# 画像UL用
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
