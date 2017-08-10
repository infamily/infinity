from django.conf import settings
from django.conf.urls import include, url

# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_swagger_view(title='Infinity API documentation', url=settings.SWAGGER_BASE_URL)

urlpatterns = [
    # url(r'^$', schema_view, name='documentation'),
    url(r'^', include('infty.api.v1.urls')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
