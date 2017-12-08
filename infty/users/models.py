import hashlib

from bigchaindb_driver.crypto import generate_keypair

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.contrib.postgres.fields import ArrayField

from infty.generic.models import GenericModel, GenericManager


class User(AbstractUser, GenericModel):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    about = models.TextField(blank=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def save(self, *args, **kwargs):
        """
        Also do some things during the creation of user.
        # TODO move it to signals
        """

        if self.email:
            name, domain = self.email.lower().split('@')

            user_hash = hashlib.sha1(
                self.email.encode('utf-8')).hexdigest()[:8]

            self.username = "{}@{}".format(name.title(), user_hash.upper())

        super(User, self).save(*args, **kwargs)

        CryptoKeypair.objects.make_one(user=self)


class CryptoKeypairManager(GenericManager):

    def make_one(self, user, key_type=0, save_private=True):
        pair = generate_keypair()

        keypair = self.create(
            user=user,
            type=key_type,
            private_key=pair.private_key if save_private else None,
            public_key=pair.public_key
        )

        setattr(
            keypair,
            '_tmp_private_key', pair.private_key if not save_private else None
        )
        return keypair


class CryptoKeypair(GenericModel):
    NONE = 0
    IPDB = 1

    KEY_TYPES = [
        (NONE, 'None'),
        (IPDB, 'IPDB'),
    ]

    user = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(KEY_TYPES, default=IPDB)
    private_key = models.TextField(null=True, blank=True)
    public_key = models.TextField(null=False, blank=False)

    objects = CryptoKeypairManager()

    def __str__(self):
        return "{} - {}".format(self.user, self.type)


class OneTimePassword(GenericModel):
    user = models.ForeignKey(User)
    one_time_password = models.CharField(max_length=64, default=get_random_string)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) #put inactive if maximum nmb of attempts was reached or when is_used=True
    login_attempts = models.IntegerField(default=0) #we can limit it in form validation

    def __str__(self):
        return self.user.username


class MemberOrganization(GenericModel):
    identifiers = models.TextField()
    domains = ArrayField(models.CharField(max_length=80), blank=True)

    def __str__(self):
        return "{}: {}".format(
            self.identifiers,
            ', '.join(self.domains)
        )

    class Meta:
        verbose_name = _("Member organization")
        verbose_name_plural = _("Member organizations")
