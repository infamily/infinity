from django.contrib import admin

from infty.meta.models import Type, Instance
from infty.meta.admin.forms import TypeForm, InstanceForm


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    form = TypeForm


@admin.register(Instance)
class InstanceModelAdmin(admin.ModelAdmin):
    form = InstanceForm
