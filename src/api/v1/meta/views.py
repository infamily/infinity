from rest_framework.permissions import IsAuthenticatedOrReadOnly

from src.meta.models import Type, Schema, Instance

from src.api.v1.generic.viewsets import CustomViewSet

from src.api.v1.meta.serializers import (
    TypeSerializer,
    SchemaSerializer,
    InstanceSerializer,
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

    serializer_class = SchemaSerializer
    queryset = Schema.objects.all()


class InstanceViewSet(CustomViewSet):

    serializer_class = InstanceSerializer
    queryset = Instance.objects.all()
