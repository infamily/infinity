# Create your tests here.
import requests
from decimal import Decimal
from test_plus.test import TestCase
from infty.core.models import (Topic,
                               Comment,
                               HourPriceSnapshot,
                               CommentSnapshot,
                               Transaction,
                               ContributionCertificate)
from infty.core.models import CURRENCY_IDS

class TestTopic(TestCase):

    def setUp(self):

        # Let's say we have a user 'thinker'..
        thinker = self.make_user('thinker')
        thinker.save()

        # ..who writes a post:
        self.topic = Topic.objects.create(
            title='Improve test module',
            body='implement class that autogenerates users',
            owner=thinker,
        )
        self.topic.save()

        # Then, we have a user 'doer'..
        doer = self.make_user('doer')
        doer.save()

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
            owner=doer
        )
        self.comment.save()

        # Then, investor comes in:
        investor = self.make_user('investor')
        investor.save()

        # ..who decides that he wants to invest into 0.2 of claimed time,
        # he sees the "(1.5 h) INVEST" button, and clicks it.

        WANT_TO_CREATE_AMOUNT_SHARES = 0.2 # (h)

        # The latest price of hour in currency chosen in the form is retrieved and saved in HourPriceSnapshot
        FORM_CURRENCY = 'EUR'
        CURRENCY_ID = CURRENCY_IDS[FORM_CURRENCY]

        HOUR_PRICE_ENDPOINT = 'https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json'
        EXCHANGE_ENDPOINT = 'https://api.fixer.io/latest?base={}'.format(FORM_CURRENCY.lower())

        hour_price_in_usd = Decimal(26.25)
        # hour_price_in_usd = requests.get(HOUR_PRICE_ENDPOINT).json().get('observations')[0]['value']
        usd_price_in_FORM_CURRENCY = Decimal(1.1694)
        # usd_price_in_FORM_CURRENCY = requests.get(EXCHANGE_ENDPOINT).json().get('rates')['USD']

        self.hour_price = HourPriceSnapshot(
            hour_price_source='https://fred.stlouisfed.org/series/CES0500000003',
            hour_price=Decimal(hour_price_in_usd),
            hour_price_currency=CURRENCY_IDS['USD'],

            currency_exchange_source='https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html',
            target_currency=CURRENCY_ID,
            unit_of_target_currency_in_hour_price_currency=Decimal(usd_price_in_FORM_CURRENCY),
            value=Decimal(hour_price_in_usd)/Decimal(usd_price_in_FORM_CURRENCY)
        )
        self.hour_price.save()

        # Then, we can we display the amount that needs to be
        # payed to generate the (0.2 h) shares.
        # Decimal(0.2) * (Decimal(26.25)/Decimal(1.1694))

        self.AMOUNT_TO_PAY_DOER = Decimal(WANT_TO_CREATE_AMOUNT_SHARES) * self.hour_price.value

        # Then, if all is good, the comment snapshot and payment is created. 

        self.comment_snapshot = CommentSnapshot(
            comment=self.comment,
            text=self.comment.text,
            claimed_hours=self.comment.claimed_hours,
            assumed_hours=self.comment.assumed_hours,
            owner=self.comment.owner
        )
        self.comment_snapshot.save()

        self.tx = Transaction(
            comment=self.comment,
            snapshot=self.comment_snapshot,
            payment_amount=self.AMOUNT_TO_PAY_DOER,
            payment_currency=CURRENCY_ID,
            payment_recipient=doer,
            payment_sender=investor,
            hour_price_snapshot=self.hour_price,
            hour_price_in_payment_currency=self.hour_price.value,
        )
        self.tx.save()

        # As part of transaction, the ContributionCertificates
        # are generated to both parties - the doer, and investor.
        # For thinker -- wil add the option to auto-generate 
        # first comment with amount of time claimed to write the topic.



    def test_comment_parsed_values(self):

        self.assertEqual(
            self.comment.claimed_hours,
            1.5
        )

        self.assertEqual(
            self.comment.assumed_hours,
            6.5
        )

    def test_hour_price(self):

        self.assertEqual(
            self.hour_price.hour_price,
            Decimal(26.25)
        )

    def test_dollar_price(self):

        self.assertEqual(
            self.hour_price.unit_of_target_currency_in_hour_price_currency,
            Decimal(1.1694)
        )

    def test_amount_to_pay(self):
        """
        Computed amount to pay should be approx (0.2*26.25) usd in eur.
        """

        # AMT SHARES * (HOUR PRICE USD / USD for EUR)
        # Decimal(0.2) * (Decimal(26.25)/Decimal(1.1694))
        self.assertEqual(
            self.AMOUNT_TO_PAY_DOER,
            Decimal('4.489481785531041828085620537')
        )

    def test_matched_hours(self):
        """
        Matched hours is 0.2, as defined.
        """

        self.assertTrue(
            (self.tx.matched_hours-Decimal(0.2)) < Decimal('1E-28')
        )

    def test_contribution_certificates(self):
        """
        Doer and Investor gets equal amount as contributors.
        """

        self.assertTrue(
            (ContributionCertificate.objects.filter(transaction=self.tx).first().matched_hours-Decimal(0.1)) < Decimal('1E-28')
        )

    def test_contributor_balance(self):
        #ContributionCertificate.objects.filter(self.doer)
        pass

