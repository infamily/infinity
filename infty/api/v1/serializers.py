from langsplit import splitter

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from infty.core.models import (
    Type,
    Instance,
    Topic,
    Comment,
)
from infty.transactions.models import (
    Currency,
    Transaction,
    Interaction,
    CommentSnapshot,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
    ContributionCertificate
)
from infty.users.models import User


class LangSplitField(serializers.CharField):
    """Langsplit CharField"""
    def to_internal_value(self, data):
        return super(LangSplitField, self).to_internal_value(data)

    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        if lang and value:
            split = splitter.split(value, title=True)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return value


class TypeSerializer(serializers.HyperlinkedModelSerializer):
    name = LangSplitField(required=True)
    definition = LangSplitField(required=True)

    class Meta:
        model = Type
        fields = ('url', 'name', 'definition', 'source', 'languages')


class InstanceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Instance
        fields = ('url', 'role', 'description', 'languages')


class CategoriesField(serializers.RelatedField):
    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        item = {
            "id": value.pk,
            "name": value.name
        }

        if lang:

            split = splitter.split(value.name, title=True)
            item["name"] = split.get(lang) or \
                'languages: {}'.format(list(split.keys()))

        return item


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    title = LangSplitField(required=True)
    body = LangSplitField(required=False)
    type = serializers.ChoiceField(choices=Topic.TOPIC_TYPES, required=False)
    owner = serializers.ReadOnlyField(source='owner.username', read_only=True)
    editors = serializers.ReadOnlyField(source='editors.username', read_only=True)
    parents = serializers.HyperlinkedRelatedField(
        many = True,
        view_name='topic-detail',
        queryset=Topic.objects.all(),
        required=False
    )

    class Meta:
        model = Topic
        fields = ('id', 'url', 'type', 'title', 'body', 'owner', 'editors', 'parents', 'categories', 'languages', 'is_draft')


class CommentOwner(serializers.CharField):

    def to_representation(self, value):
        return {"id": value.pk, "username": value.username}


class CommentSerializer(serializers.HyperlinkedModelSerializer):

    text = LangSplitField(required=True)
    topic = serializers.HyperlinkedRelatedField(view_name='topic-detail', queryset=Topic.objects.all())
    owner = CommentOwner(read_only=True)

    def get_text(self, obj):
        lang = self.context['request'].query_params.get('lang')

        if lang:
            split = splitter.split(obj.text)
            return split.get(lang) or 'languages: {}'.format(list(split.keys()))

        return obj.text

    class Meta:
        model = Comment
        fields = ('id', 'url', 'topic', 'text', 'claimed_hours', 'assumed_hours', 'owner', 'languages', 'matched', 'donated', 'remains', 'parent')


class InteractionSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(view_name='interaction-detail', queryset=Comment.objects.all())
    snapshot = serializers.PrimaryKeyRelatedField (queryset=CommentSnapshot.objects.all())

    class Meta:
        model = Interaction
        fields = ('url', 'comment', 'snapshot', 'claimed_hours_to_match')


class TransactionCreateSerializer(serializers.HyperlinkedModelSerializer):

    comment = serializers.HyperlinkedRelatedField(view_name='comment-detail', queryset=Comment.objects.all())
    payment_currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    payment_sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = ('comment', 'payment_amount', 'payment_currency', 'payment_sender')

    def create(self, validated_data):
        comment = validated_data.get('comment')
        amount = validated_data['payment_amount']
        currency_label = validated_data['payment_currency'].label
        sender = validated_data['payment_sender']

        tx = comment.invest(
            hour_amount=amount,
            payment_currency_label=currency_label,
            investor=sender,
        )

        if not tx:
            raise ValidationError('Bad data')

        return tx


class TransactionListSerializer(serializers.HyperlinkedModelSerializer):

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
    # comment_snapshot = serializers.HyperlinkedRelatedField(view_name='comment-detail', queryset=CommentSnapshot.objects.all())
    comment = serializers.HyperlinkedRelatedField(view_name='comment-detail', queryset=CommentSnapshot.objects.all())
    received_by = serializers.ReadOnlyField(source='received_by.username')

    class Meta:
        model = Interaction
        fields = ('url', 'transaction', 'comment', 'received_by')
