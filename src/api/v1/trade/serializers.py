from rest_framework import serializers

from src.trade.models import Payment


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['request', 'response', 'platform', 'provider']
