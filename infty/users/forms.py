from django import forms

from django.conf import settings
from django.utils import timezone

from captcha.fields import CaptchaField

from infty.users.models import (
    OneTimePassword,
    MemberOrganization
)


class SignupForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField()

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()

        if cleaned_data.get("email"):

            email = cleaned_data.get("email").lower()
            today = timezone.now().date()

            if not MemberOrganization.objects.filter(domains__contains=[email.split('@')[-1]]).exists():
                raise forms.ValidationError(
                    "Your organization is not a member of this server."
                )

            otp_generation_count = OneTimePassword.objects.filter(
                user__email=email,
                created_date__gte=today
            ).count()

            if otp_generation_count > settings.OTP_GENERATION_LIMIT:
                raise forms.ValidationError(
                    "You have reached a limit for one-time-password generating for today. Try again tomorrow."
                )

        return cleaned_data

class OneTimePasswordLoginForm(forms.Form):

    one_time_password = forms.CharField(required=True)

    def __init__(self, email, *args, **kwargs):
        self.email = email
        super(OneTimePasswordLoginForm, self).__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super(OneTimePasswordLoginForm, self).clean()
        otp = cleaned_data.get("one_time_password")
        email = self.email

        otp_obj = OneTimePassword.objects.filter(
            user__email=email,
            is_active=True,
            is_used=False
        ).last()

        if otp_obj:

            if otp_obj.login_attempts > settings.OTP_GENERATION_LIMIT:
                raise forms.ValidationError(
                    "You have reached a limit for one-time-password login attempts!"
                )

            elif otp_obj.one_time_password != otp:
                otp_obj.login_attempts += 1
                otp_obj.save(force_update=True)
                raise forms.ValidationError(
                    "One-time-password is incorrect!"
                )

            else:
                otp_obj.is_active = False
                otp_obj.is_used = True
                otp_obj.save(force_update=True)
        else:
            raise forms.ValidationError(
                "You have no currently pending one-time-password!"
            )
        return cleaned_data
