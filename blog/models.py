from dataclasses import fields

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse



from taggit.managers import TaggableManager



# i will define my on manager called published.
# Django has a default manager called. object,
# that is why you mostly see things like, Post.objects.all() etc.
#   by default django's manager 'object' returns instances of a model class.
# but i can create my own manager to return instances of a model class with specific features.
# maybe to return all instances whose status are active..
# i can still achieve that with the default manager, with something like this
#   Post.objects.filter(status=published)
# but creating my own custom manager is far better.





class PublishedManager(models.Manager):
    def get_queryset(self):
        # Whenever we call our manager it will retrieve instances whose status field is 'PB' which is PUBLISHED
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )

# If you declare any custom managers for
# your model, but you want to keep the objects manager as well, you have to add it explicitly to your
# model.

# we include the custom manager and the default manager in the Post model
class Post(models.Model):
    class Status(models.TextChoices): # we will mostly use Post.Status instead of Post.status
        DRAFT = 'DF', 'Draft'  # the human-readable: Draft |value: DF |name: DRAFT ...... WE can access any of the three (name, value, label)... i mean we can do these: Post.Status.DRAFT, Post.Status.DF, Post.Status.Draft
        PUBLISHED = 'PB', 'Published'
        # We will always use PUBLISHED when we code, users will see it as Published and will be saved in the db as PB

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=222)
    body = models.TextField()
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)  # we will mostly use Post.Status instead of Post.status
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'Post_User_ship')
    objects = models.Manager() # default manager
    published = PublishedManager() # custom manager
    tags = TaggableManager()

    class Meta:
        ordering = ['publish']
        indexes = [models.Index(fields=['-publish'])]


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete= models.CASCADE, related_name='comment_post_ship' )
    name = models.CharField(max_length=222)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created']),]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

