from django.conf import settings
from django.conf.urls import include, url

from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^v1/', include('infty.api.v1.urls')),
    url(r'^v1/docs/', include_docs_urls(title='WeFindX API')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
