from django.contrib import admin

from trade.models import Payment, Reserve
from trade.forms import PaymentForm, ReserveForm


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm

@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    form = ReserveForm

