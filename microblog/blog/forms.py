from django import forms
from .models import Blog, User


class BlogForm(forms.ModelForm):

    user = User()
    content = forms.CharField(label='つぶやき', widget=forms.TextInput(attrs={"size": 60}))
    photo = forms.ImageField(label='画像', required=False)

    class Meta:
        model = Blog
        fields = ["user", "content", "photo"]


class SearchForm(forms.Form):

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