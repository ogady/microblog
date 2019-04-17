from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from blog.models import Blog, Like, Tag
from blog.forms import BlogForm, TagInlineFormSet
import re

User = get_user_model()


class BlogListView(ListView):
    model = Blog
    # レスポンスに込めるobjectの名前を変える
    context_object_name = "blog_list"
    paginate_by = 10


class BlogByTagList(ListView):
    model = Blog
    context_object_name = "blog_list"
    paginate_by = 10
    slug_field = "tag"
    slug_url_kwarg = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = Tag.objects.get_or_none(name=self.kwargs['tag'])

        if not tag:
            messages.error(self.request, str("タグに「" + self.kwargs['tag'] + "」がつく投稿はありません"))
            context['blog_list'] = Blog.objects.all()
            return context

        context['blog_list'] = Blog.objects.filter(tag=tag)
        context['tag'] = tag
        return context


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
                tag = tag.strip()
                if tag != "":
                    exists_tag = Tag.objects.get_or_none(name=tag)

                    if exists_tag:
                        blog.tag.add(exists_tag)
                    else:
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


class BlogByAnimeCreateView(BlogCreateView):
    slug_field = "anime"
    slug_url_kwarg = "anime"

    def get_context_data(self, **kwargs):
        context = super(BlogByAnimeCreateView, self).get_context_data(**kwargs)
        context.update(dict(formset=TagInlineFormSet(self.request.POST or None, instance=self.object)))
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["tag"] = self.kwargs['anime']
        return initial


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

    def get_initial(self):
        initial = super().get_initial()
        tags = self.object.tag.filter(blog=self.kwargs['pk'])
        tag_list = (','.join([str(tag) for tag in tags]))

        initial["tag"] = tag_list
        return initial

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
            tag = tag.strip()
            if tag != "":
                exists_tag = Tag.objects.get_or_none(name=tag)

                if exists_tag:
                    blog.tag.add(exists_tag)
                else:
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


