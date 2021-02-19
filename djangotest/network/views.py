from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from social.settings import client

from .models import User, Post, UserProfile
from network.forms import PostForm, UserForm, UserProfileForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm



def index(request):
    if request.user.is_authenticated:
        # fetch all available posts in reverse order
        posts = Post.objects.all().order_by("-id")
        # implementing pagination with 2 posts per page
        paginator = Paginator(posts, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form = PostForm()
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.instance.user = request.user
                tumblr_post = client.create_text("digarg", state="published", slug="testing-text-posts", title="Testing", body=form.cleaned_data["body"])
                form.instance.tumblr_post_id = tumblr_post['id_string']
                form.save()
                form = PostForm()
        context = {
            'posts': page_obj, 'form': form
        }
        return render(request, "network/index.html", context)
    else:
        return render(request, "network/index.html")


def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = AuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                # validating user credentials with authenticate method
                user = authenticate(username = username, password = password)
                if user != 'None':
                    login(request, user)
                    return HttpResponseRedirect('/')
        else:
            form = AuthenticationForm()
            return render(request, "network/login.html", {'form':form})
    else:
        return HttpResponseRedirect("/")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    user_form = UserForm()
    profile_form = UserProfileForm()
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST,request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_obj = user_form.save()
            profile_form.save(commit=False)
            profile_form.instance.user = user_obj
            profile_form.save()
            user_form = UserForm()
            messages.success(request, 'Registeration Completed Successfully!!')
    context = {
        'user_form': user_form, 'profile_form': profile_form
    }
    return render(request, "network/register.html", context)


def post_update(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        body = request.POST.get("body")
        obj = Post.objects.get(id=post_id)
        if Post.objects.filter(id=post_id).exists():
            post = Post(id=post_id, body=body, created_at=obj.created_at, user=obj.user, tumblr_post_id=obj.tumblr_post_id)
            post.save()
            post = Post.objects.get(id=post_id)
            data = {'id':post.id, 'body':post.body}
            client.edit_post('digarg',id=int(post.tumblr_post_id), type="text", title="Testing", body=post.body)
            return JsonResponse(data)

    else:
        post_id = request.GET.get("post_id")
        post = Post.objects.get(id=post_id)
        data = {'id':post.id, 'body':post.body}
        return JsonResponse(data)



def profile(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        # fetch authenticated user's all posts
        posts = Post.objects.filter(user=request.user).order_by("-id")
        # implementing pagination with 1 post per page
        paginator = Paginator(posts, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        following_count = User.objects.filter(user_profile__follows = request.user).count()
        return render(request, "network/profile.html", {'user': user, 'posts': page_obj, 'following_count':following_count})
    else:
        return HttpResponseRedirect("/login")


def like_view(request):
    post = get_object_or_404(Post, id=request.GET.get('post_id'))

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    data = {"is_liked":is_liked, 'total':post.total_likes}
    return JsonResponse(data)


def all_post(request):
    posts = Post.objects.all().order_by("-id")
    # implementing pagination with 3 posts per page
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/all_post.html", {'posts': page_obj})


def post_delete(request, pk):
    post = Post.objects.get(id=pk)
    tumblr_id = post.tumblr_post_id
    post.delete()
    client.delete_post('digarg', tumblr_id)
    return HttpResponseRedirect("/profile/")


def profile_update(request, pk):
    obj = User.objects.get(id=pk)
    user_form = UserChangeForm(instance=obj)
    profile_form = UserProfileForm(instance=obj.user_profile)
    if request.method == "POST":
        obj = User.objects.get(id=pk)
        user_form = UserChangeForm(request.POST, instance=obj)
        profile_form = UserProfileForm(request.POST,request.FILES, instance=obj.user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully!!')
    context = {
        'user_form': user_form, 'profile_form': profile_form
    }
    return render(request, "network/profile_update.html", context)


def posted_user_profile(request, pk):
    if request.user.is_authenticated:
        user = User.objects.get(posts__id=pk)
        posts = Post.objects.filter(user = user).order_by("-created_at")
        following_count = User.objects.filter(user_profile__follows = user).count()
        context = {
            'user': user, 'posts':posts, 'following_count':following_count
        }
        return render(request, "network/profile.html", context)
    else:
        return HttpResponseRedirect("/login")


def following_user_posts(request):
    if request.user.is_authenticated:
        following_users = User.objects.filter(user_profile__follows = request.user).values("username")
        posts = []
        for following_user in following_users:
            obj = Post.objects.filter(user__username=following_user['username'])[:1]
            posts.append(obj)
        context = {'posts': posts}
        return render(request, "network/following_user_post.html", context)
    else:
        return HttpResponseRedirect("/login")


def follow_view(request):
    profile_id = request.GET.get("user_profile_id")
    profile = get_object_or_404(UserProfile, id=profile_id)
    is_following = False

    if profile.follows.filter(id=request.user.id).exists():
        profile.follows.remove(request.user)
        is_following = False
    else:
        profile.follows.add(request.user)
        is_following = True
    data = {"is_following": is_following,"profile_id":profile_id, "total_followers":profile.total_followers}
    return JsonResponse(data)
