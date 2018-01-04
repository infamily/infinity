from django.conf.urls import url, include


urlpatterns = [
    url(r'^core/', include('infty.api.v1.core.urls', namespace='core')),
    url(r'^meta/', include('infty.api.v1.meta.urls', namespace='meta')),
    url(r'^auth/', include('infty.api.v1.auth.urls', namespace='auth')),
    url(r'^transactions/', include('infty.api.v1.transactions.urls', namespace='transactions')),
    url(r'^otp/', include('infty.api.v1.otp.urls', namespace='otp')),
]
