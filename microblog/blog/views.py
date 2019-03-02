from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import Blog, User
from django.urls import reverse_lazy
from .forms import BlogForm, SearchForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import requests


# Create your views here.


class BlogListView(ListView):
    model = Blog
    # レスポンスに込めるobjectの名前を変える
    context_object_name = "blog_list"
    paginate_by = 10


class BlogDetailView(DetailView):
    model = Blog


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    print("form_class")
    form_class = BlogForm

    # LoginRequiredMixinを使う際は定義する必要あり
    login_url = '/login'

    # fieldsはformClassに任せる
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

    # fieldsはformClassに任せる

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


# アニメ検索機能
def api_call(request):

    # リクエストがpostであることをチェック
    if request.method == 'POST':
        # フォームデータを取得
        form = SearchForm(request.POST)
        # フォームのデータが安全かチェック
        if form.is_valid():

            # データを受け取る
            year = form.cleaned_data['year']
            cours = form.cleaned_data['cours']

            if year & year <= 9999:
                query = str(year)
                endpoint = 'http://api.moemoe.tokyo/anime/v1/master'
                url = endpoint + "/" + query

            else:
                form = SearchForm()
                messages = ["放送年は4桁の数字で入力してください"]
                context = {'messages': messages, 'form': form}

                return render(request, 'blog/anime_search.html', context)

            if cours:
                query = str(cours)
                url = url + "/" + query

            response = requests.get(url)
            anime_list = response.json()

            form = SearchForm()

            context = {'anime_list': anime_list, 'form' : form}

            return render(request, 'blog/anime_search.html', context)

        else:
            form = SearchForm()
            messages = ["放送年は4桁の数字で入力してください"]
            context = {'messages': messages, 'form': form}

            return render(request, 'blog/anime_search.html', context)
    else:
        """
        動作順序①
        """
        # 最初にブラウザから呼び出されるときに使用するフォームクラスを指定
        form = SearchForm()
    """
    動作順序②
    """
    # 作成されたフォームオブジェクトをコンテキストへ格納
    context = {'form': form}
    # 最初にブラウザから呼び出されたときに指定テンプレートとコンテキストで描画する
    return render(request, 'blog/anime_search.html', context)
