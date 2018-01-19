from django.conf.urls import url

from rest_framework import routers
from src.api.v1.auth import views


router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'tokens', views.TokenViewSet)

urlpatterns = [
    url(r'^signup/$', views.OTPRegisterView.as_view(), name="signup"),
    url(r'^signin/$', views.OTPLoginView.as_view(), name="signin"),
    url(r'^captcha/$', views.OTPCaptchaView.as_view(), name="captcha"),
] + router.urls
