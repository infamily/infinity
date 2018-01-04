from rest_framework import serializers
from rest_framework.authtoken.models import Token

from infty.users.models import User


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        extra_kwargs = {'url': {'view_name': 'api:v1:auth:token-detail'}}
        fields = (
            'key',
            'created',
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    auth_token = serializers.HyperlinkedRelatedField(
        view_name='api:v1:auth:token-detail',
        queryset=Token.objects.all())

    class Meta:
        model = User
        extra_kwargs = {'url': {'view_name': 'api:v1:auth:user-detail'}}
        fields = (
            'about',
            'url',
            'first_name',
            'last_name',
            'email',
            'username',
            'auth_token',
        )
