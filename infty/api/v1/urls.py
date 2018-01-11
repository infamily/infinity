from django.conf.urls import url, include
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/docs/')),
    url(r'^', include('infty.api.v1.core.urls')),
    url(r'^', include('infty.api.v1.meta.urls')),
    url(r'^', include('infty.api.v1.auth.urls')),
    url(r'^', include('infty.api.v1.transactions.urls')),
]
