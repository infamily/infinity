from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'src.trade'

    def ready(self):
        import src.trade.signals
