from django.contrib import admin

from infty.core.models import *
from infty.core.forms import TopicForm

# Register your models here.

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
