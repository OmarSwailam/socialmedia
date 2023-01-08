from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="user_posts")
    content = models.TextField(blank=False)
    image = models.ImageField(null=True, blank=True)
    creation_time = models.DateTimeField(default=datetime.now)

    def __str__(self) -> str:
        return f"{self.user}'s post on {self.creation_time}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    content = models.TextField(blank=False)
    creation_time = models.DateTimeField(default=datetime.now)

    def __str__(self) -> str:
        return f"{self.user}'s comment on post \"{self.post_id}\" on {self.creation_time}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_likes", null=True, blank=True)


class Follow(models.Model):
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def get_user_followed_posts(self):
        return self.user_followed.user_posts.order_by("-creation_time").all()
