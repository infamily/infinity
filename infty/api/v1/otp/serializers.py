from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from captcha.models import CaptchaStore

from infty.api.v1.otp.fields import CaptchaImageField
from infty.api.v1.otp.validators import email_domain_validator, one_time_password_limit_validator
from infty.users.models import User


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
    email = serializers.EmailField(validators=[email_domain_validator, ])

    # default_error_messages = {
    #     'password_incorrect_error':
    #     _('One-time-password is incorrect!'),
    #     'password_limit_error':
    #     _('You have reached a limit \
    #         for one-time-password generating \
    #         for today. Try again tomorrow.'),
    #     'password_pending_error':
    #     _('You have no \
    #         currently pending one-time-password!'),
    # }.update(serializers.Serializer.default_error_messages)

    # def validate(self, data):
    #     otp = data.get('one_time_password')
    #     email = data.get('email')

    #     otp_obj = OneTimePassword.objects.filter(
    #         user__email=email, is_active=True, is_used=False).last()

    #     if otp_obj:

    #         if otp_obj.login_attempts > settings.OTP_GENERATION_LIMIT:
    #             raise serializers.ValidationError(
    #                 self.default_error_messages.get('password_limit_error'))

    #         elif otp_obj.one_time_password != otp:
    #             otp_obj.login_attempts += 1
    #             otp_obj.save(force_update=True)
    #             raise serializers.ValidationError(
    #                 self.default_error_messages.get(
    #                     'password_incorrect_error'))

    #         else:
    #             otp_obj.is_active = False
    #             otp_obj.is_used = True
    #             otp_obj.save(force_update=True)
    #     else:
    #         raise serializers.ValidationError(
    #             self.default_error_messages.get('password_pending_error'))

    #     return data


class CaptchaResponseSerializer(serializers.Serializer):
    key = serializers.CharField()
    image_url = CaptchaImageField()


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = (
            'key',
            'user',
            'created',
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'about',
            'first_name',
            'last_name',
            'email',
        )


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'about',
            'first_name',
            'last_name',
            'email',
        )
