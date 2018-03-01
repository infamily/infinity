from decimal import Decimal
from django.db import models
from django.db.models import Sum

# Create your models here.
from src.users.models import User
from src.generic.models import GenericModel
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _


class Payment(GenericModel):
    STRIPE = 0
    BRAINTREE = 1
    PAYPAL = 2

    PLATFORMS = [
        (STRIPE, _('Stripe')),
        (BRAINTREE, _('Braintree')),
        (PAYPAL, _('Paypal'))
    ]

    CARD = 0
    SEPA = 1
    ALIPAY = 2
    WECHAT = 3
    AMEX = 4
    GIROPAY = 5
    SOFORT = 6

    PROVIDERS = [
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
    success = models.BooleanField(
        default=False
    )

    request = JSONField()
    response = JSONField()

    @classmethod
    def user_reserve_remains(cls, user):
        return ReservePurchase.user_purchased(user) - ReserveExpense.user_expended(user)


class ReservePurchase(GenericModel):
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

    '''
    The below fields define the number of hours
    purchased by the user with given payment
    at the price of hour_price and currency_price.
    '''

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
        null=True
    )

    hour_price = models.ForeignKey(
        'transactions.HourPriceSnapshot',
        related_name='hour_prices',
        blank=False,
        null=False
    )
    currency_price = models.ForeignKey(
        'transactions.CurrencyPriceSnapshot',
        related_name='currency_prices',
        blank=False,
        null=False
    )

    '''
    These below facts are derived from the
    details of the Payment model's fields.
    '''

    currency = models.ForeignKey(
        'transactions.Currency',
        related_name='currencies',
        blank=False,
        null=False
    )

    amount = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20
    )

    @classmethod
    def user_purchased(cls, user):
        """
        Returns amount of reserve hours that a given user has accumulated.
        """
        return Decimal(
            cls.objects.filter(
                user=user).aggregate(total=Sum('hours')).get('total')
            or 0)


class ReserveExpense(GenericModel):
    """
    Defines an expense of Infinity hours by a user
    to invest into works on Infinity.

    The expended hours are going to be subtracted
    from the daily credit balance, if the purchase
    that day exceeds the daily free limit.
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
        related_name='spender',
        blank=False,
        null=False
    )

    @classmethod
    def user_expended(cls, user):
        """
        Returns amount of reserve hours that a given user has expended.
        """
        return Decimal(
            cls.objects.filter(
                user=user).aggregate(total=Sum('hours')).get('total')
            or 0)
