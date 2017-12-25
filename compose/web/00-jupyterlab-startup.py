import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
sys.path.append("/app/")
import django
django.setup()
