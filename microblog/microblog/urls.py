from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from blog.views import blog_view, blog_option_view, user_view, anime_search_view

# 画像UL用
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('<URL>', views関数, ニックネーム(任意)),
    path('admin/', admin.site.urls),
    path('', blog_view.BlogListView.as_view(), name="index"),
    path('tag/<str:tag>', blog_view.BlogByTagList.as_view(), name="tag_seach"),

    # 受け取ったintをpkに代入する
    path('<int:pk>', blog_view.BlogDetailView.as_view(), name="detail"),
    path('create', blog_view.BlogCreateView.as_view(), name="create"),
    path('create_by_anime/<str:anime>', blog_view.BlogByAnimeCreateView.as_view(), name="create_by_anime"),
    path('<int:pk>/update', blog_view.BlogUpdateView.as_view(), name="update"),
    path('<int:pk>/delete', blog_view.BlogDeleteView.as_view(), name="delete"),

    # defaultだとregistration/loginを探しにいくので、template_nameで指定する。
    path('login', user_view.Login.as_view(template_name='login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='logout.html'), name='logout'),

    # Shangrila API呼び出し用viewとのルーティング
    path('search', anime_search_view.api_call, name='search'),

    # ユーザー登録機能とのルーティング
    path('user_create/', user_view.UserCreate.as_view(template_name='user_create.html'), name='user_create'),
    path('user_create/done', user_view.UserCreateDone.as_view(template_name='user_create_done.html'),
         name='user_create_done'),

    # コメント機能とのルーティング
    path('comment/<int:blog_pk>/', blog_option_view.comment_create, name='comment_create'),
    path('reply/<int:comment_pk>/', blog_option_view.reply_create, name='reply_create'),

    # いいね機能APIとのルーティング
    path("api/like/<int:blog_pk>/", blog_option_view.LikeAddOrDeleteApi.as_view(), name="api_like"),

    # プロフィールとのルーティング
    path("<str:nick_name>/profile/", user_view.ProfileDetailView.as_view(template_name="blog/profile_detail.html")
         , name="profile_detail"),

    # プロフィール編集とのルーティング
    path("<str:nick_name>/edit_profile/", user_view.ProfileEditView.as_view(template_name="blog/profile_edit.html")
         , name="profile_edit"),

    # ユーザー削除とのルーティング
    path("<str:nick_name>/user_delete/", user_view.UserDeleteView.as_view(), name="user_delete"),
]

# 画像UL用
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
