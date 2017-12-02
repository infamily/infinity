from django.contrib import admin

from infty.core.models import *
from infty.core.forms import TopicForm, CommentForm, InstanceForm

# Register your models here.

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Instance)
class InstanceModelAdmin(admin.ModelAdmin):
    form = InstanceForm


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
