from django.contrib import admin
from django import forms

from infty.core.models import *

# Register your models here.

class TopicForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=Topic.TOPIC_TYPES,
        initial=Topic.IDEA
    )

    class Meta:
        model = Topic
        exclude = []


class TopicModelAdmin(admin.ModelAdmin):
    form = TopicForm


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentSnapshot)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(HourPriceSnapshot)
class HourPriceSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributionCertificate)
class ContributionCertificateAdmin(admin.ModelAdmin):
    pass

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass

@admin.register(CurrencyPriceSnapshot)
class CurrencyPriceSnapshotAdmin(admin.ModelAdmin):
    pass
