from captcha.models import CaptchaStore
from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from infty.api.v1.generic.permissions import IsAuthenticatedAndActive
from infty.api.v1.otp.serializers import (
    CaptchaResponseSerializer, OneTimePasswordSerializer, SignupSerializer,
    TokenSerializer, UserDetailsSerializer, UserUpdateSerializer)
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


class OTPRegister(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self):

        new_key = CaptchaStore.pick()

        serializer = CaptchaResponseSerializer(data={
            'key': new_key,
            'image_url': new_key,
            'membership': new_key,
        })

        return Response(serializer.data)

    def post(self, request):
        signup_serializer = SignupSerializer(data=request.data)

        if signup_serializer.is_valid():
            email = signup_serializer.data.get("email")

            if email:
                user, _ = User.objects.get_or_create(
                    email=email, is_active=True)

                OneTimePassword.objects.filter(
                    user=user, is_active=True).update(is_active=False)

                password = OneTimePassword.objects.create(user=user)

                token, _ = Token.objects.get_or_create(user=user)
                token_serializer = TokenSerializer(token)

                subject = '%s - One-Time password' % settings.EMAIL_SUBJECT_PREFIX
                body = password.one_time_password

                send_mail_async(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )

                return Response(token_serializer.data)

        new_key = CaptchaStore.pick()

        captcha_response_serializer = CaptchaResponseSerializer(
            data={
                'key': new_key,
                'image_url': new_key,
                'membership': new_key,
            })

        return Response(
            captcha_response_serializer.data,
            status=status.HTTP_400_BAD_REQUEST)


class OTPLogin(views.APIView):
    def post(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)
