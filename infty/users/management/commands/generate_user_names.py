import hashlib

from django.core.management import BaseCommand

from infty.users.models import User


class Command(BaseCommand):
    help = "update users with User's Name"

    def handle(self, *args, **options):

        for user in User.objects.all():
            user.save()

        print('Done.')
