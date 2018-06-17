from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        import trade.signals
