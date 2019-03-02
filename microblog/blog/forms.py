from django import forms
from .models import Blog, User


class BlogForm(forms.ModelForm):

    user = User()
    content = forms.CharField(widget=forms.TextInput(attrs={"size": 60}))
    photo = forms.ImageField(required=False)

    class Meta:
        model = Blog
        fields = ["user", "content", "photo"]
