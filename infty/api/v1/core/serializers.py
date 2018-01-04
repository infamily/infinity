from langsplit import splitter

from django.core.urlresolvers import reverse
from rest_framework import serializers

from infty.meta.models import (
    Type,
    Instance,
)
from infty.core.models import (
    Topic,
    Comment,
)
from infty.transactions.models import ContributionCertificate
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


class UserBalanceSerializer(serializers.HyperlinkedModelSerializer):

    balance = serializers.SerializerMethodField('matched')
    contributions = serializers.SerializerMethodField('contribution_certificates')

    def matched(self, obj):
        return ContributionCertificate.user_matched(obj)

    def contribution_certificates(self, obj):
        request = self.context['request']
        protocol = 'http{}://'.format('s' if request.is_secure() else '')
        domain = request.META.get('HTTP_HOST') or ''
        endpoint = reverse('api:v1:transactions:contributioncertificate-list')

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
