# API tests at: src/api/tests/test_api.py

import json
from django.conf import settings

from test_plus.test import TestCase

from src.core.models import (
    Topic,
    Comment,
)

from src.trade.models import (
    Payment,
    Reserve
)

from src.transactions.models import (
    Currency,
    Transaction,
    HourPriceSnapshot,
    CurrencyPriceSnapshot
)


class TestReserve(TestCase):

    def setUp(self):
        # Let's say we have currencies:
        self.hur = Currency(label='hur'); self.hur.save()
        self.eur = Currency(label='eur'); self.eur.save()
        self.usd = Currency(label='usd'); self.usd.save()

        # And some currency prices:
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

        # Let's say we have a user 'thinker', 'doer' and 'investor'..
        self.thinker = self.make_user('thinker')
        self.thinker.save()
        self.doer = self.make_user('doer')
        self.doer.save()
        self.investor = self.make_user('investor')
        self.investor.save()

        # Let's say thinker writes a topic.
        self.topic = Topic.objects.create(
            title='Improve test module',
            body='implement class that autogenerates users',
            owner=self.thinker,
        )
        self.topic.save()

        # Let's say a doer writes a comment with declared hours,
        # more than available in daily quota day:

        self.comment = Comment(
            topic=self.topic,
            text="""
            - {10.5},{?0.5} for coming up with basic class structure,
            """,
            owner=self.doer
        )
        self.comment.save()

    def test_comment_parsed_values(self):

        self.assertEqual(
            self.comment.claimed_hours,
            10.5
        )

        self.assertEqual(
            self.comment.assumed_hours,
            0.5
        )

    def test_user_has_zero_reserve(self):

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            0.
        )

    def test_user_can_change_reserve(self):
        # quota = Transaction.user_quota_remains_today(sender)
        # reserve = Payment.user_reserve_remains(sender)

        payment = Payment.objects.create(
            request="{}", response="{}", platform=0, provider=0, success=True,
        )
        payment.save()

        rx = Reserve.objects.create(
            payment=payment,
            user=self.investor,
            hours=5.,
            hour_price=HourPriceSnapshot.objects.last(),
            currency_price=CurrencyPriceSnapshot.objects.last()
        )

        # After purchase, the reserve should be incre
        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            5.
        )

        # Initially, quota should be as defined in settings.
        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            settings.INVESTING_HOURS_DAILY_QUOTA # 4
        )

        # Investment should use up the hours, first from quota, then from reserve.
        tx = self.comment.invest(5., 'eur', self.investor)
        tx.save()

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            4.
        )
