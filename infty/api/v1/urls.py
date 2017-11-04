from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from infty.api.v1 import views
from infty.users.views import OTPRegister, OTPLogin

router = routers.DefaultRouter()

router.register(r'types', views.TypeViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'contributions', views.ContributionViewSet)


urlpatterns = [
    url('^$', views.schema_view),
    url(r'^', include(router.urls)),
    url(r'^otp/signup/', OTPRegister.as_view()),
    url(r'^otp/login/', OTPLogin.as_view())
]
