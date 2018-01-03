from django.contrib import admin

from infty.core.models import Topic, Comment
from infty.core.admin.forms import TopicForm, CommentForm


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
