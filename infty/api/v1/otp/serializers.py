from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from captcha.models import CaptchaStore

from infty.api.v1.otp.fields import CaptchaImageField
from infty.api.v1.otp.validators import (
    email_domain_validator,
    one_time_password_limit_validator,
)

from infty.users.models import OneTimePassword


class CaptchaSerializer(serializers.Serializer):
    hashkey = serializers.CharField()
    response = serializers.CharField()

    default_error_messages = {
        'invalid_captcha': _('Invalid CAPTCHA')
    }

    def validate(self, data):
        response = data.get('response')
        hashkey = data.get('hashkey')

        try:
            CaptchaStore.objects.get(
                response__iexact=response,
                hashkey=hashkey
            ).delete()
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['invalid_captcha'])

        return data


class SignupSerializer(serializers.Serializer):

    email = serializers.EmailField(validators=[
        email_domain_validator,
        one_time_password_limit_validator,
    ])
    captcha = CaptchaSerializer()


class OneTimePasswordSerializer(serializers.Serializer):

    one_time_password = serializers.CharField()
    email = serializers.EmailField(validators=[
        email_domain_validator,
        one_time_password_limit_validator,
    ])

    class Meta:
        model = OneTimePassword
        fields = (
            'password',
            'email',
        )


class CaptchaResponseSerializer(serializers.Serializer):
    key = serializers.CharField()
    image_url = CaptchaImageField()
