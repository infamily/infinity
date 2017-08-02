# Create your tests here.
import requests, json
from decimal import Decimal
from test_plus.test import TestCase
from infty.core.models import (
    Topic,
    Comment,
    Currency,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
    CommentSnapshot,
    Transaction,
    ContributionCertificate
)
from django.db.models import Sum

class TestTopic(TestCase):

    def setUp(self):
        # Let's say we have currencies:
        self.hur = Currency(label='hur'); self.hur.save()
        self.usd = Currency(label='usd'); self.usd.save()
        self.eur = Currency(label='eur'); self.eur.save()
        self.cny = Currency(label='cny'); self.cny.save()
        self.gbp = Currency(label='gbp'); self.gbp.save()

        # Let's say we have the hour price, and currency prices
        # collected periodically:
        # 
        # - HourPriceSnapshot
        # - CurrencyPriceSnapshot0

        self.hprice = HourPriceSnapshot(
            name='FRED',
            base=self.usd,
            data=json.loads("""
{"realtime_start":"2017-07-28","realtime_end":"2017-07-28","observation_start":"1600-01-01","observation_end":"9999-12-31","units":"lin","output_type":1,"file_type":"json","order_by":"observation_date","sort_order":"desc","count":136,"offset":0,"limit":1,"observations":[{"realtime_start":"2017-07-28","realtime_end":"2017-07-28","date":"2017-06-01","value":"26.25"}]}"""),
            endpoint='https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json',
        )
        self.hprice.save()
        self.cprice = CurrencyPriceSnapshot(
            name='FIXER',
            base=self.eur,
            data=json.loads("""
{"base":"EUR","date":"2017-07-28","rates":{"AUD":1.4732,"BGN":1.9558,"BRL":3.7015,"CAD":1.4712,"CHF":1.1357,"CNY":7.9087,"CZK":26.048,"DKK":7.4364,"GBP":0.89568,"HKD":9.1613,"HRK":7.412,"HUF":304.93,"IDR":15639.0,"ILS":4.1765,"INR":75.256,"JPY":130.37,"KRW":1317.6,"MXN":20.809,"MYR":5.0229,"NOK":9.3195,"NZD":1.5694,"PHP":59.207,"PLN":4.2493,"RON":4.558,"RUB":69.832,"SEK":9.5355,"SGD":1.5947,"THB":39.146,"TRY":4.1462,"USD":1.1729,"ZAR":15.281}}"""),
            endpoint='https://api.fixer.io/latest?base=eur',
        )
        self.cprice.save()

        # Let's say we have a user 'thinker'..
        self.thinker = self.make_user('thinker')
        self.thinker.save()

        # ..who writes a post:
        self.topic = Topic.objects.create(
            title='Improve test module',
            body='implement class that autogenerates users',
            owner=self.thinker,
        )
        self.topic.save()

        # Then, we have a user 'doer'..
        self.doer = self.make_user('doer')
        self.doer.save()

        # ..who creates a comment on it, with:
        self.comment = Comment(
            topic=self.topic,
            # 1. time spent inside "{...}" brackets
            # 2. estimates of future time needed inside "{?...}"
            # 3. declared work result - the content of comment
            text="""
            - {1.5},{?0.5} for coming up with basic class structure,
            - {?2.5} for implementation,
            - {?3.5} for testing.

            Here is the result so far:
            https://github.com/wefindx/infty2.0/commit/9f096dc54f94c31eed9558eb32ef0858f51b1aec
            """,
            owner=self.doer
        )
        self.comment.save()

        # ...and another comment, with some other amount of time, and result:
        self.comment2 = Comment(
            topic=self.topic,
            text="""
            - {?8} for testing.

            Here is the result so far:
            https://wiki.mindey.com/shared/screens/7e402349b3c2e3a626b5d25fd.png
            """,
            owner=self.doer
        )
        self.comment2.save()


        # Then, investor comes in:
        self.investor = self.make_user('investor')
        self.investor.save()

        # And there is another investor:

        self.investor2 = self.make_user('investor2')
        self.investor2.save()

        # And there is another investor:

        self.investor3 = self.make_user('investor3')
        self.investor3.save()

        # Ok, so, what investments can happen?

    def test_currency_uppercase(self):
        self.assertEqual(self.hur.label, 'HUR')
        self.assertEqual(self.eur.label, 'EUR')
        self.assertEqual(self.usd.label, 'USD')

    def test_currency_parsing(self):
        self.assertEqual(self.hprice.data['observations'][0]['value'], "26.25")
        self.assertEqual(self.cprice.data['rates']['USD'], 1.1729)

    def test_currency_eur(self):
        self.assertEqual(
            self.eur.in_hours(),
            Decimal(1)/((Decimal('26.25')/Decimal(1.1729)))
        )

    def test_currency_gbp(self):
        self.assertEqual(
            self.gbp.in_hours(),
            Decimal(1)/(Decimal('26.25')/Decimal(1.1729)*(Decimal(0.89568)))
        )

    def test_currency_cny(self):
        self.assertEqual(
            self.cny.in_hours(),
            Decimal(1)/((Decimal('26.25')/Decimal(1.1729)*(Decimal(7.9087))))
        )

    def test_comment_parsed_values(self):

        self.assertEqual(
            self.comment.claimed_hours,
            1.5
        )

        self.assertEqual(
            self.comment.assumed_hours,
            6.5
        )

    def test_comment2_parsed_values(self):
        self.assertEqual(
            self.comment2.assumed_hours,
            Decimal('8.0')
        )




    """
    INVESTMENT TYPES TO COVER
    =========================
    """

    def test_simple_investment(self):
        """
        "Simple Investment"
        : there is only one investor, and the amount to invest is smaller
          than then time declared.

        DOER
             1.5 h                       6.5 ĥ
        [------------][-------------------------------------------]

        INVESTOR

        0.2 ḥ
        [--]

        CONTRIBUTIONS
        [--]

        # https://wiki.mindey.com/shared/screens/b6767a949a4884cfd4fe17b41.png
        """

        # Investor decides that s/he wants to invest into 0.2, and pay in EUR
        # of claimed time;  sees the "(1.5 h) invest" button, and clicks it.

        self.tx = self.comment.invest(0.2, 'eur', self.investor)

        self.assertTrue(
            self.tx.hour_unit_cost-Decimal('22.38042458862648158969049976') < Decimal('1E-28')
        )

        # As part of transaction, the ContributionCertificates
        # are generated to both parties - the doer, and investor.
        # For thinker -- will add the option to auto-generate 
        # first comment with amount of time claimed to write the topic.

        # Generated amount is approximately equal to amount purchased.
        self.assertTrue(
            (self.tx.matched_hours-Decimal(0.2)) < Decimal('1E-28')
        )

        # Doer and Investor gets equal amount as contributors.

        # There should be 2 parts of the transaction:
        self.assertEqual(
            ContributionCertificate.objects.filter(transaction=self.tx).count(),
            2
        )

        # Both parts should be equal:
        self.assertEqual(
            ContributionCertificate.objects.filter(transaction=self.tx).first().hours,
            ContributionCertificate.objects.filter(transaction=self.tx).last().hours,
        )

        # Both parts of the transaction should be 
        self.assertTrue(
            (ContributionCertificate.objects.filter(transaction=self.tx).first().hours-Decimal(0.1)) < Decimal('1E-28')
        )

        # The balance (score) of user is defined as sum of all contributions!
        self.assertEqual(
            Decimal('0.1'),
            ContributionCertificate.objects.filter(
                received_by=self.doer).aggregate(
                    total=Sum('hours')
                         )['total']
        )

        # The balance (score) of user is defined as sum of all contributions!
        self.assertEqual(
            Decimal('0.1'),
            ContributionCertificate.objects.filter(
                received_by=self.investor).aggregate(
                    total=Sum('hours')
                         )['total']
        )


        self.assertEqual(
            self.comment.remains(),
            Decimal('1.5')+Decimal('6.5')-Decimal('0.2')
        )

    def test_simple_investment_multiparty(self):
        """
        "Simple Investment Multiparty"
        : there is a couple of investors, and the total amount of investment
          is smaller than total declared time.

        DOER
             1.5 h                       6.5 ĥ
        [------------][-------------------------------------------]

        INVESTOR 1

        0.2 ḥ
        [--]

        INVESTOR 2
            0.5 ḥ
            [----]

        CONTRIBUTIONS
        [--][----]
        """
        self.tx1 = self.comment.invest(0.2, 'eur', self.investor)
        self.tx2 = self.comment.invest(0.5, 'cny', self.investor2)

        self.assertTrue(
            Decimal(0.7) - self.comment.invested() < Decimal('1E-28')
        )

        self.assertTrue(
            self.tx1.hour_unit_cost-Decimal('22.38042458862648158969049976') < Decimal('1E-28')
        )

        self.assertTrue(
            self.tx2.hour_unit_cost-Decimal('177.0000639440702549483852555') < Decimal('1E-28')
        )

        self.assertEqual(
            ContributionCertificate.objects.filter(comment_snapshot__comment=self.comment).count(),
            4
        )

    def test_future_investment_one_investor(self):
        """
        DOER
                                     8.0 ĥ
        [---------------------------------------------------------]

        INVESTOR

          1.0 ħ
        [--------]

        CONTRIBUTIONS
        [-FUTURE-] ( .unmatched )
        """

        # We have correct initial state: 
        # - 0.0 claimed hours,
        # - 8.0 assumed hours
        # - 8.0 remains to invest
        self.assertEqual(
            self.comment2.claimed_hours,
            Decimal(0.0)
        )
        self.assertEqual(
            self.comment2.assumed_hours,
            Decimal(8.0)
        )
        self.assertEqual(
            self.comment2.remains(),
            Decimal(8.0)
        )

        # An investor comes to make an investment of 1.0

        self.tx = self.comment2.invest(1.0, 'eur', self.investor)

        # Both investor and doer get a certificate of investment.
        self.assertEqual(
            ContributionCertificate.objects.filter(comment_snapshot__comment=self.comment2).count(),
            2
        )

        # Invested amount 1.0
        self.assertEqual(
            Decimal('1.0'),
            self.comment2.invested()
        )

        # Remains to invest 7.0
        self.assertEqual(
            self.comment2.remains(),
            Decimal('7.0')
        )

        # Both investor and doer should by now have zero matched time.
        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    received_by=self.doer, matched=True).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(0.0)
        )

        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    received_by=self.investor, matched=True).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(0.0)
        )

        # Both doer and investor should have '0.5' h each as 'unmatched'

        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    received_by=self.doer, matched=False).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(0.5)
        )

        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    received_by=self.investor, matched=False).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(0.5)
        )

        # Now, let's say that the doer updates the comment to show
        # the progress (changes the .assumed_hours to .claimed_hours)

        """
                                     8.0 ĥ
        [---------------------------------------------------------]
        COMMENT UPDATE
             |
            \ /
             v

        DOER
        0.4 h                       7.6 ĥ
        [--][-----------------------------------------------------]

        INVESTOR

          1.0 ħ
        [--------]

        CONTRIBUTIONS
        [-FUTURE-] ( .unmatched )

        0.4 ḥ
        [--]

        HAPPENS

        (1) The old certificate should be marked broken=True

        # But for that, we need to get all contribution certificates
        # of a comment, so, need all transactions of the comment.
        """

        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2, broken=False
            ).count(),
            2
        )

        """
        And, we also need to figure out, which certificates are
        corresponding to previously matched time.
        """

        # Obviously, previously matched time corresponds to
        # sum of all ContributionCertificates with matched=True,
        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    transaction__comment=self.comment2,
                    matched=True).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(0.0)
        )
        # and previously unmatched time is all certs with matched=False
        self.assertEqual(
            Decimal(
                ContributionCertificate.objects.filter(
                    transaction__comment=self.comment2,
                    matched=False).aggregate(
                    total=Sum('hours')
                ).get('total') or 0
            ),
            Decimal(1.0)
        )

        # So, previously, matched time was 0.0, and unmatched 1.0
        # Now the matched time will be 0.4, and unmatched 0.6

        # now, we should go through the certificates in pairs,
        # and match them up until 0.4 margin.

        # We have (DOER, INVESTOR), (it was just two certificates)
        # And, of course, they will have been created in pairs,
        # And, in the sequence of ascending ids.
        # And there will be always even number of them per comment.

        self.assertEqual(
            self.comment2.invested(),
            Decimal(1.0)
        )

        self.assertEqual(
            self.comment2.matched(),
            Decimal(0.0)
        )


        parsed = self.comment2.parse_hours("""
        - {0.4}{?7.6} for testing.

        Here is the result so far:
        https://wiki.mindey.com/shared/screens/7e402349b3c2e3a626b5d25fd.png
        https://wiki.mindey.com/shared/screens/92fe2c4d8c795e4ff39884622.png
        """)
        parsed_claimed_hours = parsed['claimed_hours']
        parsed_assumed_hours = parsed['assumed_hours']

        self.assertTrue(parsed_claimed_hours - Decimal(0.4) < Decimal('1E-28'))
        self.assertTrue(parsed_assumed_hours - Decimal(7.6) < Decimal('1E-28'))

        self.assertEqual(self.comment2.claimed_hours, Decimal(0.0))
        self.assertEqual(self.comment2.assumed_hours, Decimal(8.0))

        new_claimed_hours = parsed_claimed_hours - self.comment2.matched()

        self.assertTrue(new_claimed_hours - Decimal(0.4) < Decimal('1E-28'))


        """ Going in pairs over all unmatched, unbroken certificates
        ContributionCertificates of the comment, and creating matched
        and unmatched children certificates.
        """
        cert1 = None
        for i, cert2 in enumerate(
                ContributionCertificate.objects.filter(
                    transaction__comment=self.comment2,
                    broken=False,
                    matched=False,
                ).order_by('pk').all()):
            if i % 2 == 0:
                cert1 = cert2
                continue

            # SANITY CHECKS:
            self.assertEqual(cert1.transaction, cert2.transaction)
            self.assertEqual(cert1.type, 0)
            self.assertEqual(cert2.type, 1)
            self.assertEqual(cert1.hours, cert2.hours)

            certs_hours = cert1.hours + cert2.hours
            self.assertEqual(certs_hours, Decimal(1.0))
            """ Iterating over certificate pairs. """

            DOER = 0
            INVESTOR = 1

            if not new_claimed_hours:
                break

            elif new_claimed_hours >= certs_hours:
                " Create matched certs. (2) "

                doer_cert = ContributionCertificate(
                    type=DOER,
                    transaction=cert1.transaction,
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
                new_claimed_hours -= certs_hours

            elif new_claimed_hours < certs_hours:
                " Create matched and unmatched certs. (4) "

                hours_to_match = new_claimed_hours/Decimal(2)

                doer_cert = ContributionCertificate(
                    type=DOER,
                    transaction=cert1.transaction,
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
                    comment_snapshot=cert2.comment_snapshot,
                    hours=hours_to_match,
                    matched=True,
                    received_by=cert2.received_by,
                    broken=False,
                    parent=cert2,
                )
                investor_cert.save()

                hours_to_donate = (certs_hours-new_claimed_hours)/Decimal(2)

                doer_cert = ContributionCertificate(
                    type=DOER,
                    transaction=cert1.transaction,
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
                new_claimed_hours = Decimal(0.0)

                " Break the iteration "
                break

            self.assertTrue(
                Decimal(0.6)-self.comment2.donated() < Decimal('1E-28')
            )
            self.assertTrue(
                Decimal(0.4)-self.comment2.matched() < Decimal('1E-28')
            )


            # If we can, we match it fully, if we can't, we match
            # it partially, generating matched=False certificates too.
            # Super, now we break the pairs of certificates.
            # if  .matched() < track <= .invested() region
            # we'll match them.


        """
        Then figure out the newly matched time.

        And take the difference between newly matched time
        and previously matched time, to see, which certificates
        are affacted.

        """


        """
        Then, for each affected certificate, split (brake) it
        and create four new ones.

        """

        # for ContributionCertificate.objects.filter()
        #
        # self.assertEqual(
        #
        # )

        """
        (2) The new child certificates should be generated:
          - one with matched=True, other with matched=False
           (both with broken=False)

        To do that, we need to identify the old certificate(s) that are
        within the interval.

        To do that, we need to order all the broken=False certificates
        in order of date increase (better: ID increase, cause clocks
        are changing and getting out of sync over time)

        Also order all the .claimed_time, and .assumed time at two points:

        [----------][--------] # claimed_hours, assumed_hours
        [----][-------]        # matched_hours, donated_hours

        [----][----][-][-----]
          M     M    D    D

          M - matched
          D - donated

        [--------------][----] # claimed_hours, assumed_hours
        [----][-------]        # matched_hours, donated_hours

        [----][----][--][----]
          M     M    M    D

        """

        # So, upon update of comment amount, we have to invalidate
        # previous certificate, and create two new certificates.

        self.comment2.text = """
        - {0.4}{?7.6} for testing.

        Here is the result so far:
        https://wiki.mindey.com/shared/screens/7e402349b3c2e3a626b5d25fd.png
        https://wiki.mindey.com/shared/screens/92fe2c4d8c795e4ff39884622.png
        """

        self.comment2.save()

        self.assertTrue(
            self.comment2.claimed_hours - Decimal(7.6) < Decimal('1E-28')
        )

        self.assertTrue(
            self.comment2.assumed_hours - Decimal(7.6) < Decimal('1E-28')
        )

        # self.assertEqual(
        #     self.comment2.text,
        #     Comment.objects.get(pk=self.comment2.pk).text
        # )



        # 4. Also can write more .claimed_time or .assumed_time

    def test_mixed_present_future_investment_one_investor(self):
        """
        "Mixed Present-Future Investment one investor"
        : there is only one investor, and the amount to invest is larger
          than the time declared.
          (needs to simulate that if there is re-declaration of time,
           where there is more time declared, then the new ContributionCer-
           tificates generated, linked to same Transaction)

        DOER
             1.5 h                       6.5 ĥ
        [------------][-------------------------------------------]

        INVESTOR

                    4.0 ḥ
        [---------------------------]

        CONTRIBUTIONS
        [--PRESENT--][---FUTURE-----] ( .unmatched )
        """

        self.assertEqual(
            1,
            1
        )

    def test_future_investment_multiparty(self):
        """
        DOER
                                     8.0 ĥ
        [---------------------------------------------------------]

        INVESTOR1 INVESTOR2                INVESTOR3

           1.0 ḥ    1.0 ḥ                    6.0 ḥ
        [--------][--------][-------------------------------------]

        CONTRIBUTIONS
        [-FUTURE-][-FUTURE-][---------------FUTURE----------------]
        ( .unmatched ) ( .unmatched ) ( .unmatched )
        """
        self.assertEqual(
            1,
            1
        )

    def test_mixed_present_future_investment_multiparty(self):
        """
        "Mixed Present-Future Investment Multiparty
        : there is a couple of investors ,and the total amount of investment
          is larger than the time declared.
          (needs to simulate that if there is re-declaration of time,
          where there is more time declared, then the new ContributionCer-
          tificates are generated, so as to preserve priority of investors'
          sequence. E.g., if small extra time is declared, the newly
          crated ContributionCertificate is for the earlier investments.)

        DOER
             1.5 h                       6.5 ĥ
        [------------][-------------------------------------------]

        INVESTOR1 INVESTOR2                INVESTOR3

           1.0 ḥ    1.0 ḥ                    6.0 ḥ
        [--------][--------][-------------------------------------]

        CONTRIBUTIONS
        [----P---][P-][-F--][--------------FUTURE-----------------]

        """

        self.assertEqual(
            1,
            1
        )

    def test_redeclaration_of_less_time(self):
        """
        test re-declarations of time. E.g., if there is already covered
          declared time, it should not be possible to save comment with
          less declared time than is already covered by transactions.

        -Should not be possible to change the declared time to smaller
        if there are investments already.-
        """
        self.assertEqual(
            1,
            1
        )

