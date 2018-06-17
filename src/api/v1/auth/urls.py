from django.conf.urls import url

from rest_framework import routers
from api.v1.auth import views


router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'tokens', views.TokenViewSet)

urlpatterns = [
    url(r'^signup/$', views.OTPRegisterView.as_view(), name="signup"),
    url(r'^signin/$', views.OTPLoginView.as_view(), name="signin"),
    url(r'^captcha/$', views.OTPCaptchaView.as_view(), name="captcha"),
    url(r'^signature/$', views.SignatureView.as_view(), name="signature"),
    url(r'^unsubscribe/(?P<pk>[^/.]+)/$', views.UnsubscribedView.as_view(), name="unsubscribed"),
    url(r'^constance/$', views.ConstanceView.as_view(), name="constance"),
] + router.urls
