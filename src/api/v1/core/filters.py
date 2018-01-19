from django_filters import rest_framework as filters

from src.core.models import Topic


class OwnerFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value == 'me':
            value = self.parent.request.user.pk

        return super().filter(qs, value)


class TopicFilter(filters.FilterSet):
    owner = OwnerFilter()

    class Meta:
        model = Topic
        fields = ['owner', 'parents']
