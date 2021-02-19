
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("edit/", views.post_update, name="update"),
    path("profile/", views.profile, name="profile"),
    path("posts/", views.all_post, name="all_post"),
    path('like/', views.like_view, name='like'),
    path("delete/<int:pk>/", views.post_delete, name="delete"),
    path("profile/<int:pk>/", views.profile_update, name="update_profile"),
    path("<int:pk>/", views.posted_user_profile, name="posted_user_profile"),
    path("follow/", views.follow_view, name="follow"),
    path('following/', views.following_user_posts, name="following_user_posts"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
