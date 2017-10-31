from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, generics, views, schemas, response, renderers

from infty.core.models import (
    Topic,
    Comment,
    CommentSnapshot,
    Interaction,
    Transaction,
    ContributionCertificate
)
from infty.api.v1.serializers import *

from rest_framework import viewsets, mixins
from rest_framework import filters

from .pagination_classes import (
    StandardResultsSetPagination,
    LargeResultsSetPagination
)


schema_generator = schemas.SchemaGenerator(title='WeFindX API')

@api_view()
@renderer_classes([renderers.CoreJSONRenderer])
@permission_classes((IsAuthenticatedOrReadOnly,))
def schema_view(request):
    """
    Explicit schema view
    http://www.django-rest-framework.org/api-guide/schemas/#using-an-explicit-schema-view
    """
    schema = schema_generator.get_schema(request)
    return response.Response(schema)


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


class TypeViewSet(CustomViewSet):

    serializer_class = TypeSerializer
    queryset = Type.objects.all()


class ItemViewSet(CustomViewSet):

    serializer_class = ItemSerializer
    queryset = Item.objects.all()


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
    pagination_class = LargeResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
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


class InteractionViewSet(CustomViewSet):

    serializer_class = InteractionSerializer
    queryset = Interaction.objects.all()


class TransactionViewSet(CustomViewSet):

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


class ContributionViewSet(CustomViewSet):

    serializer_class = ContributionSerializer
    queryset = ContributionCertificate.objects.all()
