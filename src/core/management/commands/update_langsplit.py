from django.core.management import BaseCommand

from src.core.models import Topic, Comment

from collections import OrderedDict
from langsplit import splitter

class Command(BaseCommand):
    help = 'update topics and comments with language'

    def handle(self, *args, **options):

        for topic in Topic.objects.all().order_by('-pk'):
            topic.save(update_fields=['title', 'body', 'languages'])

        for comment in Comment.objects.all().order_by('-pk'):
            comment.save(update_fields=['text', 'languages'])

        print('Done.')

