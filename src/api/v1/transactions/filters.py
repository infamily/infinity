from django_filters import rest_framework as filters

from src.transactions.models import Currency


class CurrencyFilter(filters.FilterSet):

    class Meta:
        model = Currency
        fields = ['enabled']

