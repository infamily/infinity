from decimal import Decimal

from django.db.models import Sum

from src.transactions.utils import instance_to_save_dict
from src.transactions.models import (
    TopicSnapshot,
    CommentSnapshot,
    ContributionCertificate,
    Currency,
    Interaction,
    Transaction,
)
from src.trade.models import Reserve


class TopicTransactionMixin():

    def create_snapshot(self, blockchain=False):
        snapshot = TopicSnapshot(
            topic=self,
            data=instance_to_save_dict(self)
        )
        snapshot.save(blockchain=blockchain)
        return snapshot

    def matched(self, by=None):
        """
        Hours matched.
        """
        qs = ContributionCertificate.objects.filter(
            comment_snapshot__comment__topic=self,
            matched=True,
            broken=False
        )
        if by:
            qs = qs.filter(received_by=by)

        return Decimal(qs.aggregate(total=Sum('hours')).get('total') or 0)


class CommentTransactionMixin():
    def create_snapshot(self, blockchain=False):
        snapshot = CommentSnapshot(
            comment=self,
            data=instance_to_save_dict(self)
        )
        snapshot.save(blockchain=blockchain)
        return snapshot

    def contributions(self):
        return ContributionCertificate.objects.filter(
            comment_snapshot__comment=self
        ).count()

    def matched(self, by=None):
        """
        Hours matched.
        """
        qs = ContributionCertificate.objects.filter(
            comment_snapshot__comment=self,
            matched=True,
            broken=False
        )
        if by:
            qs = qs.filter(received_by=by)

        return Decimal(qs.aggregate(total=Sum('hours')).get('total') or 0)

    def donated(self, by=None):
        """
        Hours donated.
        """
        qs = ContributionCertificate.objects.filter(
            comment_snapshot__comment=self,
            matched=False,
            broken=False
        )
        if by:
            qs = qs.filter(received_by=by)

        return Decimal(qs.aggregate(total=Sum('hours')).get('total') or 0)

    def invested(self):
        """
        Hours invested.  = self.matched() + self.donated()
        """
        qs = ContributionCertificate.objects.filter(
            comment_snapshot__comment=self,
            broken=False
        )
        return Decimal(qs.aggregate(total=Sum('hours')).get('total') or 0)

    def remains(self):
        """
        Hours in comment, not yet covered by investment.
        """
        return self.claimed_hours + self.assumed_hours - self.invested()

    def invest(self, hour_amount, payment_currency_label, investor):
        """
        Investing into .claimed_time, and .assumed_time.
        Generating Transaction, ContributionCertificates for
        comment owner, and investor.
        """

        amount = min(Decimal(hour_amount), self.remains())
        if not amount:
            return

        # Check that investment amount is not more than quota + reserve
        quota = Transaction.user_quota_remains_today(investor)
        reserve = Reserve.user_reserve_remains(investor)

        if amount > (quota + reserve):
            """ Don't let invest more than quota and reserve """
            return

        # Check that we have required currency
        try:
            currency = Currency.objects.get(
                label=payment_currency_label.upper()
            )
        except Currency.DoesNotExist:
            return

        value = currency.in_hours(objects=True)
        currency_amount = amount / value['in_hours']
        snapshot = self.create_snapshot(blockchain=self.blockchain)

        tx = Transaction.objects.create(
            comment=self,
            snapshot=snapshot,
            hour_price=value['hour_price_snapshot'],
            currency_price=value['currency_price_snapshot'],

            payment_amount=currency_amount,
            payment_currency=currency,
            payment_recipient=self.owner,
            payment_sender=investor,
            hour_unit_cost=Decimal(1.) / value['in_hours'],
        )

        # Deduce from reserve, if not enough quota
        if (amount - quota) > 0:
            expense = amount - quota
            Reserve.objects.create(
                transaction=tx,
                hours=-expense,
                user=investor,
            )

        # Return the transaction
        return tx

    def proceed_interaction(self):
        if not self.pk:
            self.set_hours()
            return

        """
        We create new snapshot, if changed.
        We determine the difference between new and snapshot.
        And create new ContributionCertificates if needed.
        """

        # Interaction(self, obj)
        obj = self.__class__.objects.get(pk=self.pk)
        # old = self.parse_hours(obj.text)
        new = self.parse_hours(self.text)

        # Monotonicity
        # 1. new (.claimed_hours+.assumed_hours) >= comment.invested()
        if (new['claimed_hours'] + new['assumed_hours']) < obj.invested():
            """
            Cannot remove time already paid for, don't .save().
            """
            pass
        # 2. new (.claimed_hours) >=  previously .matched_time.
        elif new['claimed_hours'] < obj.matched():
            """
            Cannot remove time matched, don't .save().
            """
            pass
        else:
            # Else, it is okay to proceed.

            # Subjects:
            amount = new['claimed_hours'] - obj.matched()

            # Taking snapshot
            snapshot = self.create_snapshot(blockchain=self.blockchain)

            # Recording interaction
            ix = Interaction.objects.create(
                comment=self,
                snapshot=snapshot,
                claimed_hours_to_match=amount,
            )

            """ Going in pairs over all unmatched, unbroken certificates
            ContributionCertificates of the comment, and creating matched and unmatched children certificates.
            """

            cert1 = None
            for i, cert2 in enumerate(
                    ContributionCertificate.objects.filter(
                        transaction__comment=self,
                        broken=False,
                        matched=False,
                    ).order_by('pk').all()):
                if i % 2 == 0:
                    cert1 = cert2
                    continue

                # Iterating over certificate pairs.
                # PAIR INTEGRITY CHECKS - PAIR MUST BE SYMMETRIC:
                if not ((cert1.transaction == cert2.transaction) & \
                    (cert1.type == ContributionCertificate.DOER) & \
                    (cert2.type == ContributionCertificate.INVESTOR) & \
                    (cert1.hours == cert2.hours)):
                    # Don't proceed if these conditions not satisfied.
                    break

                certs_hours = cert1.hours + cert2.hours

                if amount >= certs_hours:

                    # Create matched certs. (2)
                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.DOER,
                        transaction=cert1.transaction,
                        interaction=ix,
                        comment_snapshot=cert1.comment_snapshot,
                        hours=cert1.hours,
                        matched=True,
                        received_by=cert1.received_by,
                        broken=False,
                        parent=cert1,
                    )
                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.INVESTOR,
                        transaction=cert2.transaction,
                        interaction=ix,
                        comment_snapshot=cert2.comment_snapshot,
                        hours=cert2.hours,
                        matched=True,
                        received_by=cert2.received_by,
                        broken=False,
                        parent=cert2,
                    )

                    # Mark original cert as broken
                    cert1.broken = True
                    cert1.save()
                    cert2.broken = True
                    cert2.save()

                    # reduce number of hours covered
                    amount -= certs_hours

                elif amount < certs_hours:
                    # Create matched and unmatched certs. (4)

                    hours_to_match = amount / Decimal(2)

                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.DOER,
                        transaction=cert1.transaction,
                        interaction=ix,
                        comment_snapshot=cert1.comment_snapshot,
                        hours=hours_to_match,
                        matched=True,
                        received_by=cert1.received_by,
                        broken=False,
                        parent=cert1,
                    )
                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.INVESTOR,
                        transaction=cert2.transaction,
                        interaction=ix,
                        comment_snapshot=cert2.comment_snapshot,
                        hours=hours_to_match,
                        matched=True,
                        received_by=cert2.received_by,
                        broken=False,
                        parent=cert2,
                    )

                    hours_to_donate = (certs_hours - amount) / Decimal(2)

                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.DOER,
                        transaction=cert1.transaction,
                        interaction=ix,
                        comment_snapshot=cert1.comment_snapshot,
                        hours=hours_to_donate,
                        matched=False,
                        received_by=cert1.received_by,
                        broken=False,
                        parent=cert1,
                    )
                    ContributionCertificate.objects.create(
                        type=ContributionCertificate.INVESTOR,
                        transaction=cert2.transaction,
                        interaction=ix,
                        comment_snapshot=cert2.comment_snapshot,
                        hours=hours_to_donate,
                        matched=False,
                        received_by=cert2.received_by,
                        broken=False,
                        parent=cert2,
                    )

                    # Mark original cert as broken
                    cert1.broken = True
                    cert1.save()
                    cert2.broken = True
                    cert2.save()

                    # reduce number of hours covered
                    # AMOUNT = Decimal(0.0)
                    amount -= hours_to_donate

                    # Break the iteration
                    break

            self.set_hours()
