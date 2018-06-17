from decimal import Decimal
from trade.models import Reserve
from django.db.models import Sum

class TopicTradeMixin():

    def funds(self):
        return Decimal(
            Reserve.objects.filter(topic=self).aggregate(total=Sum('hours')).get('total')
            or 0)

