from decimal import Decimal

from django.db import models
from django.db.models import Sum

# Create your models here.
from src.users.models import User
from src.generic.models import GenericModel
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _


class Payment(GenericModel):
    TESTING = 0
    STRIPE = 1
    BRAINTREE = 2
    PAYPAL = 3

    PLATFORMS = [
        (TESTING, _('Testing')),
        (STRIPE, _('Stripe')),
        (BRAINTREE, _('Braintree')),
        (PAYPAL, _('Paypal'))
    ]

    TEST = 0
    CARD = 1
    SEPA = 2
    ALIPAY = 3
    WECHAT = 4
    AMEX = 5
    GIROPAY = 6
    SOFORT = 7

    PROVIDERS = [
        (TEST, _('Test')),
        (CARD, _('Card')),
        (SEPA, _('SEPA Direct Debit')),
        (ALIPAY, _('Alipay')),
        (WECHAT, _('WeChat')),
        (AMEX, _('Amex Express Checkout')),
        (GIROPAY, _('Giropay')),
        (SOFORT, _('SOFORT')),
    ]

    platform = models.PositiveSmallIntegerField(
        PLATFORMS, default=STRIPE)
    provider = models.PositiveSmallIntegerField(
        PROVIDERS, default=CARD
    )
    paid = models.NullBooleanField(
        default=None
    )

    request = JSONField()
    response = JSONField(blank=True, null=True)

    owner = models.ForeignKey(
        User,
        related_name='user_payments',
        blank=False,
        null=False
    )

    def __str__(self):
        PROVIDER = None
        for provider in self.PROVIDERS:
            if provider[0] == self.provider:
                PROVIDER = provider[1]
        PLATFORM = None
        for platform in self.PLATFORMS:
            if platform[0] == self.platform:
                PLATFORM = platform[1]
        return "[{}] {} ({}) payment by {}".format(
            self.created_date,
            PLATFORM, PROVIDER, self.owner.username)


class Reserve(GenericModel):
    """
    Defines a purchase and expenses of infinity hours credit
    reserve by a user from the managing organization, that runs
    an infinity server, as a credit institution.

    1. If it is a purchase of infinity hours, then payment__not=None.

    And the filled out fields are:
        payment
        hours (+) (positive)
        hour_price,
        currency_price,
        currency,
        amount
        user

    2. If it is an expense of infinity hours, then transaction__not=None.

    And the filled out fields are:
        transaction
        hours (-) (negative)
        user

    The reserve is used (2.), if the daily credit balance is insufficient
    to cover the investment (exceeds the daily limit of free credit).

    The purchased hours are going to be added to the daily limit of
    the user who purchased it. The purchased hours reserve is treated
    as an extra reserve in addition to the daily credit limit

    The user can use the extra hours anytime, when daily limit is not
    enough. When this extra reserve is used up, the user remains to
    have just daily limit.

    The below fields define the number of hours
    purchased by the user with given payment
    at the price of hour_price and currency_price.
    """

    hours = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
        null=False
    )

    user = models.ForeignKey(
        User,
        related_name='buyer',
        blank=False,
        null=False
    )

    payment = models.ForeignKey(
        Payment,
        blank=True,
        null=True,
        unique=True
    )

    hour_price = models.ForeignKey(
        'transactions.HourPriceSnapshot',
        related_name='hour_prices',
        blank=True,
        null=True
    )
    currency_price = models.ForeignKey(
        'transactions.CurrencyPriceSnapshot',
        related_name='currency_prices',
        blank=True,
        null=True
    )

    '''
    These below facts are derived from the
    details of the Payment model's fields.
    '''

    currency = models.ForeignKey(
        'transactions.Currency',
        related_name='currencies',
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=True,
        null=True
    )

    transaction = models.ForeignKey(
        'transactions.Transaction',
        related_name='transactions',
        blank=True,
        null=True,
        unique=True,
    )

    #TODO: Later remove with better tests
    is_test = models.BooleanField(
        default=True
    )

    @classmethod
    def user_purchased(cls, user):
        """
        Returns amount of reserve hours that a given user has accumulated.
        """
        return Decimal(
            cls.objects.filter(
                user=user, payment__isnull=False).aggregate(total=Sum('hours')).get('total')
            or 0)

    @classmethod
    def user_expended(cls, user):
        """
        Returns amount of reserve hours that a given user has expended.
        """
        return Decimal(
            cls.objects.filter(
                user=user, transaction__isnull=False).aggregate(total=Sum('hours')).get('total')
            or 0)

    @classmethod
    def user_reserve_remains(cls, user):
        return Reserve.user_purchased(user) + Reserve.user_expended(user)
