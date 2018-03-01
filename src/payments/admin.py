from django.contrib import admin

# Register your models here.
from src.payments.models import (
    Payment, Purchase
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass

@admin.register(Purchase)
class PaymentAdmin(admin.ModelAdmin):
    pass

