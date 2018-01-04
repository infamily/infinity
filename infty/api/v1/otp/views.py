from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import generics, views, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from captcha.models import CaptchaStore

from infty.api.v1.generic.permissions import IsAuthenticatedAndActive
from infty.api.v1.otp.serializers import (
    CaptchaResponseSerializer, OneTimePasswordSerializer, SignupSerializer,
    UserDetailsSerializer, UserUpdateSerializer)
from infty.mail import send_mail_async
from infty.users.models import OneTimePassword, User


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticatedAndActive, )

    def get_object(self):
        return self.request.user


class UserDetailsView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticatedAndActive, )

    def get_object(self):
        return self.request.user


class OTPCaptchaView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, *args, **kwargs):
        new_key = CaptchaStore.pick()
        captcha_response_serializer = CaptchaResponseSerializer(
            data={
                'key': new_key,
                'image_url': new_key,
            }
        )

        captcha_response_serializer.is_valid(raise_exception=True)

        return Response(captcha_response_serializer.data)


class OTPRegisterView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = SignupSerializer

    def post(self, request):
        serializer_class = self.serializer_class(data=request.data)
        serializer_class.is_valid(raise_exception=True)

        email = serializer_class.data.get("email")

        user, _ = User.objects.get_or_create(email=email, is_active=True)

        OneTimePassword.objects.filter(
            user=user, is_active=True).update(is_active=False)

        password = OneTimePassword.objects.create(user=user)

        Token.objects.get_or_create(user=user)

        subject = '%s - One-Time password' % settings.EMAIL_SUBJECT_PREFIX
        body = password.one_time_password

        send_mail_async(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            [settings.DEFAULT_FROM_EMAIL],
        )

        return Response(serializer_class.data)


class OTPLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = OneTimePasswordSerializer

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
    }

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data.get('email')
        password = serializer.data.get('one_time_password')

        otp_obj = OneTimePassword.objects.filter(
            user__email=email, is_active=True, is_used=False).last()

        if otp_obj:

            if otp_obj.login_attempts > settings.OTP_GENERATION_LIMIT:
                raise exceptions.AuthenticationFailed(
                    self.default_error_messages['password_limit_error'])

            elif otp_obj.one_time_password != password:
                otp_obj.login_attempts += 1
                otp_obj.save(force_update=True)
                raise exceptions.AuthenticationFailed(
                    self.default_error_messages['password_incorrect_error'])

            else:
                otp_obj.is_active = False
                otp_obj.is_used = True
                otp_obj.save(force_update=True)
        else:
            raise exceptions.AuthenticationFailed(
                self.default_error_messages['password_pending_error'])

        return UserDetailsSerializer(otp_obj.user)
