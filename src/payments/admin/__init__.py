from django.contrib import admin

from src.payments.models import Payment, Purchase
from src.payments.admin.forms import PaymentForm, PurchaseForm


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm

