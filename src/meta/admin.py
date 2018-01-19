from django.contrib import admin

from src.meta.models import Type, Instance
from src.meta.forms import TypeForm, InstanceForm


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    form = TypeForm


@admin.register(Instance)
class InstanceModelAdmin(admin.ModelAdmin):
    form = InstanceForm
