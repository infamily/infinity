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

            resp = stripe.Charge.create(**instance.request)

            if resp.paid:
                instance.paid = True
            elif not resp.paid:
                instance.paid = False

            instance.response = resp.to_dict()


            if Currency.objects.filter(label=resp.currency.upper()).exists():

                currency = Currency.objects.get(label=resp.currency.upper())

                # Normalize currencies based on Strip minimum currency units:
                if currency.label in Currency.objects.all().values_list('label', flat=True):
                    amount = resp.amount/100.
                else:
                    amount = resp.amount

                # Compute the amount of hours bought
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
            # payment: instance.needs_manual_review = True
