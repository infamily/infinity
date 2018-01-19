# Create your tests here.
from decimal import Decimal
import json

from test_plus.test import TestCase

from django.db.models import Sum

from src.core.models import (
    Topic,
    Comment,
)
from src.transactions.models import (
    Currency,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
    ContributionCertificate
)


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

    def test_topic_saved_to_bigchaindb(self):
        # signed by user who
        # it's easier if all users have at least one keypair.
        pass


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

        # Test the balances of the users.
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.1')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.1')
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

        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.35')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.1')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor2),
            Decimal('0.25')
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


        Now, let's say that the doer updates the comment to show
        the progress (changes the .assumed_hours to .claimed_hours)

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

        (1) We go through old certificates with broken=False, matched=False,
        (2) Make new child certificates with broken=False, matched=True,
        (3) and at the points of overflow, broken=False, matched=False.
        (4) invalidate parent certificates.
        """

        # We have correct initial state:
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

        # None is matched yet.
        self.assertEqual(
            self.comment2.matched(),
            Decimal('0.0')
        )

        # Both investor and doer should by now have zero matched time.
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.0')
        )


        # Both doer and investor should have '0.5' h each as 'unmatched'
        self.assertEqual(
            ContributionCertificate.user_unmatched(self.doer),
            Decimal('0.5')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor),
            Decimal('0.5')
        )

        # Let's say, the doer updates comment to show progress.

        self.comment2.text = """
        - {0.4}{?7.6} for testing.

        Here is the result so far:
        https://wiki.mindey.com/shared/screens/7e402349b3c2e3a626b5d25fd.png
        https://wiki.mindey.com/shared/screens/92fe2c4d8c795e4ff39884622.png
        """
        self.comment2.save()

        # The matched time is 0.4
        self.assertEqual(
            self.comment2.matched(),
            Decimal('0.4')
        )

        # The donated time is 0.6
        self.assertEqual(
            self.comment2.donated(),
            Decimal('0.6')
        )

        # Invested should be 1.0 as before
        self.assertEqual(
            self.comment2.invested(),
            Decimal('1.0')
        )

        # Remains the same amount to invest:
        self.assertTrue(
            Decimal('7.0')-self.comment2.remains() < Decimal('1E-15')
        )

        # Number of certificates for the comment should be:
        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2
            ).count(),
            6
        )

        # Two of them broken:
        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                broken=True
            ).count(),
            2
        )

        # Four of them not broken:
        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                broken=False
            ).count(),
            4
        )

        # Two of unbroken those received by doer:
        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                received_by=self.doer,
                broken=False
            ).count(),
            2
        )

        # Two of unbroken those received by the investor:
        self.assertEqual(
            ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                received_by=self.investor,
                broken=False
            ).count(),
            2
        )

        # Doer has 0.2, and investor also 0.2 matched hours.

        # Two of unbroken those received by the investor, summing to 0.2:
        self.assertEqual(
            Decimal(ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                received_by=self.investor,
                matched=True,
                broken=False
            ).aggregate(total=Sum('hours')).get('total') or 0),
            Decimal('0.2')
        )

        # Two of unbroken those received by the doer, summing to 0.2:
        self.assertEqual(
            Decimal(ContributionCertificate.objects.filter(
                transaction__comment=self.comment2,
                received_by=self.doer,
                matched=True,
                broken=False
            ).aggregate(total=Sum('hours')).get('total') or 0),
            Decimal('0.2')
        )


        # Doer has 0.2 matched hours
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.2')
        )

        # Investor has 0.2 matched hours
        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.2')
        )


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
        self.assertEqual(self.comment.claimed_hours, Decimal('1.5'))
        self.assertEqual(self.comment.assumed_hours, Decimal('6.5'))

        self.tx1 = self.comment.invest(4.0, 'eur', self.investor)

        # [INVESTED]
        self.assertEqual(
            self.comment.invested(),
            Decimal('4.0')
        )

        # [PRESENT]
        self.assertEqual(
            self.comment.matched(),
            Decimal('1.5')
        )

        # [FUTURE]
        self.assertEqual(
            self.comment.donated(),
            Decimal('2.5')
        )

        # [REMAINS]
        self.assertEqual(
            self.comment.remains(),
            Decimal('4.0')
        )


        # Balances:
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.75')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.75')
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
            self.comment2.remains(),
            Decimal('8.0')
        )

        self.tx1 = self.comment2.invest(1.0, 'eur', self.investor)
        self.tx2 = self.comment2.invest(1.0, 'eur', self.investor2)
        self.tx3 = self.comment2.invest(6.0, 'eur', self.investor3)

        self.assertEqual(
            self.comment2.invested(),
            Decimal('8.0')
        )

        self.assertEqual(
            self.comment2.remains(),
            Decimal('0.0')
        )

        # [PRESENT]
        self.assertEqual(
            self.comment2.matched(),
            Decimal('0.0')
        )

        # [FUTURE]
        self.assertEqual(
            self.comment2.donated(),
            Decimal('8.0')
        )

        # .matched_hours by investors must be zero.
        self.assertEqual(self.comment2.matched(by=self.investor),Decimal('0.0'))
        self.assertEqual(self.comment2.matched(by=self.investor2),Decimal('0.0'))
        self.assertEqual(self.comment2.matched(by=self.investor3),Decimal('0.0'))

        # .donated_hours by investors must be 1/2,1/2,6/2 respectively.
        self.assertEqual(self.comment2.donated(by=self.investor),Decimal('1.0')/Decimal(2))
        self.assertEqual(self.comment2.donated(by=self.investor2),Decimal('1.0')/Decimal(2))
        self.assertEqual(self.comment2.donated(by=self.investor3),Decimal('6.0')/Decimal(2))

        # .donated_hours by doer must be 4, or 1/2+1/2+6/2, as doer gets 50%.
        self.assertEqual(
            self.comment2.donated(by=self.doer),
            Decimal('4.0')
        )

        # Balances
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor2),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor3),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.doer),
            Decimal('4.0')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor),
            Decimal('0.5')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor2),
            Decimal('0.5')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor3),
            Decimal('3.0')
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
        self.assertEqual(self.comment.claimed_hours, Decimal('1.5'))
        self.assertEqual(self.comment.assumed_hours, Decimal('6.5'))
        self.assertEqual(self.comment.remains(), Decimal('8.0'))

        self.tx1 = self.comment.invest(1.0, 'eur', self.investor)
        self.assertEqual(self.comment.invested(), Decimal('1.0'))
        self.assertEqual(self.comment.remains(), Decimal('7.0'))
        self.assertEqual(self.comment.donated(), Decimal('0.0'))
        self.assertEqual(self.comment.contributions(), 2)

        self.assertEqual(
            self.comment.claimed_hours - self.comment.matched(),
            Decimal(0.5)
        )

        self.assertEqual(
            self.comment.assumed_hours - self.comment.donated(),
            Decimal(6.5)
        )

        self.assertEqual(self.comment.remains(), Decimal('7.0'))

        self.tx2 = self.comment.invest(1.0, 'eur', self.investor2)
        self.assertEqual(self.comment.invested(), Decimal('2.0'))
        self.assertEqual(self.comment.remains(), Decimal('6.0'))
        self.assertEqual(self.comment.contributions(), 6)
        self.assertEqual(self.comment.donated(), Decimal('0.5'))

        self.tx3 = self.comment.invest(6.0, 'eur', self.investor3)
        self.assertEqual(self.comment.invested(), Decimal('8.0'))
        self.assertEqual(self.comment.remains(), Decimal('0.0'))
        self.assertEqual(self.comment.donated(), Decimal('6.5'))


        self.assertEqual(
            self.comment.remains(),
            Decimal('0.0')
        )

        self.assertEqual(
            self.comment.matched(),
            Decimal('1.5')
        )

        self.assertEqual(
            self.comment.donated(),
            Decimal('6.5')
        )

        # Balances
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.75')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.5')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor2),
            Decimal('0.25')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor3),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.doer),
            Decimal('3.25')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor2),
            Decimal('0.25')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor3),
            Decimal('3.0')
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
            self.comment.claimed_hours,
            Decimal('1.5')
        )
        self.assertEqual(
            self.comment.assumed_hours,
            Decimal('6.5')
        )

        self.comment.invest(0.1, 'eur', self.investor)

        self.comment.text ="""
        - {1.0},{?0.1} for coming up with basic class structure,
        - {?2.5} for implementation,
        - {?3.5} for testing.

        Here is the result so far:
        https://github.com/wefindx/infty2.0/commit/9f096dc54f94c31eed9558eb32ef0858f51b1aec
        """

        self.comment.save()

        self.assertEqual(
            self.comment.claimed_hours,
            Decimal('1.0')
        )
        self.assertTrue(
            self.comment.assumed_hours-Decimal('6.1') < Decimal('1E-15')
        )

        self.assertEqual(
            self.comment.invested(),
            Decimal('0.1')
        )

        self.assertEqual(
            self.comment.matched(),
            Decimal('0.1')
        )

        self.assertEqual(
            self.comment.donated(),
            Decimal('0.0')
        )

        # Balances
        self.assertEqual(
            ContributionCertificate.user_matched(self.doer),
            Decimal('0.05')
        )

        self.assertEqual(
            ContributionCertificate.user_matched(self.investor),
            Decimal('0.05')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.doer),
            Decimal('0.0')
        )

        self.assertEqual(
            ContributionCertificate.user_unmatched(self.investor),
            Decimal('0.0')
        )
