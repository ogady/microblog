from django import forms
from .models import Blog
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class BlogForm(forms.ModelForm):
    """投稿フォーム"""
    user = User
    content = forms.CharField(label='つぶやき', widget=forms.TextInput(attrs={"size": 60}))
    photo = forms.ImageField(label='画像', required=False)

    class Meta:
        model = Blog
        fields = ["user", "content", "photo"]


class SearchForm(forms.Form):
    """アニメ検索フォーム"""
    choice = (
        ('', '選択肢から選んでください'),
        ('1', '春'),
        ('2', '夏'),
        ('3', '秋'),
        ('4', '冬'),
    )

    year = forms.IntegerField(label='放送年', required=True
                              , widget=forms.TextInput(attrs={"size": 50, 'placeholder': '2018'}))
    cours = forms.ChoiceField(label='クール', widget=forms.Select, choices=choice, required=False,)

    class Meta:
        fields = ["year", "cours"]


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User

        if User.USERNAME_FIELD == 'email':
            fields = ['email', 'nick_name']
        else:
            fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
