from django.contrib import admin

from src.core.models import Topic, Comment
from src.core.admin.forms import TopicForm, CommentForm


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
