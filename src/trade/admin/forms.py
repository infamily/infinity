from django import forms

from src.trade.models import (
    Payment, ReservePurchase, ReserveExpense
)


class PaymentForm(forms.ModelForm):

    platform = forms.ChoiceField(
        choices=Payment.PLATFORMS,
        initial=Payment.STRIPE
    )

    provider = forms.ChoiceField(
        choices=Payment.PROVIDERS,
        initial=Payment.CARD
    )

    class Meta:
        model = Payment
        exclude = []


class ReservePurchaseForm(forms.ModelForm):

    class Meta:
        model = ReservePurchase
        exclude = []


class ReserveExpenseForm(forms.ModelForm):

    class Meta:
        model = ReserveExpense
        exclude = []
