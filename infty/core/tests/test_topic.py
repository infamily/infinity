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

        # Then, investor comes in:
        self.investor = self.make_user('investor')
        self.investor.save()

        # And there is another investor:

        self.alice = self.make_user('alice')
        self.alice.save()

        # And there is another investor:

        self.bob = self.make_user('bob')
        self.bob.save()

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

    def test_simple_investment(self):
        """
        Investment amount is smaller than declared hours,
        and there is just one investor.
        """

        # Investor decides that he wants to invest into 0.2 of claimed time,
        # he sees the "(1.5 h) invest" button, and clicks it.
        WANT_TO_CREATE_AMOUNT_HOUR_SHARES = Decimal(0.2) # (h)

        # Let's say he has chosen the currency 'EUR':
        CHOSEN_CURRENCY = Currency.objects.get(label='EUR')
        CURRENCY_VALUE, h_obj, c_obj = CHOSEN_CURRENCY.in_hours(objects=True)

        # Then, we can we display the amount that needs to be payed:
        self.AMOUNT_TO_PAY_DOER = WANT_TO_CREATE_AMOUNT_HOUR_SHARES / CURRENCY_VALUE

        self.assertEqual(
            self.AMOUNT_TO_PAY_DOER,
            Decimal(0.2) * (Decimal(26.25)/Decimal(1.1729))
        )

        # Then, if all is good, the comment snapshot is saved.. 
        self.comment_snapshot = CommentSnapshot(
            comment=self.comment,
            text=self.comment.text,
            claimed_hours=self.comment.claimed_hours,
            assumed_hours=self.comment.assumed_hours,
            owner=self.comment.owner
        )
        self.comment_snapshot.save()

        # ..and payment is created:
        self.tx = Transaction(
            comment=self.comment,
            snapshot=self.comment_snapshot,
            currency_price=c_obj,
            hour_price=h_obj,

            payment_amount=self.AMOUNT_TO_PAY_DOER,
            payment_currency=CHOSEN_CURRENCY,
            payment_recipient=self.doer,
            payment_sender=self.investor,
            hour_unit_cost=Decimal(1.)/CURRENCY_VALUE,
        )
        self.tx.save()

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
