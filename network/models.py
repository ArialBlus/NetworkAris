from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    userFollowing = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")


    def __str__(self):
        return f"{self.user} is following {self.userFollowing}"


class Like(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name="like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")

    def __str__(self):
        return f"{self.user} likes {self.post}"
    
    class Meta:
        unique_together = ("user", "post")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postComment")
    content = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="comments/", blank=True, null=True)

    def __str__(self):
        return f"{self.user} commented on {self.post} on {self.date.strftime('%d %b %Y %H:%M:%S')}"