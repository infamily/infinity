from django.contrib import admin

# Register your models here.
from src.payments.models import (
    Purchase
)


@admin.register(Purchase)
class PaymentAdmin(admin.ModelAdmin):
    pass

