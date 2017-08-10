from rest_framework import serializers
from infty.core.models import Topic, Comment, Transaction, CommentSnapshot


class TopicSerializer(serializers.HyperlinkedModelSerializer):

    type = serializers.ChoiceField(choices = Topic.TOPIC_TYPES)
    owner = serializers.ReadOnlyField(source='owner.username')
    editors = serializers.ReadOnlyField(source='editors.username')
    parents = serializers.HyperlinkedRelatedField(many = True, view_name='topic-detail', queryset=Topic.objects.all())

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
    snapshot = serializers.SlugRelatedField(slug_field='comment', read_only=True)
    hour_price = serializers.SlugRelatedField(slug_field='name', read_only=True)
    currency_price = serializers.SlugRelatedField(slug_field='name', read_only=True)
    payment_currency = serializers.SlugRelatedField(slug_field='label', read_only=True)
    payment_recipient = serializers.SlugRelatedField(slug_field='name', read_only=True)
    payment_sender = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Transaction
        fields = ('comment', 'snapshot', 'hour_price', 'currency_price',
            'payment_amount', 'payment_currency', 'payment_recipient',
            'payment_sender', 'hour_unit_cost', 'donated_hours', 'matched_hours')



