from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.SimpleRouter()

router.register(r'topic', views.TopicViewSet, base_name='topics')



urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'topic/$', views.TopicListView.as_view(), name='topic'),
    url(r'topics/$', views.TopicViewSet.as_view({'get': 'list'}))
]
