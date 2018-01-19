from django.core.management import BaseCommand

from src.users.models import User, CryptoKeypair


class Command(BaseCommand):
    help = 'update users with CryptoKeypairs, at least one per service'

    def handle(self, *args, **options):

        for user in User.objects.all():
            if CryptoKeypair.objects.filter(user=user).count() > 0:
                continue

            CryptoKeypair.make_one(user=user).save()
            print('- created key for user {}.'.format(user.username))

        print('Done.')
