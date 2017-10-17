from rest_framework import serializers
from infty.core.models import (Topic, Comment, Transaction, CommentSnapshot,
    HourPriceSnapshot, CurrencyPriceSnapshot, Currency)
from infty.users.models import User


class TopicSerializer(serializers.HyperlinkedModelSerializer):

    type = serializers.ChoiceField(choices = Topic.TOPIC_TYPES, required=False)
    owner = serializers.ReadOnlyField(source='owner.username', read_only=True)
    editors = serializers.ReadOnlyField(source='editors.username', read_only=True)
    parents = serializers.HyperlinkedRelatedField(many = True, view_name='topic-detail', 
        queryset=Topic.objects.all(), required=False)

    class Meta:
        model = Topic
        fields = ('url', 'type', 'title', 'body', 'owner', 'editors', 'parents')


class CommentSerializer(serializers.HyperlinkedModelSerializer):

    topic = serializers.HyperlinkedRelatedField(view_name='topic-detail', queryset=Topic.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = ('url', 'topic', 'text', 'claimed_hours', 'assumed_hours', 'owner')


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
