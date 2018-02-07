from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from langsplit import splitter
from rest_framework import fields, serializers


def get_langsplit(lang, value):
    split = splitter.split(value, title=True)
    return split.get(lang) or 'languages: {}'.format(list(split.keys()))


class UserField(serializers.CharField):
    def to_representation(self, value):
        return {"id": value.pk, "username": value.username}


class CategoryNameField(serializers.RelatedField):
    """
    Topic categories string representation field
    Read-Write access
    """
    default_error_messages = {
        'does_not_exist': _('Category with name={name} does not exists.'),
        'invalid': _('Invalid value.'),
    }

    def to_internal_value(self, data):
        """Retrieve category by part of its name (case-insensitive)"""
        try:
            return self.get_queryset().filter(**{'name__icontains': data}).order_by('name').first()
        except ObjectDoesNotExist:
            self.fail('does_not_exist', name=smart_text(data))
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, obj):
        """Returns langsplitted or the whole value"""
        lang = self.context['request'].query_params.get('lang')
        value = obj.name

        if lang and value:
            return get_langsplit(lang, value)

        return value


class LangSplitField(fields.CharField):
    """Langsplit CharField"""

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, value):
        lang = self.context['request'].query_params.get('lang')

        if lang and value:
            return get_langsplit(lang, value)

        return value
