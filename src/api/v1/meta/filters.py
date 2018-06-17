from django_filters import rest_framework as filters

from meta.models import Type


class TypeFilter(filters.FilterSet):
    parents__isnull = filters.BooleanFilter(name='parents', lookup_expr='isnull')

    class Meta:
        model = Type
        fields = ['is_category', 'parents']


