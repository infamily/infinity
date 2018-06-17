from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from api.v1.generic.viewsets import CustomViewSet

from transactions.models import (
    Currency,
    Interaction,
    Transaction,
    ContributionCertificate,
    TopicSnapshot,
    CommentSnapshot,
    HourPriceSnapshot,
    CurrencyPriceSnapshot,
)

from api.v1.transactions.serializers import (
    CurrencyListSerializer,
    InteractionSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    ContributionSerializer,
    TopicSnapshotSerializer,
    CommentSnapshotSerializer,
    HourPriceSnapshotSerializer,
    CurrencyPriceSnapshotSerializer,
)

from api.v1.transactions.filters import CurrencyFilter


class CurrencyViewSet(CustomViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CurrencyListSerializer
    queryset = Currency.objects.all()
    filter_class = CurrencyFilter


class TransactionViewSet(CustomViewSet):

    queryset = Transaction.objects.all()
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('comment',)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer

        return TransactionListSerializer


class InteractionViewSet(CustomViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = InteractionSerializer
    queryset = Interaction.objects.all()


class ContributionViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('transaction', 'received_by')

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ContributionSerializer
    queryset = ContributionCertificate.objects.all()


class TopicSnapshotViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('topic',)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    serializer_class = TopicSnapshotSerializer
    queryset = TopicSnapshot.objects.all()


class CommentSnapshotViewSet(CustomViewSet):
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('comment',)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    serializer_class = CommentSnapshotSerializer
    queryset = CommentSnapshot.objects.all()


class HourPriceSnapshotViewSet(CustomViewSet):

    serializer_class = HourPriceSnapshotSerializer
    queryset = HourPriceSnapshot.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class CurrencyPriceSnapshotViewSet(CustomViewSet):

    serializer_class = CurrencyPriceSnapshotSerializer
    queryset = CurrencyPriceSnapshot.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
