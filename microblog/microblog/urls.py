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
from django.contrib.auth.views import LogoutView
from blog import views

# 画像UL用
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('<URL>', views関数, ニックネーム(任意)),
    path('admin/', admin.site.urls),
    path('', views.BlogListView.as_view(), name="index"),

    # 受け取ったintをpkに代入する
    path('<int:pk>', views.BlogDetailView.as_view(), name="detail"),
    path('create', views.BlogCreateView.as_view(), name="create"),
    path('<int:pk>/update', views.BlogUpdateView.as_view(), name="update"),
    path('<int:pk>/delete', views.BlogDeleteView.as_view(), name="delete"),

    # defaultだとregistration/loginを探しにいくので、template_nameで指定する。
    path('login', views.Login.as_view(template_name='login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='logout.html'), name='logout'),

    # API呼び出し用viewとのルーティング
    path('search', views.api_call, name='search'),

    # ユーザー登録機能とのルーティング
    path('user_create/', views.UserCreate.as_view(template_name='user_create.html'), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(template_name='user_create_done.html'),
         name='user_create_done'),

    # リプライ機能とのルーティング
    path('comment/<int:blog_pk>/', views.comment_create, name='comment_create'),
    path('reply/<int:comment_pk>/', views.reply_create, name='reply_create'),

    # いいね機能APIとのルーティング
    path("api/like/<int:blog_pk>/", views.LikeAddOrDeleteApi.as_view(), name="api_like"),

    # プロフィールとのルーティング
    path("<str:nick_name>/profile/", views.ProfileDetailView.as_view(template_name="blog/profile_detail.html")
         , name="profile_detail"),

    # プロフィール編集とのルーティング
    path("<str:nick_name>/edit_profile/", views.ProfileEditView.as_view(template_name="blog/profile_edit.html")
         , name="profile_edit"),

    # ユーザー削除とのルーティング
    path("<str:nick_name>/user_delete/", views.UserDeleteView.as_view(), name="user_delete"),
]

# 画像UL用
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
