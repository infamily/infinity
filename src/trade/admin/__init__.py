from django.contrib import admin

from src.trade.models import Payment, Reserve
from src.trade.admin.forms import PaymentForm, ReserveForm


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm

@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    form = ReserveForm
