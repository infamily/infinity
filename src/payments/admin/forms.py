from django import forms

from src.payments.models import Payment, Purchase


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


class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        exclude = []
