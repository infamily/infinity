from django_filters import rest_framework as filters

from transactions.models import Currency


class CurrencyFilter(filters.FilterSet):

    class Meta:
        model = Currency
        fields = ['enabled']

