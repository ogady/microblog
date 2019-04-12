from django.test import TestCase
from microblog.blog import models
from microblog.blog import forms
# Create your tests here.


class BlogModelTest(TestCase):

    def test_valid(self):
        """正常な入力を行えばエラーにならないことを検証"""
        params = dict(content="test", photo="", anime_id="", anime="", tag="tag,tag、tag", user=1)
        blog = models.Blog()
        form = forms.BlogForm(params, instance=blog)
        self.assertTrue(form.is_valid())

    def test_either1(self):
        """何も入力しなければエラーになることを検証"""
        params = dict()
        blog = models.Blog()
        form = forms.BlogForm(params, instance=blog)
        self.assertFalse(form.is_valid())


class CommentModelTest(TestCase):

    def test_valid(self):
        """正常な入力を行えばエラーにならないことを検証"""
        params = dict(comment="test", post=1)
        comment = models.Comment()
        form = forms.CommentForm(params, instance=comment)
        self.assertTrue(form.is_valid())

    def test_either1(self):
        """何も入力しなければエラーになることを検証"""
        params = dict()
        blog = models.Comment()
        form = forms.CommentForm(params, instance=blog)
        self.assertFalse(form.is_valid())



