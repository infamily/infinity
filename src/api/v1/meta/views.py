from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from src.api.v1.generic.permissions import (
    IsOwner
)

from src.meta.models import Type, Schema, Instance

from src.api.v1.generic.viewsets import CustomViewSet

from src.api.v1.meta.serializers import (
    TypeSerializer,
    SchemaSerializer,
    InstanceSerializer,
)

from src.api.v1.generic.pagination_classes import (
    StandardResultsSetPagination,
    LargeResultsSetPagination
)


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


class SchemaViewSet(CustomViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ('name', 'version')
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwner()]

        return [permission() for permission in self.permission_classes]

    serializer_class = SchemaSerializer
    queryset = Schema.objects.all()


class InstanceViewSet(CustomViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LargeResultsSetPagination
    filter_fields = ('schema',)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwner()]

        return [permission() for permission in self.permission_classes]

    serializer_class = InstanceSerializer
    queryset = Instance.objects.all()
