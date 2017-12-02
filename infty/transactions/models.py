from django.db import models

from django.contrib.postgres.fields import JSONField

import json
import bigchaindb_driver
from re import finditer
from decimal import Decimal


bdb = bigchaindb_driver.BigchainDB(
    settings.IPDB_API_ROOT,
    headers={
        'app_id': settings.IPDB_APP_ID,
        'app_key': settings.IPDB_APP_KEY
    }
)

def blockchain_save(user, data, blockchain=False):

    if blockchain in dict(CryptoKeypair.KEY_TYPES).keys():

        cryptokey_qs = CryptoKeypair.objects.filter(
            user=user,
            type=blockchain,
            private_key__isnull=False
        )

        if not cryptokey_qs.exists():
            keypair = CryptoKeypair.make_one(user=user)
            keypair.save()
        else:
            keypair = cryptokey_qs.last()

        tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=keypair.public_key,
            asset={'data': data},
        )

        signed_tx = bdb.transactions.fulfill(
            tx,
            private_keys=keypair.private_key
        )

        sent_tx = bdb.transactions.send(signed_tx)

        txid = sent_tx['id']

        # Try 100 times till completion.
        trials = 0

        while trials < 100:
            try:
                if bdb.transactions.status(txid).get('status') == 'valid':
                    return txid
            except bigchaindb_driver.exceptions.NotFoundError:
                    trials += 1
        return None




class TopicSnapshot(GenericSnapshot):
    """
    Whenever topic is changed, we store its here, and a copy in BigChainDB.
    """
    data = JSONField()
    topic = models.ForeignKey(Topic)

    def __str__(self):
        return "Topic snapshot for {}".format(self.topic)

    def save(self, blockchain=False, *args, **kwargs):
        """
        Save in a blockchain ID= blockchain.
        """

        if blockchain:
            txid = blockchain_save(
                user=self.topic.owner,
                blockchain=blockchain,
                data=self.data
            )
            self.blockchain = blockchain
            self.blockchain_tx = txid

        super(TopicSnapshot, self).save(*args, **kwargs)


class CommentSnapshot(GenericSnapshot):
    """
    Whenever comment is changed, or transaction is made,
    we have to store the comment content to permanent storage.

    To be saved in BigchainDB, possibly e-mailed, and posted on social media.
    """

    data = JSONField()
    comment = models.ForeignKey(Comment)

    def __str__(self):
        return "Comment snapshot for {}".format(self.comment)

    def save(self, blockchain=False, *args, **kwargs):
        """
        Save in a blockchain ID= blockchain.
        """

        if blockchain:
            txid = blockchain_save(
                user=self.comment.owner,
                blockchain=blockchain,
                data=self.data
            )
            self.blockchain = blockchain
            self.blockchain_tx = txid

        super(CommentSnapshot, self).save(*args, **kwargs)

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

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "currencies"


class HourPriceSnapshot(GenericSnapshot):
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

    def __str__(self):
        return self.name


class CurrencyPriceSnapshot(GenericSnapshot):
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

    def __str__(self):
        return self.name


class Interaction(GenericModel):
    """
    Interactions are a way to invest time, parts of comments.

    They are actions of claiming time - claimed_hours, assumed_hours.
    """

    comment = models.ForeignKey(Comment)
    snapshot = models.ForeignKey(CommentSnapshot)

    claimed_hours_to_match = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)


class Transaction(GenericModel):
    """
    Transactions are a way to invest money to claimed time and things.

    They are actions of covering time - matched_hours, donated_hours.
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
        """ Hours matched up with claimed time. """
        paid_in_hours = self.payment_amount/self.hour_unit_cost


        # self.matched_hours = min(self.snapshot.claimed_hours, paid_in_hours)
        remaining_claimed_time = self.comment.claimed_hours - self.comment.matched()
        self.matched_hours = min(remaining_claimed_time, paid_in_hours)

        """ Hours not matched up.  """
        # self.donated_hours = min(self.snapshot.assumed_hours, paid_in_hours - self.matched_hours)
        remaining_assumed_time = self.comment.assumed_hours - self.comment.donated()
        self.donated_hours = min(remaining_assumed_time, paid_in_hours - self.matched_hours)

    def create_contribution_certificates(self):
        """
        Subject: comment's remaining claimed_time, and assumed_time.
        ============================================================
        remaining_claimed_time , remaining_assumed_time
        """
        remaining_claimed_time = self.comment.claimed_hours - self.comment.matched()
        remaining_assumed_time = self.comment.assumed_hours - self.comment.donated()



        DOER = 0
        INVESTOR = 1

        if self.matched_hours:
            doer_cert = ContributionCertificate(
                type=DOER,
                transaction=self,
                comment_snapshot=self.snapshot,
                hours=self.matched_hours/Decimal(2.),
                matched=True,
                received_by=self.payment_recipient,
            )
            doer_cert.save()
            investor_cert = ContributionCertificate(
                type=INVESTOR,
                transaction=self,
                comment_snapshot=self.snapshot,
                hours=self.matched_hours/Decimal(2.),
                matched=True,
                received_by=self.payment_sender,
            )
            investor_cert.save()

        if self.donated_hours:
            doer_cert = ContributionCertificate(
                type=DOER,
                transaction=self,
                comment_snapshot=self.snapshot,
                hours=self.donated_hours/Decimal(2.),
                matched=False,
                received_by=self.payment_recipient,
            )
            doer_cert.save()
            investor_cert = ContributionCertificate(
                type=INVESTOR,
                transaction=self,
                comment_snapshot=self.snapshot,
                hours=self.donated_hours/Decimal(2.),
                matched=False,
                received_by=self.payment_sender,
            )
            investor_cert.save()


class ContributionCertificate(GenericModel):
    """
    ContributionCertificates are proofs of co-creation, grounded in
    immutable comment_snapshots and transactions: one doer, one investor.

    They will be e-mailed to both parties, in additional e-mail addresses
    desired, as well as in blockchains, so as to have multi-method prov-
    ability. ( https://infty.xyz/goal/116/detail/?lang=en )

    Additionally, users will be able to provide social media accounts to
    post their updates of ContributionCertificates.

    Regarding the .matched property -- indicates if the time was matched.
      Instead of updating the record, we will create new contribution
      certificates. If a transaction certificate is updated, derived
      future is considered invalid.

    Whenever we have a contribution certificate with matched=False time,

    """
    DOER = 0
    INVESTOR = 1

    CERTIFICATE_TYPES = [
        (DOER, 'DOER'),
        (INVESTOR, 'INVESTOR'),
    ]

    type = models.PositiveSmallIntegerField(CERTIFICATE_TYPES, default=DOER)
    transaction = models.ForeignKey(Transaction)
    interaction = models.ForeignKey(Interaction, blank=True, null=True)
    comment_snapshot = models.ForeignKey(CommentSnapshot)
    hours = models.DecimalField(default=0.,decimal_places=8,max_digits=20,blank=False)
    matched = models.BooleanField(default=True)
    received_by = models.ForeignKey(User)

    broken = models.BooleanField(default=False)
    parent = models.ForeignKey('self', blank=True, null=True)


    @classmethod
    def user_matched(cls, user):
        """
        Returns amount of matched hours that a given user has accumulated.
        """
        return Decimal(
            cls.objects.filter(
                matched=True,
                broken=False,
                received_by=user).aggregate(
                    total=Sum('hours')
                ).get('total')
            or 0)

    @classmethod
    def user_unmatched(cls, user):
        """
        Returns amount of matched hours that a given user has accumulated.
        """
        return Decimal(
            cls.objects.filter(
                matched=False,
                broken=False,
                received_by=user).aggregate(
                    total=Sum('hours')
                ).get('total')
            or 0)