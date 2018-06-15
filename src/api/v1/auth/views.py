from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import viewsets
from rest_framework.authtoken.models import Token

from rest_framework import generics, views, exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from captcha.models import CaptchaStore

from src.api.v1.auth import serializers
from src.users.models import User, OneTimePassword
from src.core.models import Topic

from src.api.v1.auth.serializers import (
    SignatureSerializer, CaptchaResponseSerializer,
    OneTimePasswordSerializer, SignupSerializer,
    UnsubscribedSerializer
)
from src.mail import send_mail_async
from src.api.v1.auth.serializers import UserSerializer

from django.core.signing import Signer
from constance import config


class SignatureView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, *args, **kwargs):
        signature_serializer = SignatureSerializer(
            data={
                'service': 'infinity',
            }
        )

        signature_serializer.is_valid(raise_exception=True)

        return Response(signature_serializer.data)


class ConstanceView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, *args, **kwargs):
        data={
            'terms': config.TERMS_AND_CONDITIONS,
            'show_balance': config.SHOW_BALANCE_WIDGET,
            'page_how': config.PAGE_HOW,
            'page_what': config.PAGE_WHAT,
            'splash_background_urls': config.SPLASH_BACKGROUNDS_URL.split('\r\n'),
        }
        return Response(data)


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

        user_serializer = UserSerializer(otp_obj.user, context={'request': request})
        return Response(user_serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pk=self.request.user.pk)
        return qs


class TokenViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TokenSerializer
    queryset = Token.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class UnsubscribedView(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, *args, **kwargs):

        signer = Signer()

        sign = self.request.GET.get('sign')
        topic = kwargs.get('pk')


        if not topic:
            data = {'status': 'No topic #{} found.'.format(topic)}

        if not sign:
            data = {'status': 'No message sign passed.'}

        if sign and topic:
            try:
                topic = Topic.objects.get(pk=topic)
                user = User.objects.get(email=signer.unsign(sign))

                topic.unsubscribed.add(user)

                data = {'status': 'successfully unsubscribed from topic #{}'.format(topic.pk)}
            except:
                data = {'status': 'wrong signature, cannot unsubscribe'}

        unsubscribed_serializer = UnsubscribedSerializer(
            data=data
        )

        unsubscribed_serializer.is_valid(raise_exception=True)

        return Response(unsubscribed_serializer.data)
