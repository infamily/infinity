from django_filters import rest_framework as filters

from src.meta.models import Type


class TypeFilter(filters.FilterSet):

    class Meta:
        model = Type
        fields = ['is_category']


