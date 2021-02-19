from django.contrib import admin
from network.models import User, Post, UserProfile
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(UserProfile)
