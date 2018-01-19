from rest_framework.test import APITestCase
from rest_framework import status

from captcha.conf import settings
from captcha.models import CaptchaStore

from django.test import override_settings
from django.core.urlresolvers import reverse

from src.users.models import (
    User,
    OneTimePassword,
    MemberOrganization
)

settings.CAPTCHA_TEST_MODE = True


@override_settings(OTP_GENERATION_LIMIT=3)
class APITestCaseCustom(APITestCase):

    def setUp(self):

        self.organization = MemberOrganization.objects.create(
            identifiers="Test Organization",
            domains=['test.com'],
        )
        self.email = "test@test.com"
        self.password = "password_for_test"
        self.testuser = User.objects.create_user(username=self.email, email=self.email)
        self.testuser.set_password(self.password)
        self.testuser.save()

        self.signup_data = {"email": self.email}

        self.otp = OneTimePassword.objects.create(
            user=self.testuser,
        )
        self.otp_id = self.otp.id
        self.otp_signup_url = reverse('signup')
        self.otp_login_url = reverse('signin')


class OTPSignupTestCase(APITestCaseCustom):

    def test_can_create_otp(self):
        response = self.client.get(reverse('captcha'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        captcha = CaptchaStore.objects.first()
        captcha_response = captcha.response
        captcha_hashkey = captcha.hashkey

        data = {"email": self.email, "captcha": {
            "hashkey": captcha_hashkey,
            "response": captcha_response,
        }}

        response = self.client.post(self.otp_signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_create_otp_wo_membership(self):
        data = {"email": 'test@other.com', "captcha_0": "abc", "captcha_1": "passed"}
        response = self.client.post(self.otp_signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_otp_wo_email(self):
        data = {"email": "", "captcha_0": "abc", "captcha_1": "abc"}
        response = self.client.post(self.otp_signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_otp_over_the_limit(self):
        for _ in range(3):
            OneTimePassword.objects.create(user=self.testuser, is_active=False)

        response = self.client.post(self.otp_signup_url, self.signup_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_new_otp_disables_previous(self):
        self.test_can_create_otp()
        self.client.post(self.otp_signup_url, self.signup_data, format="json")
        initial_otp = OneTimePassword.objects.get(id=self.otp_id)
        self.assertEqual(initial_otp.is_active, False)


class OTPLoginTestCase(APITestCaseCustom):

    def test_can_login_with_wrong_otp(self):
        login_data = {"email": self.email, "one_time_password": "some_wrong_otp"}
        response = self.client.post(self.otp_login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_login_without_otp(self):
        login_data = {"email": self.email, "one_time_password": ""}
        response = self.client.post(self.otp_login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_login_without_email(self):
        login_data = {"email": "", "one_time_password": self.otp.one_time_password}
        response = self.client.post(self.otp_login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_login_over_attempts_limit(self):
        login_data = {"email": self.email, "one_time_password": "some_wrong_otp"}

        # add 3 more login attempts for today (default limit is 3)
        for _ in range(3):
            response = self.client.post(self.otp_login_url, login_data, format="json")

        response = self.client.post(self.otp_login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
