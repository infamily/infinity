from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from rest_framework import views
from rest_framework.authtoken.models import Token

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from .models import User, OneTimePassword
from .forms import SignupForm, OneTimePasswordLoginForm

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

class OTPRegister(views.APIView):
    authentication_classes = ()
    permission_classes = ()
    def get(self, request):
        new_key = CaptchaStore.pick()
        to_json_response = {
            'key': new_key,
            'image_url': captcha_image_url(new_key),
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')
    def post(self, request):
        json_data = json.loads(request.body.decode('utf-8'))
        form = SignupForm(json_data)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if email:
                email=email.lower()
                user, created = User.objects.get_or_create(email=email, is_active=True)
                OneTimePassword.objects.filter(user=user, is_active=True).update(is_active=False)
                password = OneTimePassword.objects.create(user=user)
                token, created = Token.objects.get_or_create(user=user)
                send_mail(
                    "{} - One-Time Password".format(
                        settings.EMAIL_SUBJECT_PREFIX),
                    password.one_time_password,
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                print("One Time Password", password.one_time_password)
                return HttpResponse(json.dumps({'token': token.key}), content_type='application/json')
        new_key = CaptchaStore.pick()
        to_json_response = {
            'key': new_key,
            'image_url': captcha_image_url(new_key),
        }
        return HttpResponseBadRequest(json.dumps(to_json_response))

class OTPLogin(views.APIView):
    def post(self, request):
        user = request.user
        return HttpResponse()
