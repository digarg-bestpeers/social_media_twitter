from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    @property
    def full_name(self):
      return "{} {}".format(self.first_name, self.last_name)

    @property
    def total_posts_per_user (self):
      return self.posts.count()


class Post(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True)
  body = models.TextField()
  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now = True)
  likes = models.ManyToManyField(User, related_name='post_likes')
  tumblr_post_id = models.CharField(max_length=255, null=True)

  @property
  def total_likes(self):
    return self.likes.count()

  def __str__(self):
    return self.body


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
  image = models.ImageField(upload_to='images/', max_length=255, blank=True)
  follows = models.ManyToManyField(User, related_name="following")

  @property
  def total_followers(self):
    return self.follows.count()


