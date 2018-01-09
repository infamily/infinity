from rest_framework import serializers

from infty.meta.models import (
    Type,
    Instance,
)


from infty.api.v1.core.fields import LangSplitField


class TypeSerializer(serializers.HyperlinkedModelSerializer):
    name = LangSplitField(required=True)
    definition = LangSplitField(required=True)

    class Meta:
        model = Type
        fields = ('url', 'name', 'definition', 'source', 'languages')


class InstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instance
        fields = ('url', 'role', 'description', 'languages')
