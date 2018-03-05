# API tests at: src/api/tests/test_api.py

import json
import responses
from decimal import Decimal

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
            - {14.5},{?0.5} for coming up with basic class structure,
            """,
            owner=self.doer
        )
        self.comment.save()

    def test_comment_parsed_values(self):

        self.assertEqual(
            self.comment.claimed_hours,
            14.5
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

    @responses.activate
    def test_user_can_change_reserve(self):
        # Initially, quota should be as defined in settings.
        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            4.
        )
        # Initially, reserve should be zero:
        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            0.
        )

        # After payment, reserve should be more than zero:
        payment = Payment.objects.create(
            request={
                "amount": "150",
                "currency": "usd",
            },
            platform=0, provider=0, owner=self.investor
        )

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            Decimal('5.71428571')
        )
        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            4.
        )

        # Investment should use up the hours, first from quota,
        tx = self.comment.invest(1., 'eur', self.investor)

        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            3.
        )

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            Decimal('5.71428571')
        )

        # Try more
        tx = self.comment.invest(3., 'eur', self.investor)

        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            0.
        )

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            Decimal('5.71428571')
        )

        # Try more
        tx = self.comment.invest(1., 'eur', self.investor)

        self.assertEqual(
            Transaction.user_quota_remains_today(self.investor),
            0.
        )

        self.assertEqual(
            Reserve.user_reserve_remains(self.investor),
            Decimal('4.71428571')
        )

        credit = Transaction.user_quota_remains_today(self.investor) + \
            Reserve.user_reserve_remains(self.investor)

        self.assertEqual(
            credit,
            Decimal('4.71428571')
        )

        # Remaining credit should be such:
        self.assertEqual(
            credit,
            (Decimal(4.) + Decimal('5.71428571')) - \
            (Decimal(1.) + Decimal(3.) + Decimal(1.))
        )

        # Comment should still have remaining 10. hrs
        self.assertEqual(
            self.comment.remains(),
            Decimal(14.5)+Decimal(0.5) - \
            (Decimal(1.) + Decimal(3.) + Decimal(1.))
        )

        # If we try invest more than available, we should fail:

        # Try more
        tx = self.comment.invest(4.9, 'eur', self.investor)

        # Not created:
        self.assertEqual(
            tx,
            None
        )

        # But we should be able to invest exactly the remainder:

        tx = self.comment.invest(Decimal('4.71428571'), 'eur', self.investor)

        self.assertEqual(
            self.comment.remains(),
            Decimal('5.28571428')
        )

        credit = Transaction.user_quota_remains_today(self.investor) + \
            Reserve.user_reserve_remains(self.investor)

        self.assertEqual(
            credit,
            0.
        )

        # Testing with real endpoints.
        # payment = Payment.objects.create(
        #     request={
        #         "amount": "150",
        #         "currency": "usd",
        #         "card": "tok_visa",
        #         "description": "me@myself.com"
        #     },
        #     platform=1, provider=1, owner=self.investor
        # )
