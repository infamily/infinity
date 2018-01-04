from django.conf.urls import include, url

from api.views import SchemaView


urlpatterns = [
    url('^$', SchemaView.as_view()),
    url(r'^v1/', include('infty.api.v1.urls', namespace='v1')),
]
