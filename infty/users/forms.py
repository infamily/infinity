from django import forms

from .models import OneTimePassword

from captcha.fields import CaptchaField

from django.utils import timezone

class SignupForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField()
    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        if cleaned_data.get("email"):
            #django-allauth lowers emails
            email = cleaned_data.get("email").lower()
            today = timezone.now().date()
            otp_generation_nmb = OneTimePassword.objects.filter(user__email=email, created__gte=today).count()
            if otp_generation_nmb > 3:
                raise forms.ValidationError("You have reached a limit for one-time-password generating for today! Try again tomorrow!")
        return cleaned_data

class OneTimePasswordLoginForm(forms.Form):
    one_time_password = forms.CharField(required=True)
    def __init__(self, email, *args, **kwargs):
        self.email = email
        super(OneTimePasswordLoginForm, self).__init__(*args, **kwargs)
    def clean(self):
        cleaned_data = cleaned_data = super(OneTimePasswordLoginForm, self).clean()
        otp = cleaned_data.get("one_time_password")
        email = self.email
        otp_obj = OneTimePassword.objects.filter(user__email=email, is_active=True, is_used=False).last()
        if otp_obj:
            print("cleaned data")
            if otp_obj.login_attempts > 3:
                print(1)
                raise forms.ValidationError("You have reached a limit for one-time-password login attempts!")
            elif otp_obj.one_time_password != otp:
                otp_obj.login_attempts+=1
                otp_obj.save(force_update=True)
                raise forms.ValidationError("One-time-password is incorrect!")
            else:
                otp_obj.is_active=False
                otp_obj.is_used=True
                otp_obj.save(force_update=True)
        else:
            raise forms.ValidationError("You have no currently pending one-time-password!")
        return cleaned_data