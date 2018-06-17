from django.conf.urls import include, url

from api.views import SchemaView


urlpatterns = [
    url('^api/', SchemaView.as_view()),
    url(r'^', include('api.v1.urls')),
]
