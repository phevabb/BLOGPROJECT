from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug',  'author', 'publish', 'status']
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ['author']   # this is used on foreign keys
    ordering = ['status', 'publish']
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'body', 'created', 'active']
    raw_id_fields = ['post']
