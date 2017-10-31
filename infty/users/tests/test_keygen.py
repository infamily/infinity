from test_plus.test import TestCase
from infty.users.models import CryptoKeypair

class TestKeygen(TestCase):

    def setUp(self):
        self.trader = self.make_user('trader')
        self.trader.save()

    def test_name_correct(self):
        self.assertEqual(
            self.trader.username,
            'trader'
        )

    def test_create_ipdb_key(self):

        self.assertEqual(
            True,
            CryptoKeypair.objects.filter(user=self.trader).count() > 0
        )

        self.assertEqual(
            True,
            len(
                CryptoKeypair.objects.filter(
                    user=self.trader).first().private_key) > 5
        )
