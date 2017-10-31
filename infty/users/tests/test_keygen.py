from test_plus.test import TestCase
from infty.users.models import CryptoKeypair
from bigchaindb_driver.crypto import generate_keypair

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
        alice = generate_keypair()
        IPDB = 0

        keypair = CryptoKeypair(
            user=self.trader,
            type=IPDB,
            private_key=alice.private_key,
            public_key=alice.public_key
        )
        keypair.save()

        self.assertEqual(
            keypair.public_key,
            alice.public_key
        )

        self.assertEqual(
            keypair.private_key,
            alice.private_key
        )





