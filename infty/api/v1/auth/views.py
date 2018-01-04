from rest_framework import viewsets
from rest_framework.authtoken.models import Token

from infty.api.v1.auth import serializers
from infty.users.models import User


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pk=self.request.user.pk)
        return qs


class TokenViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TokenSerializer
    queryset = Token.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs
