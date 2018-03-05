from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from src.api.v1.generic.viewsets import CustomViewSet
from src.trade.models import Payment, Reserve
from src.api.v1.trade.serializers import (
    PaymentSerializer,
    ReserveListSerializer
)

from src.api.v1.generic.permissions import (
    IsOwner
)


class PaymentViewSet(CustomViewSet):
    serializer_class = PaymentSerializer

    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('owner',)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(owner=self.request.user)
        return qs


class ReserveListViewSet(CustomViewSet):
    serializer_class = ReserveListSerializer

    queryset = Reserve.objects.all()
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,)
    filter_fields = ('user', 'payment', 'transaction')
    http_method_names = ['get']
