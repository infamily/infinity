from rest_framework import serializers

from src.trade.models import Payment, Reserve


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['request', 'response', 'platform', 'provider']


class ReserveListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reserve
        fields = ['hours', 'payment', 'transaction', 'currency', 'amount', 'user']
