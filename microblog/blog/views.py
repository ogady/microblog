from django.contrib.messages import success
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Blog
from django.urls import reverse_lazy
from .forms import BlogForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
import json


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
        # self.requestオブジェクトに”保存しました”を込める
        messages.success(self.request, "削除しました。")
        # super()で継承元の処理を返すのがお約束
        return super().delete(request, *args, **kwargs)


def title_call(request):
    if request.POST['title']:
        title = request.POST['title']
        endpoint = 'https://api.animedb.moe/madb/anime/search'
        query = {
            'title': title,
        }

        response = requests.get(endpoint, params=query)
        print("response", response.json())
        return render(request, 'index.html')
