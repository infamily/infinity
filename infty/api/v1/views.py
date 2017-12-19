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

from infty.users.models import User, LanguageName

from infty.core.models import (
    Type,
    Instance,
    Topic,
    Comment,
)
from infty.transactions.models import (
    Currency,
    Interaction,
    Transaction,
    ContributionCertificate,
    TopicSnapshot,
    CommentSnapshot,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
)
from infty.api.v1.serializers import (
    TypeSerializer,
    InstanceSerializer,
    TopicSerializer,
    CommentSerializer,

    CurrencyListSerializer,
    InteractionSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    ContributionSerializer,
    TopicSnapshotSerializer,
    CommentSnapshotSerializer,
    HourPriceSnapshotSerializer,
    CurrencyPriceSnapshotSerializer,

    UserBalanceSerializer,
    LanguageNameSerializer,
)
from infty.api.v1.pagination_classes import (
    StandardResultsSetPagination,
    LargeResultsSetPagination
)

from infty.api.v1.filters import TopicFilter


schema_generator = schemas.SchemaGenerator(title='Infinity API')


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


class CurrencyViewSet(CustomViewSet):
    serializer_class = CurrencyListSerializer
    queryset = Currency.objects.all()


class InteractionViewSet(CustomViewSet):

    serializer_class = InteractionSerializer
    queryset = Interaction.objects.all()


class TransactionViewSet(CustomViewSet):

    queryset = Transaction.objects.all()
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('comment',)

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer

        return TransactionListSerializer


class ContributionViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('transaction', 'received_by')

    serializer_class = ContributionSerializer
    queryset = ContributionCertificate.objects.all()


class TopicSnapshotViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('topic',)

    serializer_class = TopicSnapshotSerializer
    queryset = TopicSnapshot.objects.all()


class CommentSnapshotViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('comment',)

    serializer_class = CommentSnapshotSerializer
    queryset = CommentSnapshot.objects.all()


class HourPriceSnapshotViewSet(CustomViewSet):

    serializer_class = HourPriceSnapshotSerializer
    queryset = HourPriceSnapshot.objects.all()


class CurrencyPriceSnapshotViewSet(CustomViewSet):

    serializer_class = CurrencyPriceSnapshotSerializer
    queryset = CurrencyPriceSnapshot.objects.all()


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
