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


        # self.AMOUNT_TO_PAY_DOER = self.comment.invest(0.2, 'eur')
        #
        # self.assertEqual(
        #     self.AMOUNT_TO_PAY_DOER,
        #     Decimal(0.2) * (Decimal(26.25)/Decimal(1.1729))
        # )
        #
        # # Then, if all is good, the comment snapshot is saved for history.. 
        # self.comment_snapshot = self.comment.create_snapshot()

        # ..and payment is created with all associated details..
        # self.tx = Transaction(
        #     comment=self.comment,
        #     snapshot=self.comment_snapshot,
        #     hour_price=VALUE['hour_price_snapshot'],
        #     currency_price=VALUE['currency_price_snapshot'],
        #
        #     payment_amount=self.AMOUNT_TO_PAY_DOER,
        #     payment_currency=CURRENCY,
        #     payment_recipient=self.doer,
        #     payment_sender=self.investor,
        #     hour_unit_cost=Decimal(1.)/VALUE['in_hours'],
        # )
        # self.tx.save()

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

        # Testing condition:
        self.assertTrue(
            (ContributionCertificate.objects.filter(transaction=self.tx).first().matched_hours-Decimal(0.1)) < Decimal('1E-28')
        )

        # The balance (score) of user is defined as sum of all contributions!
        self.assertEqual(
            Decimal('0.1'),
            ContributionCertificate.objects.filter(
                received_by=self.doer).aggregate(
                    total=Sum('matched_hours')
                         )['total']
        )

        # The balance (score) of user is defined as sum of all contributions!
        self.assertEqual(
            Decimal('0.1'),
            ContributionCertificate.objects.filter(
                received_by=self.investor).aggregate(
                    total=Sum('matched_hours')
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


        self.assertEqual(
            1,
            1
        )

    def test_future_investment_one_investor(self):
        """
        DOER
                                     8.0 ĥ
        [---------------------------------------------------------]

        INVESTOR

          1.0 ḥ
        [-------]

        CONTRIBUTIONS
        [-------]
        """
        self.assertEqual(
            1,
            1
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
        [------------][-------------]
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
        [--------][--------][-------------------------------------]
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
        [--------][--][----][-------------------------------------]

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

