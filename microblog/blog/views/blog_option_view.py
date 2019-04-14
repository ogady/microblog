from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from blog.models import Blog, Comment, Like
from blog.forms import CommentForm

User = get_user_model()


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


def comment_create(request, blog_pk):
    """記事へのコメント作成"""
    post = get_object_or_404(Blog, pk=blog_pk)
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


class LikeAddOrDeleteApi(LoginRequiredMixin, View):
    """いいねをするorいいねを解除するAPI"""

    def get(self, request, **kwargs):
        blog = Blog.objects.get(id=kwargs['blog_pk'])
        is_like = Like.objects.filter(user=request.user).filter(post=blog).count()

        # いいねを解除する
        if is_like > 0:
            liking = Like.objects.get(post__id=kwargs['blog_pk'], user=request.user)
            liking.delete()
            blog.like_num -= 1
            blog.save()

            return JsonResponse({"like": blog.like_num})

        # いいねする
        blog.like_num += 1
        blog.save()
        like = Like()
        like.user = request.user
        like.post = blog
        like.save()

        return JsonResponse({"like": blog.like_num})