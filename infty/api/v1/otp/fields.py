from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import serializers
from rest_framework import fields

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from infty.users.utils import organizations_domains_hashes


class CaptchaImageField(fields.CharField):
    def to_representation(self, value):
        result = super().to_representation(value)
        return captcha_image_url(result)


class OrganizationsDomainsHashesField(fields.ListField):
    def to_representation(self, value):
        return organizations_domains_hashes(value)


class CaptchaField(serializers.Serializer):
    hashkey = serializers.CharField()
    response = serializers.CharField()

    default_error_messages = {
        'invalid_captcha': _('Invalid CAPTCHA')
    }

    def validate(self, data):
        response = data.get('response')
        hashkey = data.get('hashkey')

        if not settings.CAPTCHA_GET_FROM_POOL:
            CaptchaStore.remove_expired()

        try:
            CaptchaStore.objects.get(
                response=response,
                hashkey=hashkey
            ).delete()
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['invalid_captcha'])

        return data
