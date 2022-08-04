# posts/views.py
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


POSTS_PER_PAGE: int = 10


def get_paginator(request, posts):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    template_index = 'posts/index.html'
    posts_list = Post.objects.all()
    page_obj = get_paginator(request, posts_list)
    context = {
        'posts': posts_list,
        'page_obj': page_obj,
    }
    return render(request=request,
                  template_name=template_index,
                  context=context)


def group_posts(request, slug):
    template_group_posts = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_paginator(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request=request,
                  template_name=template_group_posts,
                  context=context)


def profile(request, username):
    template_profile = 'posts/profile.html'
    text = 'Профайл пользователя'
    author = get_object_or_404(User, username=username)
    following = (request.user.is_authenticated
                 and request.user.follower.filter(author=author).exists())
    posts_list = author.posts.all()
    page_obj = get_paginator(request, posts_list)
    context = {
        'text': text,
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request=request,
                  template_name=template_profile,
                  context=context)


def post_detail(request, post_id):
    template_post = 'posts/post_detail.html'
    post_obj = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post_obj.comments.all()
    context = {
        'post': post_obj,
        'form': form,
        'comments': comments,
    }
    return render(request=request,
                  template_name=template_post,
                  context=context)


@login_required
def post_create(request):
    template_post_create = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'form': form,
        'is_new': True
    }
    if not form.is_valid():
        return render(request=request,
                      template_name=template_post_create,
                      context=context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile',
                    username=request.user.username)


@login_required
def post_edit(request, post_id):
    template_post_edit = 'posts/create_post.html'
    post = get_object_or_404(Post,
                             id=post_id)
    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )
        context = {
            'form': form,
            'post_id': post_id,
            'is_new': False
        }
        if not form.is_valid():
            return render(request=request,
                          template_name=template_post_edit,
                          context=context)
        form.save()
    return redirect('posts:post_detail',
                    post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
        'posts:post_detail',
        post_id=post_id,
    )


@login_required
def follow_index(request):
    template_follow = 'posts/follow.html'
    title_text = 'Публикации избранных авторов'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, posts_list)
    context = {
        'title_text': title_text,
        'posts': posts_list,
        'page_obj': page_obj,
    }
    return render(
        request,
        template_follow,
        context
    )


@login_required
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    follow_exist = request.user.follower.filter(author=follow_author).exists()
    if follow_author != request.user and not follow_exist:
        Follow.objects.create(
            user=request.user,
            author=follow_author
        )
    return redirect('posts:profile',
                    username)


@login_required
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author=follow_author)
    if data_follow.exists():
        data_follow.delete()
    return redirect('posts:profile',
                    username)
