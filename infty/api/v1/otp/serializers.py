from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from infty.api.v1.otp.fields import CaptchaField, CaptchaImageField, OrganizationsDomainsHashesField
from infty.users.models import MemberOrganization, OneTimePassword, User


class SignupSerializer(serializers.Serializer):

    email = serializers.EmailField()
    captcha = CaptchaField()

    default_error_messages = {
        'organization_error':
        _('Your organization is not a \
            member of this server.'),
        'password_limit_error':
        _('You have reached a limit \
            for one-time-password generating \
            for today. Try again tomorrow.')
    }.update(serializers.Serializer.default_error_messages)

    def validate(self, data):
        email = data.get('email')
        today = timezone.now().date()

        if not MemberOrganization.objects.filter(
                domains__contains=[email.split('@')[-1]]).exists():
            raise serializers.ValidationError(
                self.default_error_messages.get('organization_error'))

        otp_generation_count = OneTimePassword.objects.filter(
            user__email=email, created_date__gte=today).count()

        if otp_generation_count > settings.OTP_GENERATION_LIMIT:
            raise forms.ValidationError(
                self.default_error_messages.get('password_limit_error'))

        return data


class OneTimePasswordSerializer(serializers.Serializer):

    one_time_password = serializers.CharField()
    email = serializers.EmailField()

    default_error_messages = {
        'password_incorrect_error':
        _('One-time-password is incorrect!'),
        'password_limit_error':
        _('You have reached a limit \
            for one-time-password generating \
            for today. Try again tomorrow.'),
        'password_pending_error':
        _('You have no \
            currently pending one-time-password!'),
    }.update(serializers.Serializer.default_error_messages)

    def validate(self, data):
        otp = data.get('one_time_password')
        email = data.get('email')

        otp_obj = OneTimePassword.objects.filter(
            user__email=email, is_active=True, is_used=False).last()

        if otp_obj:

            if otp_obj.login_attempts > settings.OTP_GENERATION_LIMIT:
                raise serializers.ValidationError(
                    self.default_error_messages.get('password_limit_error'))

            elif otp_obj.one_time_password != otp:
                otp_obj.login_attempts += 1
                otp_obj.save(force_update=True)
                raise serializers.ValidationError(
                    self.default_error_messages.get(
                        'password_incorrect_error'))

            else:
                otp_obj.is_active = False
                otp_obj.is_used = True
                otp_obj.save(force_update=True)
        else:
            raise serializers.ValidationError(
                self.default_error_messages.get('password_pending_error'))

        return data


class CaptchaResponseSerializer(serializers.Serializer):
    key = serializers.CharField()
    image_url = CaptchaImageField()
    membership = OrganizationsDomainsHashesField()


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


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'about',
            'first_name',
            'last_name',
            'email',
        )
