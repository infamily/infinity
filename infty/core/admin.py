from django.contrib import admin
from infty.core.models import *

# Register your models here.

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass


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