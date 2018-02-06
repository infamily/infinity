from django.core.urlresolvers import reverse
from langsplit import splitter
from rest_framework import serializers

from src.api.v1.core.fields import LangSplitField, UserField, CategoryNameField
from src.core.models import (
    Topic,
    Comment,
)
from src.meta.models import Type
from src.transactions.models import ContributionCertificate
from src.users.models import (User, LanguageName)


class TopicParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'url', 'type', 'title', 'body',
                  'languages', 'is_draft')


class TypeParentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('id', 'url', 'name', 'definition')


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    title = LangSplitField(required=True)
    body = LangSplitField(required=False)
    type = serializers.ChoiceField(choices=Topic.TOPIC_TYPES, required=False)
    owner = UserField(read_only=True)
    editors = serializers.ReadOnlyField(
        source='editors.username', read_only=True)
    parents = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='topic-detail',
        queryset=Topic.objects.all(),
        required=False)
    children = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='topic-detail',
        queryset=Topic.objects.all(),
        required=False)

    categories = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='type-detail',
        queryset=Type.objects.categories(),
        required=False)

    # To assign categories as list of arbitrary strings
    categories_str = CategoryNameField(
        write_only=True,
        many=True,
        queryset=Type.objects.categories(),
        required=False
    )

    # To retrieve list of categories names (localized via langsplit)
    categories_names = CategoryNameField(
        read_only=True,
        many=True,
        source='categories',
    )

    class Meta:
        model = Topic
        fields = ('id', 'url', 'type', 'title', 'body', 'owner', 'editors',
                  'parents', 'children', 'categories', 'categories_str', 'categories_names', 'languages', 'is_draft',
                  'blockchain', 'matched')

    def create(self, validated_data):
        categories_str = validated_data.pop('categories_str', [])
        validated_data['categories'].extend(categories_str)
        return super(TopicSerializer, self).create(validated_data)


class CommentSerializer(serializers.HyperlinkedModelSerializer):

    text = LangSplitField(required=True)
    topic = serializers.HyperlinkedRelatedField(
        view_name='topic-detail', queryset=Topic.objects.all())
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
        fields = ('id', 'url', 'topic', 'text', 'claimed_hours',
                  'assumed_hours', 'owner', 'languages', 'matched', 'donated',
                  'remains', 'parent', 'blockchain')


class UserBalanceSerializer(serializers.HyperlinkedModelSerializer):

    balance = serializers.SerializerMethodField('matched')
    contributions = serializers.SerializerMethodField('contribution_certificates')

    def matched(self, obj):
        return ContributionCertificate.user_matched(obj)

    def contribution_certificates(self, obj):
        request = self.context['request']
        protocol = 'http{}://'.format('s' if request.is_secure() else '')
        domain = request.META.get('HTTP_HOST') or ''
        endpoint = reverse('contributioncertificate-list')

        return "{}{}{}?received_by={}".format(protocol, domain, endpoint,
                                              obj.id)

    class Meta:
        model = User
        fields = ('id', 'username', 'balance', 'contributions')


class LanguageNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LanguageName
        fields = ('lang', 'name', 'enabled')
