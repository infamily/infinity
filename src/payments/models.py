from django.db import models

# Create your models here.
from src.users.models import User
from src.generic.models import GenericModel
from django.contrib.postgres.fields import JSONField


class GenericPayment(GenericModel):
    processor = models.PositiveSmallIntegerField(default=1)

    class Meta:
        abstract = True


class Purchase(GenericPayment):
    """
    Defines a purchase of infinity hours by a user
    from the managing organization, that runs
    the infinity server, as a credit institution.

    The purchased hours are going to be added to
    the daily limit of the user who purchased it.

    The purchased hours are treated as an extra
    reserve in addition to the daily credit limit

    The user can use the extra hours anytime, when
    daily limit is not enough.

    When this extra reserve is used up,
    the user remains to have just daily limit.
    """
    hours = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False
    )
    hour_price = models.ForeignKey(
        'transactions.HourPriceSnapshot',
        related_name='hour_prices',
        blank=False
    )
    currency_price = models.ForeignKey(
        'transactions.CurrencyPriceSnapshot',
        related_name='currency_prices',
        blank=False
    )

    user = models.ForeignKey(
        User,
        related_name='users',
        blank=False
    )
    currency = models.ForeignKey(
        'transactions.Currency',
        related_name='currencies',
        blank=False
    )

    amount = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False
    )
    platform = models.CharField(
        max_length=20,
        default='stripe'
    )
    provider = models.CharField(
        max_length=20,
        default='card'
    )
    reqeust = JSONField()
    response = JSONField()
