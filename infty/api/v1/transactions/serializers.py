from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from infty.core.models import Comment
from infty.transactions.models import (
    Currency, Transaction, Interaction, TopicSnapshot, CommentSnapshot,
    HourPriceSnapshot, CurrencyPriceSnapshot, ContributionCertificate)

from infty.users.models import User

from infty.api.v1.core.fields import UserField


class CurrencyListSerializer(serializers.HyperlinkedModelSerializer):

    hour_price = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:hourpricesnapshot-detail',
        queryset=HourPriceSnapshot.objects.all())
    currency_price = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:currencypricesnapshot-detail',
        queryset=CurrencyPriceSnapshot.objects.all())

    class Meta:
        model = Currency
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:currency-detail'}}
        fields = ('id', 'label', 'in_hours', 'hour_price', 'currency_price')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:interaction-detail',
        queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField(
        queryset=CommentSnapshot.objects.all())

    class Meta:
        model = Interaction
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:interaction-detail'}}
        fields = ('url', 'comment', 'snapshot', 'claimed_hours_to_match')


class TransactionCreateSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:comment-detail', queryset=Comment.objects.all())
    payment_currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all())
    payment_sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Transaction
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:transaction-detail'}}
        fields = ('comment', 'payment_amount', 'payment_currency',
                  'payment_sender')

    def create(self, validated_data):
        comment = validated_data.get('comment')
        amount = validated_data['payment_amount']
        currency = validated_data['payment_currency']
        sender = validated_data['payment_sender']

        tx = comment.invest(
            hour_amount=amount,
            payment_currency_label=currency.label.lower(),
            investor=sender,
        )

        if not tx:
            raise ValidationError('Bad data')

        return tx


class TransactionListSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:comment-detail', queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField(
        queryset=CommentSnapshot.objects.all())
    hour_price = serializers.PrimaryKeyRelatedField(
        queryset=HourPriceSnapshot.objects.all())
    currency_price = serializers.PrimaryKeyRelatedField(
        queryset=CurrencyPriceSnapshot.objects.all())
    payment_currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all())
    payment_recipient = UserField(read_only=True)
    payment_sender = UserField(read_only=True)

    class Meta:
        model = Transaction
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:transaction-detail'}}
        fields = ('url', 'comment', 'snapshot', 'hour_price', 'currency_price',
                  'payment_amount', 'payment_currency', 'payment_recipient',
                  'payment_sender', 'hour_unit_cost', 'donated_hours',
                  'matched_hours')


class ContributionSerializer(serializers.HyperlinkedModelSerializer):

    transaction = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:transaction-detail',
        queryset=Transaction.objects.all())
    interaction = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:interaction-detail',
        queryset=Interaction.objects.all())
    comment_snapshot = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:commentsnapshot-detail',
        queryset=CommentSnapshot.objects.all())
    received_by = UserField(read_only=True)

    class Meta:
        model = ContributionCertificate
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:contribution-detail'}}
        fields = ('type', 'url', 'interaction', 'transaction', 'received_by',
                  'comment_snapshot', 'broken', 'parent')


class TopicSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    topic = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = TopicSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:topic_snapshot-detail'}}
        fields = ('id', 'created_date', 'topic', 'data', 'blockchain',
                  'blockchain_tx')


class CommentSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:transactions:comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = CommentSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:comment_snapshot-detail'}}
        fields = ('id', 'created_date', 'comment', 'data', 'blockchain',
                  'blockchain_tx')


class HourPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    base = serializers.HyperlinkedIdentityField(view_name="api:v1:transactions:currency-detail")

    class Meta:
        model = HourPriceSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:hourprice_snapshot-detail'}}
        fields = ('id', 'url', 'name', 'base', 'endpoint', 'data')


class CurrencyPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    base = serializers.HyperlinkedIdentityField(view_name="api:v1:transactions:currency-detail")

    class Meta:
        model = CurrencyPriceSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:transactions:currencyprice_snapshot-detail'}}
        fields = ('id', 'name', 'base', 'endpoint', 'data')
