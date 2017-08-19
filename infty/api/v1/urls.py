from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from infty.api.v1 import views

router = routers.DefaultRouter()

router.register(r'topics', views.TopicViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'transactions', views.TransactionViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]

