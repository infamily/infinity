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
        view_name='hourpricesnapshot-detail',
        queryset=HourPriceSnapshot.objects.all())
    currency_price = serializers.HyperlinkedRelatedField(
        view_name='currencypricesnapshot-detail',
        queryset=CurrencyPriceSnapshot.objects.all())

    class Meta:
        model = Currency
        fields = ('id', 'label', 'in_hours', 'hour_price', 'currency_price')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='transactions:interaction-detail',
        queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField(
        queryset=CommentSnapshot.objects.all())

    class Meta:
        model = Interaction
        fields = ('url', 'comment', 'snapshot', 'claimed_hours_to_match')


class TransactionCreateSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='comment-detail', queryset=Comment.objects.all())
    payment_currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all())
    payment_sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Transaction
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
        view_name='comment-detail', queryset=Comment.objects.all())
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
        fields = ('url', 'comment', 'snapshot', 'hour_price', 'currency_price',
                  'payment_amount', 'payment_currency', 'payment_recipient',
                  'payment_sender', 'hour_unit_cost', 'donated_hours',
                  'matched_hours')


class ContributionSerializer(serializers.HyperlinkedModelSerializer):

    transaction = serializers.HyperlinkedRelatedField(
        view_name='transaction-detail',
        queryset=Transaction.objects.all())
    interaction = serializers.HyperlinkedRelatedField(
        view_name='interaction-detail',
        queryset=Interaction.objects.all())
    comment_snapshot = serializers.HyperlinkedRelatedField(
        view_name='commentsnapshot-detail',
        queryset=CommentSnapshot.objects.all())
    received_by = UserField(read_only=True)

    class Meta:
        model = ContributionCertificate
        fields = ('type', 'url', 'interaction', 'transaction', 'received_by',
                  'comment_snapshot', 'broken', 'parent')


class TopicSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    topic = serializers.HyperlinkedRelatedField(
        view_name='comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = TopicSnapshot
        fields = ('id', 'created_date', 'topic', 'data', 'blockchain',
                  'blockchain_tx')


class CommentSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = CommentSnapshot
        fields = ('id', 'created_date', 'comment', 'data', 'blockchain',
                  'blockchain_tx')


class HourPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    base = serializers.HyperlinkedIdentityField(view_name="currency-detail")

    class Meta:
        model = HourPriceSnapshot
        fields = ('id', 'url', 'name', 'base', 'endpoint', 'data')


class CurrencyPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    base = serializers.HyperlinkedIdentityField(view_name="currency-detail")

    class Meta:
        model = CurrencyPriceSnapshot
        fields = ('id', 'name', 'base', 'endpoint', 'data')
