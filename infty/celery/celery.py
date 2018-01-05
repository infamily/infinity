from __future__ import absolute_import
import os
from celery import Celery
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'config.settings.test')  # pragma: no cover

app = Celery(
    'celery',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BROKER_BACKEND,
)
app.autodiscover_tasks()


class CeleryConfig(AppConfig):
    name = 'celery'
    verbose_name = 'Celery Config'

    def ready(self):
        if hasattr(settings, 'RAVEN_CONFIG'):
            # Celery signal registration
            from raven import Client as RavenClient
            from raven.contrib.celery import register_signal as raven_register_signal
            from raven.contrib.celery import register_logger_signal as raven_register_logger_signal

            raven_client = RavenClient(dsn=settings.RAVEN_CONFIG['DSN'])
            raven_register_logger_signal(raven_client)
            raven_register_signal(raven_client)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
