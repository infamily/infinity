# from rest_framework.test import APITestCase
# from rest_framework import status

# from infty.users.models import User, OneTimePassword


# class APITestCaseCustom(APITestCase):

#     def setUp(self):

#         self.email = "test@test.com"
#         self.password = "password_for_test"
#         self.testuser = User.objects.create_user(username=self.email, email=self.email)
#         self.testuser.set_password(self.password)
#         self.testuser.save()

#         self.signup_data = {"email": self.email}

#         self.otp = OneTimePassword.objects.create(
#             user=self.testuser,
#         )
#         self.otp_id = self.otp.id


# class OTPSignupTestCase(APITestCaseCustom):

#     def test_can_create_otp(self):
#         data = {"email": self.email}
#         response = self.client.post("/api/v1/otp/signup", data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_cannnot_create_otp_wo_email(self):
#         data = {"emainl": ""}
#         response = self.client.post("/api/v1/otp/signup", data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_cannot_create_otp_over_the_limit(self):
#         #add 3 more otp creation for today (default limit is 3)
#         for _ in range(3):
#             OneTimePassword.objects.create(user=self.testuser, is_active=False)

#         response = self.client.post("/api/v1/otp/signup", self.signup_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_if_new_otp_disables_previous(self):
#         self.client.post("/api/v1/otp/signup", self.signup_data, format="json")
#         initial_otp = OneTimePassword.objects.get(id=self.otp_id)
#         self.assertEqual(initial_otp.is_active, False)


# class OTPLoginTestCase(APITestCaseCustom):

#     def test_can_login_with_otp(self):
#         login_data = {"email": self.email, "one_time_password": self.otp.one_time_password}
#         response = self.client.post("/api/v1/otp/login", login_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_can_login_with_wrong_otp(self):
#         login_data = {"email": self.email, "one_time_password": "some_wrong_otp"}
#         response = self.client.post("/api/v1/otp/login", login_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_cannot_login_without_otp(self):
#         login_data = {"email": self.email, "one_time_password": ""}
#         response = self.client.post("/api/v1/otp/login", login_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_cannot_login_without_email(self):
#         login_data = {"email": "", "one_time_password": self.otp.one_time_password}
#         response = self.client.post("/api/v1/otp/login", login_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_can_login_over_attempts_limit(self):
#         login_data = {"email": self.email, "one_time_password": "some_wrong_otp"}

#         #add 3 more login attempts for today (default limit is 3)
#         for _ in range(3):
#             response = self.client.post("/api/v1/otp/login", login_data, format="json")

#         response = self.client.post("/api/v1/otp/login", login_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
