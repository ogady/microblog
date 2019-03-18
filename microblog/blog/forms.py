from django import forms
from .models import Blog,  Comment
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class BlogForm(forms.ModelForm):
    """投稿フォーム"""
    user = User
    content = forms.CharField(label='つぶやき', widget=forms.Textarea)
    photo = forms.ImageField(label='画像', required=False)
    anime = forms.CharField(label='アニメタイトル', required=False)
    anime_id = forms.IntegerField(label='アニメID', required=False)

    class Meta:
        model = Blog
        fields = ["user", "content", "photo", "anime_id", "anime"]


class CommentForm(forms.ModelForm):
    """コメントフォーム"""
    comment = Comment
    content = forms.CharField(label='コメント', widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ["content"]


class SearchForm(forms.Form):
    """アニメ検索フォーム"""

    years = [('', '選択肢から選ぶ')]
    years_cnt = 2014

    while years_cnt <= 2030:

        years.append((years_cnt, years_cnt))
        years_cnt = years_cnt + 1

    years_choice = years

    choice = (
        ('', '選択肢から選ぶ'),
        ('1', '春'),
        ('2', '夏'),
        ('3', '秋'),
        ('4', '冬'),
    )

    # year = forms.IntegerField(label='放送年', required=True
    #                           , widget=forms.TextInput(attrs={"size": 50, 'placeholder': '2018'}))
    year = forms.ChoiceField(label='放送年', widget=forms.Select, choices=years_choice, required=False, )
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
