"""
Local settings

- Run in Debug mode

- Use mailhog for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

import os
import socket

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default=';2sEAsau;l^I9*[1AY72:G4XeIpjjM;kV5uJ(BT}(5U-95}IRk')

# Mail settings
# ------------------------------------------------------------------------------

# EMAIL_PORT = 1025
#
# EMAIL_HOST = env('EMAIL_HOST', default='mailhog')
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='INFINITY <noreply@inf.li>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[WFX]')
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]


# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1']

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    'django_extensions'
]

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# CELERY
# In development, all tasks will be executed locally by blocking until the task returns
CELERY_ALWAYS_EAGER = True
# END CELERY

# Your local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
