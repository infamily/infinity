from django.conf.urls import url, include
from infty.api.v1 import views

urlpatterns = [
    url('^$', views.schema_view),
    url(r'^core/', include('infty.api.v1.core.urls', namespace='core')),
    url(r'^transactions/', include('infty.api.v1.transactions.urls', namespace='transactions')),
    url(r'^otp/', include('infty.api.v1.otp.urls', namespace='otp')),
]
