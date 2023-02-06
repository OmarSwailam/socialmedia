from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from .models import *
from .utils import paginatePosts

def index(request):
    posts = Post.objects.all().order_by("-creation_time").all()
    posts, custom_paginator = paginatePosts(request, posts, 10)

    return render(request, "network/index.html", {
        "post_form": PostForm(),
        "comment_form": CommentForm(),
        "posts": posts,
        "posts_type": "All Posts",
        'custom_paginator': custom_paginator
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if request.GET.get('next') else 'index')
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if  (not username) or (not email) or (not password):
            return render(request, "network/register.html", {
                "message": "You must fill out all fields."
            })

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect(request.GET['next'] if request.GET.get('next') else 'index')
    else:
        return render(request, "network/register.html")


def add_post(request):
    owner = request.user
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = owner
            post.save()
            return redirect(request.GET['next'] if request.GET.get('next') else 'index')


def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(request.GET['next'] if request.GET.get('next') else 'index')

    form = PostForm(instance=post)
    return render(request, "network/editpost.html", {
        "form": form,
        "post": post
    })


def delete_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk=post_id)
        post.delete()
        return redirect(request.GET['next'] if request.GET.get('next') else 'index')



def comment(request, post_id):
    if request.method == "POST":
        owner = request.user
        post = Post.objects.get(pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = owner
            comment.save()
            return redirect(request.GET['next'] if request.GET.get('next') else 'index')

def like(request):
    if request.method == "POST":
        if "post_id" in request.POST:
            post_id = request.POST["post_id"]
            try:
                like = Like.objects.get(user=request.user, post=Post.objects.get(pk=post_id))
            except Like.DoesNotExist:
                new_like = Like(user=request.user, post=Post.objects.get(pk=post_id))
                new_like.save()
            else:
                like.delete()
        elif "comment_id" in request.POST:
            comment_id = request.POST["comment_id"]
            try:
                like = Like.objects.get(user=request.user, comment=Comment.objects.get(pk=comment_id))
            except Like.DoesNotExist:
                new_like = Like(user=request.user, comment=Comment.objects.get(pk=comment_id))
                new_like.save()
            else:
                like.delete()
        return redirect(request.GET['next'] if request.GET.get('next') else 'index')

def profile(request, user_pk):
    user_profile = User.objects.get(pk=user_pk)
    posts = user_profile.user_posts.order_by("-creation_time").all()
    return render(request, "network/profilepage.html", {
        "user_profile": user_profile,
        "user_posts": posts,
        "comment_form": CommentForm()
    })

def follow_unfollow(request, user_pk):
    if request.method == "POST":
        try:
            follow = Follow.objects.get(user_following=request.user.id, user_followed=user_pk)
        except Follow.DoesNotExist:
            try:
                user_to_follow = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponse(status=404)
            else:
                new_follow = Follow(user_following=request.user, user_followed=user_to_follow)
                new_follow.save()
        else:
            follow.delete()

        return redirect(request.GET['next'] if request.GET.get('next') else 'index')


def following(request):
    current_user = User.objects.get(pk=request.user.pk)
    users_posts = [user.get_user_followed_posts() for user in current_user.following.all()]
    posts = [post for user in users_posts for post in user]
    posts, custom_paginator = paginatePosts(request, posts, 10)

    return render(request, "network/index.html", {
        "post_form": PostForm(),
        "comment_form": CommentForm(),
        "posts": posts,
        "posts_type": "Following Posts",
        'custom_paginator': custom_paginator

    })
