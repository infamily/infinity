import stripe
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.dispatch import receiver

from src.trade.models import Payment, Reserve
from src.transactions.models import Currency

@receiver(models.signals.post_save, sender=Payment)
def payment_post_save(sender, instance, created, *args, **kwargs):

    if instance.request:

        # Testing
        if (instance.platform == instance.TESTING) and \
           (instance.provider == instance.TEST):

            instance.response = instance.request

            if instance.request.get('amount') and \
                instance.request.get('currency'):

                if Currency.objects.filter(label=instance.response['currency'].upper()).exists():

                    currency = Currency.objects.get(label=instance.response['currency'].upper())
                    amount = instance.request['amount']
                    purchase = Decimal(amount) * currency.in_hours()

                    Reserve.objects.create(
                        payment=instance,
                        user=instance.owner,
                        hours=purchase,
                        hour_price=currency.hour_price(),
                        currency_price=currency.currency_price(),
                        is_test=True
                    )

        # Stripe
        if (instance.platform == instance.STRIPE) and \
           (instance.provider == instance.CARD):

            if settings.STRIPE_LIVE_MODE == 'True':
                stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
                IS_TEST = False
            else:
                stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
                IS_TEST = True

            client = stripe.http_client.RequestsClient()
            stripe.set_app_info(
                settings.OWNER_ORGANIZATION_NAME,
                version="latest",
                url=settings.ALLOWED_HOSTS
            )

            if 'card' in instance.request.keys():
                token = stripe.Token.create(
                  card=instance.request['card'],
                )
                instance.request.update({'card': token.id})

            currency_label = instance.request.get('currency')
            currency_amount = instance.request.get('amount')

            # Assume that amount is sent in dollars, and we need to convert it to cents.
            if currency_label.upper() in Currency.objects.all().values_list('label', flat=True):
                currency_amount = int(float(currency_amount) * 100.)
                instance.request.update({'amount': currency_amount})

            resp = stripe.Charge.create(**instance.request)

            if resp.paid:
                instance.paid = True
            elif not resp.paid:
                instance.paid = False

            instance.response = resp.to_dict()


            # Assume that amount is in cents, and we need to convert it to dollars.
            if Currency.objects.filter(label=resp.currency.upper()).exists():

                amount = resp.amount / 100.

                # Compute the amount of hours bought
                currency = Currency.objects.get(label=resp.currency.upper())
                purchase = Decimal(amount) * currency.in_hours()

                Reserve.objects.create(
                    payment=instance,
                    user=instance.owner,
                    hours=purchase,
                    hour_price=currency.hour_price(),
                    currency_price=currency.currency_price(),
                    is_test=IS_TEST
                )
            else:
                pass
            # No associated reserve change recorded.
            # payment: instance.needs_manual_review.
