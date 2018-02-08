import json_lines
import gzip
from rest_framework import status, mixins, viewsets
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

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
    permission_classes = (IsAuthenticated,)
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
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
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


class InstanceBulkViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    filter_fields = ('schema',)
    queryset = Instance.objects.all()
    parser_classes = (FileUploadParser, )
    serializer_class = InstanceSerializer

    def create(self, request, *args, **kwargs):
        fp = request._request.FILES.get('file.jl.gz')
        data = [line for line in json_lines.reader(gzip.GzipFile(fileobj=fp))]

        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)

