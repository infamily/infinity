from django.conf.urls import url
from infty.api.v1.otp import views

urlpatterns = [
    url(r'^signup/$', views.OTPRegisterView.as_view(), name="signup"),
    url(r'^signin/$', views.OTPLoginView.as_view(), name="signin"),
    url(r'^captcha/$', views.OTPCaptchaView.as_view(), name="captcha"),
]
