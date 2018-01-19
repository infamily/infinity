from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'src.core'

    def ready(self):
        import src.core.signals
