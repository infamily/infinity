from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from infty.users.models import MemberOrganization


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


email_domain_validator = EmailDomainValidator()
