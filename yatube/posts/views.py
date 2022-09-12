from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm
from posts.models import Group, Post
from posts.utils import get_paginator

User = get_user_model()


def index(request):
    """Функция отображения главной страницы."""
    posts = Post.objects.select_related('author').all()
    context = {
        'page_obj': get_paginator(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция отображения постов выбраной группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page = get_paginator(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Функция отображения страницы пользователя."""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    page = get_paginator(request, posts)
    context = {
        'page_obj': page,
        'author': user,
        'post': posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Функция отображения одного поста пользователя."""
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    count_posts = author.posts.all().count()
    context = {
        'post': post,
        'count_posts': count_posts,
        'user': request.user,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция создания нового поста пользователя."""
    form = PostForm(request.POST or None)
    if form.is_valid() and request.method == 'POST':
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=edit_post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': edit_post,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)
