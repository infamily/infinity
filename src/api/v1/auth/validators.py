from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from users.models import (
    MemberOrganization,
    OneTimePassword,
)


class EmailDomainValidator:
    message = _('Your organization is not a member of this server.')
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if not MemberOrganization.objects.filter(
                domains__contains=[value.split('@')[-1]]).exists():
            raise ValidationError(self.message)


class OneTimePasswordLimitValidator:
    message = _('You have reached a limit \
    \         for one-time-password generating\
    \         for today. Try again tomorrow.')
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        today = timezone.now().date()

        otp_generation_count = OneTimePassword.objects.filter(
            user__email=value, created_date__gte=today).count()

        if otp_generation_count > settings.OTP_GENERATION_LIMIT:
            raise ValidationError(self.message)


email_domain_validator = EmailDomainValidator()
one_time_password_limit_validator = OneTimePasswordLimitValidator()
