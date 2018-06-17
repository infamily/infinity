from django import forms

from trade.models import (
    Payment, Reserve
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


class ReserveForm(forms.ModelForm):

    class Meta:
        model = Reserve
        exclude = []
