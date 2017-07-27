# Create your models here.
from re import finditer
from decimal import Decimal

from django.db import models
from infty.users.models import User
from django.contrib.postgres.fields import JSONField


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
    owner = models.ForeignKey(User)
    editors = models.ManyToManyField(
        User,
        related_name='topic_editors',
        blank=True
    )
    parents = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='parent_topics'
    )


class Comment(GenericModel):
    """
    Comments are the place to discuss and claim time and things.
    """

    topic = models.ForeignKey(Topic)
    text = models.TextField()
    claimed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    assumed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    owner = models.ForeignKey(User)
    parents = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='parent_comments'
    )

    def save(self, *args, **kwargs):
        """
        Save comment created date to parent object.
        """
        self.set_hours()
        super(Comment, self).save(*args, **kwargs)

    def set_hours(self):

        self.claimed_hours = Decimal(0.0)
        self.assumed_hours = Decimal(0.0)

        for m in finditer('\{([^}]+)\}', self.text):
            token = m.group(1)
            if token:
                if token[0] == '?':
                    try:
                        hours = float(token[1:])
                        self.assumed_hours += Decimal(hours)
                        print(self.assumed_hours)
                    except:
                        pass
                else:
                    try:
                        hours = float(token)
                        self.claimed_hours += Decimal(hours)
                        print(self.claimed_hours)
                    except:
                        pass


class CommentSnapshot(GenericModel):
    """
    Whenever comment is changed, or transaction is made,
    we have to store the comment content to permanent storage.
    """
    comment = models.ForeignKey(Comment)
    text = models.TextField()
    claimed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    assumed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    owner = models.ForeignKey(User)


CURRENCY_TYPES = [
    (0, 'HUR'), # Human Hour as Currency (backed by registered assets)
    (1, 'EUR'), # European Euro
    (2, 'USD'), # United States Dollar
    (3, 'CNY'), # Chinese Yuan
    (4, 'RUB'), # Russian Rouble
    (5, 'JPY'), # Japanese Yen
    (6, 'INR'), # Indian Ruppie
]

CURRENCY_IDS = dict([(C[-1], C[0]) for C in CURRENCY_TYPES])


class HourPriceSerie(GenericModel):
    """
    We need average price of human labor.

    Example:

    name = 'FRED'
    endpoint = 'https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json'

    """
    name = models.TextField()
    endpoint = models.TextField()
    data = JSONField()


class CurrencyPriceSerie(GenericModel):
    """
    We need the prices of currencies.

    Example:
    name = 'FIXER'
    endpoint = 'https://api.fixer.io/latest?base=hur'
    The base 'hur' to be comupted in overloaded .save() method.
    """
    name = models.TextField()
    endpoint = models.TextField()
    data = JSONField()


class HourPriceSnapshot(GenericModel):
    """
    Record of hour price used, based the exchange rate at the time of transaction.
    """

    price = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    currency = models.PositiveSmallIntegerField(CURRENCY_TYPES, default=1)

    hour_price = models.ForeignKey(HourPriceSerie)
    currency_price = models.ForeignKey(CurrencyPriceSerie)


class Transaction(GenericModel):
    """
    Transactions are a way to invest money to claimed time and things.
    """

    comment = models.ForeignKey(Comment)
    snapshot = models.ForeignKey(CommentSnapshot)
    payment_amount = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    payment_currency = models.PositiveSmallIntegerField(CURRENCY_TYPES, default=1)
    payment_recipient = models.ForeignKey(User, related_name='recipient')
    payment_sender = models.ForeignKey(User, related_name='sender')

    hour_price_snapshot = models.ForeignKey(HourPriceSnapshot)
    hour_price_in_payment_currency = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)

    donated_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    matched_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)

    def save(self, *args, **kwargs):
        """
        Save comment created date to parent object.
        """
        self.set_hours()
        super(Transaction, self).save(*args, **kwargs)
        self.create_contribution_certificates()

    def set_hours(self):
        self.donated_hours = self.payment_amount/self.hour_price_in_payment_currency
        self.matched_hours = min(self.snapshot.claimed_hours, self.donated_hours)

    def create_contribution_certificates(self):

        DOER = 0
        INVESTOR = 1

        doer_cert = ContributionCertificate(
            type=DOER,
            transaction=self,
            comment_snapshot=self.snapshot,
            matched_hours=self.matched_hours/Decimal(2.),
            received_by=self.payment_recipient,
        )
        doer_cert.save()
        investor_cert = ContributionCertificate(
            type=INVESTOR,
            transaction=self,
            comment_snapshot=self.snapshot,
            matched_hours=self.matched_hours/Decimal(2.),
            received_by=self.payment_sender,
        )
        investor_cert.save()



class ContributionCertificate(GenericModel):
    """
    ContributionCertificates are proofs of co-creation, grounded in
    immutable comment_snapshots and transactions: one doer, one investor.
    """
    DOER = 0
    INVESTOR = 1

    CERTIFICATE_TYPES = [
        (DOER, 'DOER'),
        (INVESTOR, 'INVESTOR'),
    ]

    type = models.PositiveSmallIntegerField(CERTIFICATE_TYPES, default=DOER)
    transaction = models.ForeignKey(Transaction)
    comment_snapshot = models.ForeignKey(CommentSnapshot)
    matched_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    received_by = models.ForeignKey(User)
