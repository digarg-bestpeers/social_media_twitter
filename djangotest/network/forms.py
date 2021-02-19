from django import forms
from network.models import Post, User, UserProfile
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
  '''create form for Post'''
  class Meta:
    model = Post
    fields = ['body']
    labels = {'body': 'New Post'}
    widgets = {'body': forms.TextInput(attrs = {'class': 'form-control'})}

class UserForm(UserCreationForm):
  '''create form for User'''
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'username']


class UserProfileForm(forms.ModelForm):
  '''create form for UserProfile which is mapped with User'''
  class Meta:
    model = UserProfile
    fields = ['image']
    widgets = {'image': forms.FileInput()}


class UserChangeForm(forms.ModelForm):
  '''create form to change User profile'''
  class Meta:
    model = User
    fields = ['email', 'username','first_name', 'last_name']
    widgets = {
      'username':forms.TextInput(attrs={'readonly':True}),
      'email': forms.TextInput(attrs={'readonly':True})
      }
