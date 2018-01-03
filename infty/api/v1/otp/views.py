from captcha.models import CaptchaStore
from django.conf import settings
from rest_framework import generics, views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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
            })

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

        token, _ = Token.objects.get_or_create(user=user)

        subject = '%s - One-Time password' % settings.EMAIL_SUBJECT_PREFIX
        body = password.one_time_password

        send_mail_async(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        return Response(serializer_class.data)


class OTPLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = OneTimePasswordSerializer

    def post(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)
