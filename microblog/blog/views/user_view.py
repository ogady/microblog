from django.shortcuts import redirect
from django.views.generic import DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from blog.models import Blog, UserProfile
from blog.forms import UserCreateForm, LoginForm, UserUpdateForm, ProfileFormSet

User = get_user_model()


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm


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

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()

            formset.save()
            messages.success(self.request, "更新しました。")
            nick_name = form.cleaned_data['nick_name']
            return redirect("profile_detail", nick_name=nick_name)

        else:
            context['form'] = form
            messages.error(self.request, "更新に失敗しました。")
            return self.render_to_response(context)

    def form_invalid(self, form):
        # self.requestオブジェクトに”更新に失敗しました。”を込める
        messages.error(self.request, "更新に失敗しました。")
        return super().form_invalid(form)


class UserDeleteView(LoginRequiredMixin, TemplateView):
    """ユーザー削除"""
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
