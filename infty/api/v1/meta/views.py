from rest_framework.permissions import IsAuthenticatedOrReadOnly

from infty.meta.models import Type, Instance

from infty.api.v1.generic.viewsets import CustomViewSet

from infty.api.v1.meta.serializers import (
    TypeSerializer,
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


class InstanceViewSet(CustomViewSet):

    serializer_class = InstanceSerializer
    queryset = Instance.objects.all()
