from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('infty.api.v1.core.urls')),
    url(r'^', include('infty.api.v1.meta.urls')),
    url(r'^', include('infty.api.v1.auth.urls')),
    url(r'^', include('infty.api.v1.transactions.urls')),
]
