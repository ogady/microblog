from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.http.response import JsonResponse
from .models import Blog, Comment, Like, UserProfile, Tag
from .forms import BlogForm, SearchForm, UserCreateForm, LoginForm, \
    CommentForm, UserUpdateForm, ProfileFormSet, TagInlineFormSet
import requests
import re

User = get_user_model()


# Create your views here.


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm


class BlogListView(ListView):
    model = Blog
    # レスポンスに込めるobjectの名前を変える
    context_object_name = "blog_list"
    paginate_by = 10


class BlogDetailView(DetailView):
    model = Blog

    def get_context_data(self, **kwargs):
        # 継承元のメソッドを呼び出す
        context = super().get_context_data(**kwargs)
        # 記事へのコメントを取得
        context['comment_list'] = self.object.comment_set.filter(parent__isnull=True)
        tags = self.object.tag.filter(blog=kwargs['object'])
        tag_list = []

        for tag in tags:
            tag_list.append(str(tag.name))

        context['tags'] = tag_list
        context['like_cnt'] = Like.objects.filter(post=kwargs['object']).count()
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    # modelのfieldsはformClassに任せる
    model = Blog
    form_class = BlogForm
    # LoginRequiredMixinを使う際は定義する必要あり
    login_url = '/login'

    success_url = reverse_lazy("index")
    # templateをクラス汎用ビューのデフォルトから変える
    template_name = "blog/blog_create_form.html"

    def get_context_data(self, **kwargs):
        context = super(BlogCreateView, self).get_context_data(**kwargs)
        context.update(dict(formset=TagInlineFormSet(self.request.POST or None, instance=self.object)))

        return context

    # バリデート後
    def form_valid(self, form):

        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            tags = self.request.POST.get("tag")
            tag_list = re.split("[,、]", tags)

            blog = form.save(commit=False)
            blog.save()

            for tag in tag_list:
                tag_obj = Tag(name=tag)
                tag_obj.save()
                blog.tag.add(tag_obj)

            messages.success(self.request, "保存しました。")
            return super().form_valid(form)

        else:
            context['form'] = form
            messages.error(self.request, "保存に失敗しました。")
            return self.render_to_response(context)

    def form_invalid(self, form):
        # self.requestオブジェクトに”保存に失敗しました。”を込める
        messages.error(self.request, "保存に失敗しました。")
        return super().form_invalid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm

    login_url = '/login'

    def get_context_data(self, **kwargs):
        context = super(BlogUpdateView, self).get_context_data(**kwargs)
        context.update(dict(formset=TagInlineFormSet(self.request.POST or None, instance=self.object)))
        tags = self.object.tag.filter(**kwargs)
        tag_list = []

        for tag in tags:
            tag_list.append(str(tag.name))

        context['tags'] = tag_list
        return context

    # success_urlを自作する
    def get_success_url(self):
        # <int:pk>はself.kwargsに{"pk": 2（int）}と辞書型にセットされているためpkを取得する
        blog_pk = self.kwargs['pk']

        # 上記同様にreverseする際も{"pk": blog_pk}の辞書型形式でkwargsにセットしてあげる
        url = reverse_lazy("detail", kwargs={"pk": blog_pk})
        return url

    # templateをクラス汎用ビューのデフォルトから変える
    template_name = "blog/blog_update_form.html"

    # バリデート後
    def form_valid(self, form):

        tags = self.request.POST.get("tag")
        tag_list = re.split("[,、]", tags)

        blog = form.save(commit=False)
        blog.save()

        if not tags:
            messages.success(self.request, "更新しました。")
            return super().form_valid(form)

        blog.tag.clear()

        for tag in tag_list:
            tag_obj = Tag(name=tag)
            tag_obj.save()
            blog.tag.add(tag_obj)

        messages.success(self.request, "更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        # self.requestオブジェクトに”更新に失敗しました。”を込める
        messages.error(self.request, "更新に失敗しました。")
        return super().form_invalid(form)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    # LoginRequiredMixinを先に継承しないとエラーになることがある

    model = Blog
    success_url = reverse_lazy("index")

    # LoginRequiredMixinを使う際は定義する必要あり
    login_url = '/login'

    # バリデート後
    def delete(self, request, *args, **kwargs):
        # self.requestオブジェクトに”削除しました。”を込める
        messages.success(self.request, "削除しました。")
        # super()で継承元の処理を返すのがお約束
        return super().delete(request, *args, **kwargs)


# ページネーション機能
def paginate_queryset(request, queryset, count):
    """Pageオブジェクトを返す。"""
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


# アニメ検索機能（関数ビューの知見）
def api_call(request):
    endpoint = 'http://api.moemoe.tokyo/anime/v1/master'

    # リクエストがpostであることをチェック
    if request.method == 'POST':
        # フォームデータを取得
        form = SearchForm(request.POST)
        # フォームのデータが安全かチェック
        if form.is_valid():

            # データを受け取る
            year = form.cleaned_data['year']
            cours = form.cleaned_data['cours']

            if year:
                query = str(year)
                url = endpoint + "/" + query

            else:
                form = SearchForm()
                messages = ["放送年を選択してください"]
                context = {'messages': messages, 'form': form}

                return render(request, 'blog/anime_search.html', context)

            if cours:
                query = str(cours)
                url = url + "/" + query

            response = requests.get(url)
            anime_list = response.json()

            form = SearchForm()

            page_obj = paginate_queryset(request, anime_list, 10)
            context = {
                'anime_list': page_obj.object_list,
                'form': form,
                'year': year,
                'cours': cours,
                'page_obj': page_obj,
            }

            return render(request, 'blog/anime_search.html', context)

        else:
            form = SearchForm()
            messages = ["放送年を選択してください"]

            context = {'messages': messages, 'form': form}

            return render(request, 'blog/anime_search.html', context)
    else:

        # 最初にブラウザから呼び出されるときに使用するフォームクラスを指定
        form = SearchForm()

        # ページネーションバーからGETで遷移したときの処理
        # ページネーションしてきたときはクエリにyear,coursがあるのでそれを判定して分岐に入る
        if 'year' in request.GET:
            year = request.GET.get('year')
            url = endpoint + "/" + year

            cours = request.GET.get('cours')

            if cours:
                cours = request.GET.get('cours')
                url = url + "/" + cours

            response = requests.get(url)
            anime_list = response.json()
            page_obj = paginate_queryset(request, anime_list, 10)

            context = {
                'anime_list': page_obj.object_list,
                'form': form,
                'year': year,
                'cours': cours,
                'page_obj': page_obj,
            }

            return render(request, 'blog/anime_search.html', context)

    # 作成されたフォームオブジェクトをコンテキストへ格納
    context = {'form': form}
    # 最初にブラウザから呼び出されたときに指定テンプレートとコンテキストで描画する
    return render(request, 'blog/anime_search.html', context)


class UserCreate(CreateView):
    """ユーザー登録"""
    model = User
    form_class = UserCreateForm

    def form_valid(self, form):
        """ユーザー登録"""
        # formをテーブルに保存するかを指定するオプション（デフォルト=True）
        user = form.save(commit=True)
        # is_active<-ユーザーアカウントをアクティブにするかどうかを指定,
        # 退会処理も、is_activeをFalseにするという処理がベター。
        user.is_active = True
        user.save()

        return redirect('user_create_done')


class UserCreateDone(TemplateView):
    """ユーザー登録完了"""


class ProfileDetailView(DetailView):
    model = UserProfile
    slug_field = "nick_name"  # モデルのフィールドの名前
    slug_url_kwarg = "nick_name"  # urls.pyでのキーワードの名前

    def get_object(self, queryset=None):
        user_id = User.objects.get(nick_name=self.kwargs['nick_name'])
        return UserProfile.objects.get(user_id=user_id)

    def get_context_data(self, **kwargs):
        # 継承元のメソッドを呼び出す
        user_id = User.objects.get(nick_name=self.kwargs['nick_name'])
        context = super().get_context_data(**kwargs)
        context['blog_list'] = Blog.objects.filter(user=user_id)
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """プロフィール編集"""
    model = User
    form_class = UserUpdateForm
    login_url = '/login'
    template_name = "blog/profile_edit.html"
    slug_field = "nick_name"
    slug_url_kwarg = "nick_name"

    def get_context_data(self, **kwargs):
        context = super(ProfileEditView, self).get_context_data(**kwargs)
        # 子フォームをつくる
        context.update(dict
                       (formset=ProfileFormSet(self.request.POST or None,
                                               files=self.request.FILES or None, instance=self.object)))

        return context

    def get_success_url(self):
        # <int:pk>はself.kwargsに{"pk": 2（int）}と辞書型にセットされているためpkを取得する
        nick_name = self.kwargs['nick_name']
        url = reverse_lazy("profile_detail", kwargs={"nick_name": nick_name})
        return url

    def form_valid(self, form):
        context = self.get_context_data()

        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()

            formset.save()
            messages.success(self.request, "更新しました。")
            return redirect(self.get_success_url())

        else:
            context['form'] = form
            messages.error(self.request, "更新に失敗しました。")
            return self.render_to_response(context)

    def form_invalid(self, form):
        # self.requestオブジェクトに”更新に失敗しました。”を込める
        messages.error(self.request, "更新に失敗しました。")
        return super().form_invalid(form)


class UserDeleteView(LoginRequiredMixin, TemplateView):
    """プロフィール削除"""
    # LoginRequiredMixinを先に継承しないとエラーになることがある
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(nick_name=self.kwargs['nick_name'])

        # is_active<-ユーザーアカウントをアクティブにするかどうかを指定,
        # 退会処理も、is_activeをFalseにするという処理がベター。
        user.is_active = False
        user.save()
        messages.error(self.request, "アカウントを削除しました。")

        return redirect('index')


def comment_create(request, blog_pk):
    """記事へのコメント作成"""
    post = get_object_or_404(Blog, pk=blog_pk)
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return redirect('detail', pk=post.pk)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/comment_form.html', context)


def reply_create(request, comment_pk):
    """コメントへの返信"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    post = comment.post
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        reply = form.save(commit=False)
        reply.parent = comment
        reply.post = post
        reply.save()
        return redirect('detail', pk=post.pk)

    context = {
        'form': form,
        'post': post,
        'comment': comment,
    }
    return render(request, 'blog/comment_form.html', context)


class LikeAddOrDeleteApi(LoginRequiredMixin, View):
    """いいねをするorいいねを解除するAPI"""

    def get(self, request, **kwargs):
        blog = Blog.objects.get(id=kwargs['blog_pk'])
        is_like = Like.objects.filter(user=request.user).filter(post=blog).count()

        # いいねを解除する
        if is_like > 0:
            liking = Like.objects.get(post__id=kwargs['blog_pk'], user=request.user)
            liking.delete()
            blog.like_num -= 1
            blog.save()

            return JsonResponse({"like": blog.like_num})

        # いいねする
        blog.like_num += 1
        blog.save()
        like = Like()
        like.user = request.user
        like.post = blog
        like.save()

        return JsonResponse({"like": blog.like_num})
