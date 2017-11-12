from rest_framework import serializers
from infty.core.models import (
    Type,
    Item,
    Topic,
    Comment,
    Currency,
    Transaction,
    Interaction,
    CommentSnapshot,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
    ContributionCertificate
)
from infty.users.models import User

from langsplit import splitter


class TypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Type
        fields = ('url', 'definition', 'source', 'languages')


class ItemSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Item
        fields = ('url', 'type', 'description', 'languages')


class LangSplitField(serializers.CharField):
    """Langsplit CharField"""
    def to_internal_value(self, data):
        return super(LangSplitField, self).to_internal_value(data)

    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(value, title=True)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return value


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    title = LangSplitField(required=True)
    body = LangSplitField(required=True)
    type = serializers.ChoiceField(choices=Topic.TOPIC_TYPES, required=True)
    owner = serializers.ReadOnlyField(source='owner.username', read_only=True)
    editors = serializers.ReadOnlyField(source='editors.username', read_only=True)
    parents = serializers.HyperlinkedRelatedField(many = True, view_name='topic-detail',
        queryset=Topic.objects.all(), required=False)

    def get_title(self, obj):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(obj.title, title=True)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return obj.title

    def get_body(self, obj):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(obj.body)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return obj.body

    class Meta:
        model = Topic
        fields = ('url', 'type', 'title', 'body', 'owner', 'editors', 'parents')



class CommentSerializer(serializers.HyperlinkedModelSerializer):

    text = serializers.SerializerMethodField()
    topic = serializers.HyperlinkedRelatedField(view_name='topic-detail', queryset=Topic.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')

    def get_text(self, obj):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(obj.text)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return obj.text

    class Meta:
        model = Comment
        fields = ('url', 'topic', 'text', 'claimed_hours', 'assumed_hours', 'owner')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(view_name='interaction-detail', queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField (queryset=CommentSnapshot.objects.all())

    class Meta:
        model = Interaction
        fields = ('url', 'comment', 'snapshot', 'claimed_hours_to_match')


class TransactionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(view_name='comment-detail', queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField (queryset=CommentSnapshot.objects.all())
    hour_price = serializers.PrimaryKeyRelatedField(queryset=HourPriceSnapshot.objects.all())
    currency_price = serializers.PrimaryKeyRelatedField(queryset=CurrencyPriceSnapshot.objects.all())
    payment_currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    payment_recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    payment_sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = ('url', 'comment', 'snapshot', 'hour_price', 'currency_price',
            'payment_amount', 'payment_currency', 'payment_recipient',
            'payment_sender', 'hour_unit_cost', 'donated_hours', 'matched_hours')


class ContributionSerializer(serializers.HyperlinkedModelSerializer):

    transaction = serializers.HyperlinkedRelatedField(view_name='transaction-detail', queryset=Transaction.objects.all())
    comment_snapshot = serializers.HyperlinkedRelatedField(view_name='comment-snapshot-detail', queryset=CommentSnapshot.objects.all())
    received_by = serializers.ReadOnlyField(source='received_by.username')

    class Meta:
        model = Interaction
        fields = ('url', 'transaction', 'comment_snapshot', 'received_by')
