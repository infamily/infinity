from django.conf.urls import include, url

from infty.api.views import SchemaView


urlpatterns = [
    url('^api/', SchemaView.as_view()),
    url(r'^', include('infty.api.v1.urls')),
]
