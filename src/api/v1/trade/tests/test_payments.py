import json
from rest_framework.test import APITestCase
from rest_framework import status

from django.core.urlresolvers import reverse
from src.users.models import User


class APITestCaseAuthorizedUser(APITestCase):
    def setUp(self):
        self.username = "testuser"
        self.email = "test@test.com"
        self.password = "password_for_test"
        self.testuser = User.objects.create_user(
            self.username, self.email, is_superuser=False, is_staff=False)
        self.testuser.set_password(self.password)
        self.testuser.save()

        self.client.force_authenticate(user=User.objects.first())

    def test_create_payment(self):

#         payment_request = json.loads('''{
#   "amount": "10000",
#   "currency": "usd",
#   "description": "me@myself.com",
#   "card": "tok_visa"
# }''')

        payment_request = json.loads('''{
  "amount": "10000",
  "currency": "usd",
  "description": "me@myself.com",
  "card": {
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2019,
    "cvc": "123"
}
}''')

        payment_response = json.loads('''{
  "id": "ch_1C1eKALB0t3JwecP9pBPWln7",
  "object": "charge",
  "amount": 10000,
  "amount_refunded": 0,
  "application": null,
  "application_fee": null,
  "balance_transaction": "txn_1C1eKALB0t3JwecPoVAThbBN",
  "captured": true,
  "created": 1520098750,
  "currency": "usd",
  "customer": null,
  "description": "me@myself.com",
  "destination": null,
  "dispute": null,
  "failure_code": null,
  "failure_message": null,
  "fraud_details": {
  },
  "invoice": null,
  "livemode": false,
  "metadata": {
  },
  "on_behalf_of": null,
  "order": null,
  "outcome": {
    "network_status": "approved_by_network",
    "reason": null,
    "risk_level": "normal",
    "seller_message": "Payment complete.",
    "type": "authorized"
  },
  "paid": true,
  "receipt_email": null,
  "receipt_number": null,
  "refunded": false,
  "refunds": {
    "object": "list",
    "data": [
    ],
    "has_more": false,
    "total_count": 0,
    "url": "/v1/charges/ch_1C1eKALB0t3JwecP9pBPWln7/refunds"
  },
  "review": null,
  "shipping": null,
  "source": {
    "id": "card_1C1eKALB0t3JwecPU1rM1p3V",
    "object": "card",
    "address_city": null,
    "address_country": null,
    "address_line1": null,
    "address_line1_check": null,
    "address_line2": null,
    "address_state": null,
    "address_zip": null,
    "address_zip_check": null,
    "brand": "Visa",
    "country": "US",
    "customer": null,
    "cvc_check": null,
    "dynamic_last4": null,
    "exp_month": 8,
    "exp_year": 2019,
    "fingerprint": "rcVLLEdEK8JnLaJu",
    "funding": "credit",
    "last4": "4242",
    "metadata": {
    },
    "name": null,
    "tokenization_method": null
  },
  "source_transfer": null,
  "statement_descriptor": null,
  "status": "succeeded",
  "transfer_group": null
}''')


        self.assertEqual(self.username, 'testuser')

        #TODO: Later use responses library to finalize

        # response = self.client.post(
        #     reverse('payment-list'),
        #     {'request': payment_request},
        #     format="json"
        # )
        #
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
