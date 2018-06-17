from test_plus.test import TestCase
from users.models import CryptoKeypair

class TestKeygen(TestCase):

    def setUp(self):
        self.trader = self.make_user('trader')

    def test_keypair_count(self):
        self.assertEqual(
            CryptoKeypair.objects.count(),
            1
        )

    def test_name_correct(self):
        self.assertEqual(
            self.trader.username,
            'Trader@75A23485'
        )

    def test_create_ipdb_keypair(self):

        self.assertEqual(
            True,
            CryptoKeypair.objects.filter(
                user=self.trader).count() == 1
        )

        self.assertEqual(
            True,
            len(
                CryptoKeypair.objects.filter(
                    user=self.trader).first().private_key) > 5
        )

    def test_create_ipdb_keypair_not_saving_private_key(self):
        keypair = CryptoKeypair.objects.make_one(
            user=self.trader, save_private=False
        )
        keypair.save()

        self.assertTrue(
            len(keypair._tmp_private_key) > 10
        )

        self.assertEqual(
            CryptoKeypair.objects.filter(user=self.trader).count(),
            2
        )

    def test_create_ipdb_keypair_with_saving_private_key(self):
        keypair = CryptoKeypair.objects.make_one(user=self.trader)
        keypair.save()

        self.assertTrue(
            keypair._tmp_private_key is None
        )

        self.assertEqual(
            CryptoKeypair.objects.filter(user=self.trader).count(),
            2
        )
