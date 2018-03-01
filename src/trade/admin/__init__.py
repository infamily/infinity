from django.contrib import admin

from src.trade.models import Payment, ReservePurchase, ReserveExpense
from src.trade.admin.forms import PaymentForm, ReservePurchaseForm, ReserveExpenseForm


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm


@admin.register(ReservePurchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = ReservePurchaseForm


@admin.register(ReserveExpense)
class PurchaseAdmin(admin.ModelAdmin):
    form = ReserveExpenseForm

