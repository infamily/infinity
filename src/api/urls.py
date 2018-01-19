from django.conf.urls import include, url

from src.api.views import SchemaView


urlpatterns = [
    url('^api/', SchemaView.as_view()),
    url(r'^', include('src.api.v1.urls')),
]
