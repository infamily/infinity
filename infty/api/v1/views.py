from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import (
    viewsets,
    schemas,
    response,
    renderers,
    mixins,
    filters
)

from django_filters.rest_framework import DjangoFilterBackend

from infty.core.models import (
    Type,
    Instance,
    Topic,
    Comment,
)
from infty.transactions.models import (
    Interaction,
    Transaction,
    ContributionCertificate
)
from infty.api.v1.serializers import (
    TypeSerializer,
    InstanceSerializer,
    TopicSerializer,
    CommentSerializer,

    InteractionSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    ContributionSerializer,
)
from infty.api.v1.pagination_classes import (
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


class InteractionViewSet(CustomViewSet):

    serializer_class = InteractionSerializer
    queryset = Interaction.objects.all()


class TransactionViewSet(CustomViewSet):

    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer

        return TransactionListSerializer


class ContributionViewSet(CustomViewSet):

    serializer_class = ContributionSerializer
    queryset = ContributionCertificate.objects.all()
