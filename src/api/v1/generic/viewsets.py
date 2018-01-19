from rest_framework import viewsets, mixins


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
