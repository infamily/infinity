from langsplit import splitter
from collections import OrderedDict

def _type_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for Type definition. """

    name = splitter.split(instance.name, title=True)
    try:
        definition = splitter.split(instance.definition)
    except Exception as e:
        print(e)
        definition = None

    langs = OrderedDict()
    for lang in list(name.keys()) + list(definition.keys()) if definition else []:
        if lang in name.keys() and lang in definition.keys():
            langs[lang] = True

    instance.name = splitter.convert(name, title=True).strip()

    if definition:
        instance.definition = splitter.convert(definition)

    instance.languages = list(langs.keys())

def _item_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for Item text. """
    description = splitter.split(instance.description)

    instance.description = splitter.convert(description)

    if isinstance(description, dict):
        instance.languages = list(description.keys())
    else:
        instance.languages = []

def _topic_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for topic title, body. """
    title = splitter.split(instance.title, title=True)
    try:
        body = splitter.split(instance.body)
    except Exception as e:
        print(e)
        body = None

    langs = OrderedDict()
    for lang in list(title.keys()) + list(body.keys()) if body else []:
        if lang in title.keys() and lang in body.keys():
            langs[lang] = True

    instance.title = splitter.convert(title, title=True).strip()

    if body:
        instance.body = splitter.convert(body)

    instance.languages = list(langs.keys())

def _topic_post_save(sender, instance, created, *args, **kwargs):
    """
    Create topic snapshot in blockchain, if requested.
    """
    if instance.blockchain:
        instance.create_snapshot(blockchain=instance.blockchain)

def _comment_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for comment text. """
    text = splitter.split(instance.text)

    instance.text = splitter.convert(text)

    if isinstance(text, dict):
        instance.languages = list(text.keys())
    else:
        instance.languages = []

def _comment_post_save(sender, instance, created, *args, **kwargs):
    """
    Create comment snapshot in blockchain, if requested.
    """
    if instance.blockchain:
        instance.create_snapshot(blockchain=instance.blockchain)




 #pre save
 #Comment
    def save(self, *args, **kwargs):
        """
        Save comment created date to parent object.
        """

        if self.pk:
            """
            We create new snapshot, if changed.
            We determine the difference between new and snapshot.
            And create new ContributionCertificates if needed.
            """

            # Interaction(self, obj)

            obj = Comment.objects.get(pk=self.pk)
            old = self.parse_hours(obj.text)
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
                AMOUNT = new['claimed_hours'] - obj.matched()

                # Taking snapshot
                snapshot = self.create_snapshot(blockchain=self.blockchain)

                # Recording interaction
                ix = Interaction(
                    comment=self,
                    snapshot=snapshot,
                    claimed_hours_to_match=AMOUNT,
                )
                ix.save()

                """ Going in pairs over all unmatched, unbroken certificates
                ContributionCertificates of the comment, and creating matched and unmatched children certificates.
                """

                DOER = 0
                INVESTOR = 1

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
                    """ Iterating over certificate pairs. """

                    # PAIR INTEGRITY CHECKS - PAIR MUST BE SYMMETRIC:
                    if not ((cert1.transaction == cert2.transaction) & \
                       (cert1.type == DOER) & \
                       (cert2.type == INVESTOR) & \
                       (cert1.hours == cert2.hours)):
                        " Don't proceed if these conditions not satisfied. "
                        break

                    certs_hours = cert1.hours + cert2.hours


                    if AMOUNT >= certs_hours:

                        " Create matched certs. (2) "

                        doer_cert = ContributionCertificate(
                            type=DOER,
                            transaction=cert1.transaction,
                            interaction=ix,
                            comment_snapshot=cert1.comment_snapshot,
                            hours=cert1.hours,
                            matched=True,
                            received_by=cert1.received_by,
                            broken=False,
                            parent=cert1,
                        )
                        doer_cert.save()
                        investor_cert = ContributionCertificate(
                            type=INVESTOR,
                            transaction=cert2.transaction,
                            interaction=ix,
                            comment_snapshot=cert2.comment_snapshot,
                            hours=cert2.hours,
                            matched=True,
                            received_by=cert2.received_by,
                            broken=False,
                            parent=cert2,
                        )
                        investor_cert.save()

                        " Mark original cert as broken "

                        cert1.broken = True; cert1.save()
                        cert2.broken = True; cert2.save()

                        " reduce number of hours covered "
                        AMOUNT -= certs_hours

                    elif AMOUNT < certs_hours:
                        " Create matched and unmatched certs. (4) "

                        hours_to_match = AMOUNT/Decimal(2)

                        doer_cert = ContributionCertificate(
                            type=DOER,
                            transaction=cert1.transaction,
                            interaction=ix,
                            comment_snapshot=cert1.comment_snapshot,
                            hours=hours_to_match,
                            matched=True,
                            received_by=cert1.received_by,
                            broken=False,
                            parent=cert1,
                        )
                        doer_cert.save()
                        investor_cert = ContributionCertificate(
                            type=INVESTOR,
                            transaction=cert2.transaction,
                            interaction=ix,
                            comment_snapshot=cert2.comment_snapshot,
                            hours=hours_to_match,
                            matched=True,
                            received_by=cert2.received_by,
                            broken=False,
                            parent=cert2,
                        )
                        investor_cert.save()

                        hours_to_donate = (certs_hours-AMOUNT)/Decimal(2)

                        doer_cert = ContributionCertificate(
                            type=DOER,
                            transaction=cert1.transaction,
                            interaction=ix,
                            comment_snapshot=cert1.comment_snapshot,
                            hours=hours_to_donate,
                            matched=False,
                            received_by=cert1.received_by,
                            broken=False,
                            parent=cert1,
                        )
                        doer_cert.save()
                        investor_cert = ContributionCertificate(
                            type=INVESTOR,
                            transaction=cert2.transaction,
                            interaction=ix,
                            comment_snapshot=cert2.comment_snapshot,
                            hours=hours_to_donate,
                            matched=False,
                            received_by=cert2.received_by,
                            broken=False,
                            parent=cert2,
                        )
                        investor_cert.save()

                        " Mark original cert as broken "

                        cert1.broken = True; cert1.save()
                        cert2.broken = True; cert2.save()

                        " reduce number of hours covered "
                        # AMOUNT = Decimal(0.0)
                        AMOUNT -= hours_to_donate

                        " Break the iteration "
                        break

                self.set_hours()
                super(Comment, self).save(*args, **kwargs)

        else:
            self.set_hours()
            super(Comment, self).save(*args, **kwargs)