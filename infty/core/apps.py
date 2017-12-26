from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'infty.core'

    def ready(self):
        import infty.core.signals
