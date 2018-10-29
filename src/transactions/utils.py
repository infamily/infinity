import json
import urllib
from bigchaindb_driver import BigchainDB

from django.core import serializers
from django.conf import settings

from users.models import CryptoKeypair


# HOUR_PRICE_SOURCES = {
#     'FRED': 'https://api.stlouisfed.org/fred/series/observations?series_id=CES0500000003&api_key=0a90ca7b5204b2ed6e998d9f6877187e&limit=1&sort_order=desc&file_type=json'
# }

# CURRENCY_PRICE_SOURCES = {
#     'FIXER': 'https://api.fixer.io/latest?base=eur'
# }


def instance_to_save_dict(instance):
    return json.loads(
        serializers.serialize(
            'json', [instance], ensure_ascii=False)[1:-1]
    )


def blockchain_save(user, data, blockchain=False):

    if settings.IPDB_APP_ID and settings.IPDB_APP_KEY:
        headers = {
            'app_id': settings.IPDB_APP_ID,
            'app_key': settings.IPDB_APP_KEY
        }
        bdb = BigchainDB(
            settings.IPDB_API_ROOT,
            headers=headers
        )
    else:
        bdb = BigchainDB(
            settings.IPDB_API_ROOT
        )

    if blockchain in dict(CryptoKeypair.KEY_TYPES).keys():

        cryptokey_qs = CryptoKeypair.objects.filter(
            user=user,
            type=blockchain,
            private_key__isnull=False
        )

        if not cryptokey_qs.exists():
            keypair = CryptoKeypair.objects.make_one(user=user)
            keypair.save()
        else:
            keypair = cryptokey_qs.last()

        tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=keypair.public_key,
            asset={'data': data},
        )

        signed_tx = bdb.transactions.fulfill(
            tx,
            private_keys=keypair.private_key
        )

        sent_tx = bdb.transactions.send_commit(signed_tx)

        txid = urllib.parse.urljoin(
            settings.IPDB_API_ROOT,
            'api/v1/transactions/{}'.format(
                sent_tx['id']
            )
        )

        return txid
