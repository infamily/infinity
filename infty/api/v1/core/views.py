from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from infty.users.models import User, LanguageName

from infty.meta.models import Type, Instance

from infty.core.models import Topic, Comment

from infty.api.v1.generic.viewsets import CustomViewSet

from infty.api.v1.core.serializers import (
    TypeSerializer,
    InstanceSerializer,
    TopicSerializer,
    CommentSerializer,

    UserBalanceSerializer,
    LanguageNameSerializer,
)

from infty.api.v1.generic.pagination_classes import (
    StandardResultsSetPagination,
    LargeResultsSetPagination
)

from infty.api.v1.core.filters import TopicFilter


class TypeViewSet(CustomViewSet):

    serializer_class = TypeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Type.objects.all()

    def get_queryset(self):
        qs = super(TypeViewSet, self).get_queryset()

        lang = self.request.query_params.get('lang', None)

        if lang:
            return qs.filter(languages__contains=[lang])

        return qs


class InstanceViewSet(CustomViewSet):

    serializer_class = InstanceSerializer
    queryset = Instance.objects.all()


class TopicViewSet(CustomViewSet):

    serializer_class = TopicSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Topic.objects.all()
    search_fields = ['title']
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_class = TopicFilter

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super(TopicViewSet, self).get_queryset()

        TYPE = self.request.query_params.get('type', None)

        if TYPE:
            qs = qs.filter(type=TYPE)

        lang = self.request.query_params.get('lang', None)

        if lang:
            return qs.filter(languages__contains=[lang])

        return qs


class CommentViewSet(CustomViewSet):

    serializer_class = CommentSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    search_fields = ['text']
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)

    filter_fields = ('topic',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super(CommentViewSet, self).get_queryset()

        lang = self.request.query_params.get('lang', None)

        if lang:
            return qs.filter(languages__contains=[lang])

        return qs


@permission_classes((IsAuthenticatedOrReadOnly,))
class UserBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)

    filter_fields = ('username', 'id',)

    serializer_class = UserBalanceSerializer
    queryset = User.objects.all()


@permission_classes((IsAuthenticatedOrReadOnly,))
class LanguageNameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageNameSerializer
    queryset = LanguageName.objects.all()
