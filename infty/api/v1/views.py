from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, generics, views

from infty.core.models import Topic, Comment, CommentSnapshot, Transaction
from infty.api.v1.serializers import *

from rest_framework import viewsets, mixins
from rest_framework import filters

from .pagination_classes import StandardResultsSetPagination


class CustomViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):
    """
    A viewset that provides default `create()`, `retrieve()`,
    `update()`, `partial_update()` and `list()` actions.
    We don't use `destroy()` yet.
    """
    pass


class TopicViewSet(CustomViewSet):

    serializer_class = TopicSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Topic.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super(TopicViewSet, self).get_queryset()

        lang = self.request.query_params.get('lang', None)

        if lang:
            return qs.filter(languages__contains=[lang])

        return qs


class CommentViewSet(CustomViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    search_fields = ['text']
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super(CommentViewSet, self).get_queryset()

        lang = self.request.query_params.get('lang', None)

        if lang:
            return qs.filter(languages__contains=[lang])

        return qs


class TransactionViewSet(CustomViewSet):

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


