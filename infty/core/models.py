# Create your models here.
from django.db import models
from infty.users.models import User

class GenericModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Topic(GenericModel):
    """
    Main content type, to include fields of all types.
    """
    NEED = 0
    GOAL = 1
    IDEA = 2
    PLAN = 3
    STEP = 4
    TASK = 5

    TOPIC_TYPES = [
        (NEED, 'Need'),
        (GOAL, 'Goal'),
        (IDEA, 'Idea'),
        (PLAN, 'Plan'),
        (STEP, 'Step'),
        (TASK, 'Task'),
    ]

    type = models.PositiveSmallIntegerField(TOPIC_TYPES, default=TASK)
    title = models.TextField()
    body = models.TextField(null=True, blank=True)
    editors = models.ManyToManyField(
        User,
        related_name='topic_editors',
        blank=True
    )
    parents = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='parent_items'
    )


class Comment(GenericModel):
    """
    Comments are the place to discuss and claim time and things.
    """

    topic = models.ForeignKey(Topic)
    text = models.TextField()
    claimed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    assumed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)


class CommentSnapshot(GenericModel):
    """
    Whenever comment is changed, or transaction is made,
    we have to store the comment content to permanent storage.
    """
    comment = models.ForeignKey(Comment)
    text = models.TextField()
    claimed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    assumed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)


CURRENCY_TYPES = [
    (0, 'USD'),
    (1, 'EUR'),
    (2, 'CNY'),
    (3, 'RUB'),
    (4, 'JPY'),
    (5, 'INR'),
]

class HourPriceSnapshot(GenericModel):
    """
    Record of hour price used, based the exchange rate at the time of transaction.
    HourPrice needs to be computed every time, immediately before Transaction,
    from two sources:

    1. Hour Price Source

    E.g., if our hour price source is FRED, we would look at:
     hour_price_source = 'https://fred.stlouisfed.org/series/CES0500000003'
     hour_price = 26.25
     hour_price_currency = 'USD'

    2. Currency Exchange Rate Source

    E.g., if our dollar exchange source is European Central Bank:

     currency_exchange_source = 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html'
     target_currency = 'EUR'
     unit_of_target_currency_in_hour_price_currency = 1.1642

    (So, we have:)

     hour_price_in_payment_currency = 26.25 / 1.1642

    """
    hour_price_source = models.TextField()
    hour_price = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    hour_price_currency = models.PositiveSmallIntegerField(CURRENCY_TYPES)

    currency_exchange_source = models.TextField()
    target_currency = models.PositiveSmallIntegerField(CURRENCY_TYPES)
    unit_of_target_currency_in_hour_price_currency = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)


class Transaction(GenericModel):
    """
    Transactions are a way to invest money to claimed time and things.
    """

    comment = models.ForeignKey(Comment)
    snapshot = models.ForeignKey(CommentSnapshot)
    payment_amount = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    payment_currency = models.PositiveSmallIntegerField(CURRENCY_TYPES)
    payment_recipient = models.ForeignKey(User, related_name='recipient')
    payment_sender = models.ForeignKey(User, related_name='sender')

    hour_price_snapshot = models.ForeignKey(HourPriceSnapshot)
    hour_price_in_payment_currency = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)

    donated_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    matched_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)


class ContributionCertificate(GenericModel):
    """
    ContributionCertificates are proofs of co-creation, grounded in
    immutable comment_snapshots and transactions: one doer, one investor.
    """

    transaction = models.ForeignKey(Transaction)
    comment_snapshot = models.ForeignKey(CommentSnapshot)
    matched_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    received_by = models.ForeignKey(User)
