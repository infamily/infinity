from rest_framework import serializers

from src.meta.models import (
    Type,
    Schema,
    Instance,
)


from src.api.v1.core.fields import LangSplitField


class TypeSerializer(serializers.HyperlinkedModelSerializer):
    name = LangSplitField(required=True)
    definition = LangSplitField(required=True)

    class Meta:
        model = Type
        fields = ('url', 'name', 'definition', 'source', 'languages', 'is_category', 'parents')


class SchemaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Schema
        fields = '__all__'


class InstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instance
        fields = '__all__'
