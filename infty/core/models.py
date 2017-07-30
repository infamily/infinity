# Create your models here.
from re import finditer
from decimal import Decimal

from django.db import models
from infty.users.models import User
from django.contrib.postgres.fields import JSONField

from django.db.models import Sum

class GenericModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Thing(GenericModel):
    """
    F: Things are references to anything with respect to which we
    will formulate goals. To be implemented in blockchain db.
    """
    ASSET = 0
    AGENT = 1
    PLACE = 2
    EVENT = 3
    TOPIC = 4

    THING_TYPES = [
        (ASSET, 'Asset'),
        (AGENT, 'Agent'),
        (PLACE, 'Place'),
        (EVENT, 'Event'),
        (TOPIC, 'Topic'),
    ]

    type = models.PositiveSmallIntegerField(THING_TYPES, default=TOPIC)


class Topic(GenericModel):
    """
    Y: Main content type, to include fields of all infty types.

    Note: 'STEP' is missing intentionally. 'TASK' and 'STEP' are
    redundant, and in the choice, which one to get rid of, 'STEP'
    made more sense to remove, because people have theories of HTN
    (hierarchical task networks), and 'TASK' is understood as 'STEP'
    by AI planning community. Also 'TASK' is much more tangible thing
    to start with for people. We'll introduce the fields of 'STEP'
    (e.g., planning I/O, https://github.com/wefindx/StepIO) later.
    """
    NEED = 0
    GOAL = 1
    IDEA = 2
    PLAN = 3
    TASK = 4

    TOPIC_TYPES = [
        (NEED, 'Need'),
        (GOAL, 'Goal'),
        (IDEA, 'Idea'),
        (PLAN, 'Plan'),
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
    X: Comments are the place to discuss and claim time and things.

    Note: the reason why we need a separate model for Comment,
    is because comments should not have multiple editors.
    """

    topic = models.ForeignKey(Topic)
    text = models.TextField()

    claimed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    assumed_hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)

    owner = models.ForeignKey(User)

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

    def create_snapshot(self):

        snapshot = CommentSnapshot(
            comment=self,
            text=self.text,
            claimed_hours=self.claimed_hours,
            assumed_hours=self.assumed_hours,
            owner=self.owner
        )

        snapshot.save()

        return snapshot

    def remains(self):
        return (
            self.claimed_hours + self.assumed_hours - \
            ContributionCertificate.objects.filter(
                comment_snapshot__comment=self).aggregate(
                    total=Sum('matched_hours')
                         )['total']
        )

    def invest(self, hour_amount, payment_currency_label):

        amount = min(Decimal(hour_amount), self.remains())

        currency = Currency.objects.get(
            label=payment_currency_label.upper()
        )

        value = currency.in_hours(objects=True)

        to_pay = amount / value['in_hours']



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


HOUR_PRICE_SOURCES = {
    'FRED': 'https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json'
}

CURRENCY_PRICE_SOURCES = {
    'FIXER': 'https://api.fixer.io/latest?base=eur'
}


class Currency(GenericModel):
    """
    Currency labels, e.g. 'EUR', 'CNY', 'USD'.
    """
    label = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        """
        Save in upper case.
        """
        self.label = self.label.upper()
        super(Currency, self).save(*args, **kwargs)

    def in_hours(self,
                 hour_price_obj=None,
                 currency_price_obj=None,
                 hour_price_source='FRED',
                 currency_price_source='FIXER',
                 objects=False):
        """
        Compute the value of currency in hours.
        """

        if not hour_price_obj:
            hour_price_obj = HourPriceSnapshot.objects.filter(
                name=hour_price_source,
            ).last()

        if not currency_price_obj:
            currency_price_obj = CurrencyPriceSnapshot.objects.filter(
                name=currency_price_source
            ).last()

        if hour_price_obj.name =='FRED' and \
            currency_price_obj.name=='FIXER':


            rates = currency_price_obj.data['rates']
            rates[currency_price_obj.base.label] = 1.

            price = Decimal(hour_price_obj.data['observations'][0]['value'])
            hour_base_rate = Decimal(rates[hour_price_obj.base.label])
            local_base_rate = Decimal(rates[self.label])

            value = Decimal(1)/((price/hour_base_rate)*local_base_rate)

            if objects:
                return {
                    "in_hours": value,
                    "hour_price_snapshot": hour_price_obj,
                    "currency_price_snapshot": currency_price_obj
                }

            return value


class HourPriceSnapshot(GenericModel):
    """
    We need average price of human labor.

    Example:

    name = 'FRED'
    base = 'USD'
    endpoint = 'https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json'
    """
    name = models.CharField(max_length=10)
    base = models.ForeignKey(Currency)

    endpoint = models.TextField()
    data = JSONField()


class CurrencyPriceSnapshot(GenericModel):
    """
    We need the prices of currencies.

    Example:

    name = 'FIXER'
    base = 'EUR'
    endpoint = 'https://api.fixer.io/latest?base=hur'
    """
    name = models.CharField(max_length=10)
    base = models.ForeignKey(Currency)

    endpoint = models.TextField()
    data = JSONField()


class Transaction(GenericModel):
    """
    Transactions are a way to invest money to claimed time and things.
    """

    comment = models.ForeignKey(Comment)
    snapshot = models.ForeignKey(CommentSnapshot)
    hour_price = models.ForeignKey(HourPriceSnapshot)
    currency_price = models.ForeignKey(CurrencyPriceSnapshot)

    payment_amount = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    payment_currency = models.ForeignKey(Currency)
    payment_recipient = models.ForeignKey(User, related_name='recipient')
    payment_sender = models.ForeignKey(User, related_name='sender')
    hour_unit_cost = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)

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
        self.donated_hours = self.payment_amount/self.hour_unit_cost
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
