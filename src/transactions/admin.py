from django.contrib import admin

from transactions.models import (
    TopicSnapshot,
    CommentSnapshot,
    Currency,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
    Interaction,
    Transaction,
    ContributionCertificate
)


@admin.register(TopicSnapshot)
class TopicSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentSnapshot)
class CommentSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(HourPriceSnapshot)
class HourPriceSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(CurrencyPriceSnapshot)
class CurrencyPriceSnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributionCertificate)
class ContributionCertificateAdmin(admin.ModelAdmin):
    pass
