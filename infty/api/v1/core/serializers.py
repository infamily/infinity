from langsplit import splitter

from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from infty.meta.models import (
    Type,
    Instance,
)
from infty.core.models import (
    Topic,
    Comment,
)
from infty.transactions.models import (
    Currency, Transaction, Interaction, TopicSnapshot, CommentSnapshot,
    HourPriceSnapshot, CurrencyPriceSnapshot, ContributionCertificate)
from infty.users.models import (User, LanguageName)

from infty.api.v1.core.fields import LangSplitField, UserField


class TypeSerializer(serializers.HyperlinkedModelSerializer):
    name = LangSplitField(required=True)
    definition = LangSplitField(required=True)

    class Meta:
        model = Type
        extra_kwargs = {'url': {'view_name': 'api:v1:core:type-detail'}}
        fields = ('url', 'name', 'definition', 'source', 'languages')


class InstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instance
        extra_kwargs = {'url': {'view_name': 'api:v1:core:instance-detail'}}
        fields = ('url', 'role', 'description', 'languages')


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    title = LangSplitField(required=True)
    body = LangSplitField(required=False)
    type = serializers.ChoiceField(choices=Topic.TOPIC_TYPES, required=False)
    owner = UserField(read_only=True)
    editors = serializers.ReadOnlyField(
        source='editors.username', read_only=True)
    parents = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='api:v1:core:topic-detail',
        queryset=Topic.objects.all(),
        required=False)

    class Meta:
        model = Topic
        extra_kwargs = {'url': {'view_name': 'api:v1:core:topic-detail'}}
        fields = ('id', 'url', 'type', 'title', 'body', 'owner', 'editors',
                  'parents', 'categories', 'languages', 'is_draft',
                  'blockchain')


class CommentSerializer(serializers.HyperlinkedModelSerializer):

    text = LangSplitField(required=True)
    topic = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:topic-detail', queryset=Topic.objects.all())
    owner = UserField(read_only=True)

    def get_text(self, obj):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(obj.text)
            return split.get(lang) or 'languages: {}'.format(
                list(split.keys()))

        return obj.text

    class Meta:
        model = Comment
        extra_kwargs = {'url': {'view_name': 'api:v1:core:comment-detail'}}
        fields = ('id', 'url', 'topic', 'text', 'claimed_hours',
                  'assumed_hours', 'owner', 'languages', 'matched', 'donated',
                  'remains', 'parent', 'blockchain')


class TopicSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    topic = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = TopicSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:core:topic_snapshot-detail'}}
        fields = ('id', 'created_date', 'topic', 'data', 'blockchain',
                  'blockchain_tx')


class CommentSnapshotSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:comment-detail', queryset=Comment.objects.all())

    class Meta:
        model = CommentSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:core:comment_snapshot-detail'}}
        fields = ('id', 'created_date', 'comment', 'data', 'blockchain',
                  'blockchain_tx')


class HourPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HourPriceSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:core:hourprice_snapshot-detail'}}
        fields = ('id', 'name', 'base', 'endpoint', 'data')


class CurrencyPriceSnapshotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CurrencyPriceSnapshot
        extra_kwargs = {'url': {'view_name': 'api:v1:core:currencyprice_snapshot-detail'}}
        fields = ('id', 'name', 'base', 'endpoint', 'data')


class CurrencyListSerializer(serializers.HyperlinkedModelSerializer):

    hour_price = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:hourpricesnapshot-detail',
        queryset=HourPriceSnapshot.objects.all())
    currency_price = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:currencypricesnapshot-detail',
        queryset=CurrencyPriceSnapshot.objects.all())

    class Meta:
        model = Currency
        extra_kwargs = {'url': {'view_name': 'api:v1:core:currency-detail'}}
        fields = ('id', 'label', 'in_hours', 'hour_price', 'currency_price')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:interaction-detail',
        queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField(
        queryset=CommentSnapshot.objects.all())

    class Meta:
        model = Interaction
        extra_kwargs = {'url': {'view_name': 'api:v1:core:interaction-detail'}}
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
        extra_kwargs = {'url': {'view_name': 'api:v1:core:comment-detail'}}
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
        extra_kwargs = {'url': {'view_name': 'api:v1:core:transaction-detail'}}
        fields = ('url', 'comment', 'snapshot', 'hour_price', 'currency_price',
                  'payment_amount', 'payment_currency', 'payment_recipient',
                  'payment_sender', 'hour_unit_cost', 'donated_hours',
                  'matched_hours')


class ContributionSerializer(serializers.HyperlinkedModelSerializer):

    transaction = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:transaction-detail',
        queryset=Transaction.objects.all())
    interaction = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:interaction-detail',
        queryset=Interaction.objects.all())
    comment_snapshot = serializers.HyperlinkedRelatedField(
        view_name='api:v1:core:commentsnapshot-detail',
        queryset=CommentSnapshot.objects.all())
    received_by = UserField(read_only=True)

    class Meta:
        model = ContributionCertificate
        extra_kwargs = {'url': {'view_name': 'api:v1:core:contribution-detail'}}
        fields = ('type', 'url', 'interaction', 'transaction', 'received_by',
                  'comment_snapshot', 'broken', 'parent')


class UserBalanceSerializer(serializers.HyperlinkedModelSerializer):

    balance = serializers.SerializerMethodField('matched')
    contributions = serializers.SerializerMethodField('contribution_certificates')

    def matched(self, obj):
        return ContributionCertificate.user_matched(obj)

    def contribution_certificates(self, obj):
        request = self.context['request']
        protocol = 'http{}://'.format('s' if request.is_secure() else '')
        domain = request.META.get('HTTP_HOST') or ''
        endpoint = reverse('api:v1:core:contributioncertificate-list')

        return "{}{}{}?received_by={}".format(protocol, domain, endpoint,
                                              obj.id)

    class Meta:
        model = User
        extra_kwargs = {'url': {'view_name': 'api:v1:core:user_balance-detail'}}
        fields = ('id', 'username', 'balance', 'contributions')


class LanguageNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LanguageName
        extra_kwargs = {'url': {'view_name': 'api:v1:core:language_name-detail'}}
        fields = ('lang', 'name', 'enabled')
