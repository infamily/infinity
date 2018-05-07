from rest_framework import serializers

from src.trade.models import Payment, Reserve


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'url', 'request', 'response', 'platform', 'provider', 'topic']


class ReserveListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reserve
        fields = ['id', 'url', 'hours', 'payment', 'transaction', 'currency', 'amount', 'user', 'topic']
