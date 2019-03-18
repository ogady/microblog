from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .models import Blog, Comment
from .forms import BlogForm, SearchForm, UserCreateForm, LoginForm, CommentForm
import requests

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
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    # modelのfieldsはformClassに任せる
    model = Blog

    form_class = BlogForm
    print(BlogForm)
    # LoginRequiredMixinを使う際は定義する必要あり
    login_url = '/login'

    success_url = reverse_lazy("index")
    # templateをクラス汎用ビューのデフォルトから変える
    template_name = "blog/blog_create_form.html"

    # バリデート後
    def form_valid(self, form):
        # self.requestオブジェクトに”保存しました”を込める
        messages.success(self.request, "保存しました。")
        # super()で継承元の処理を返すのがお約束
        return super().form_valid(form)

    def form_invalid(self, form):
        # self.requestオブジェクトに”保存に失敗しました。”を込める
        messages.error(self.request, "保存に失敗しました。")
        return super().form_invalid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm

    # LoginRequiredMixinを使う際は定義する必要あり
    login_url = '/login'

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
        # self.requestオブジェクトに”更新しました。”を込める
        messages.success(self.request, "更新しました。")
        # super()で継承元の処理を返すのがお約束
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


# アニメ検索機能
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
        """
        動作順序①
        """
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

    """
    動作順序②
    """
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


def comment_create(request, post_pk):
    """記事へのコメント作成"""
    post = get_object_or_404(Blog, pk=post_pk)
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
