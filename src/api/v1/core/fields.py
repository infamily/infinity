from rest_framework import fields, serializers
from langsplit import splitter


class UserField(serializers.CharField):
    def to_representation(self, value):
        return {"id": value.pk, "username": value.username}


class CategoriesField(serializers.RelatedField):
    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        item = {"id": value.pk, "name": value.name}

        if lang:

            split = splitter.split(value.name, title=True)
            item["name"] = split.get(lang) or \
                'languages: {}'.format(list(split.keys()))

        return item


class LangSplitField(fields.CharField):
    """Langsplit CharField"""

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        if lang and value:
            split = splitter.split(value, title=True)
            return split.get(lang) or 'languages: {}'.format(
                list(split.keys()))

        return value
