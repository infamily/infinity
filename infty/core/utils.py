import json

from django.core import serializers


def instance_to_save_dict(instance):
    return json.loads(
        serializers.serialize(
            'json', [instance], ensure_ascii=False)[1:-1]
    )
