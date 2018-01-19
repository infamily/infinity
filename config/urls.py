from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import IsAuthenticatedOrReadOnly


urlpatterns = [
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^accounts/', include('allauth.urls')),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    url(r'', include('src.api.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^docs/',
        include_docs_urls(
            title='Infinity API',
            permission_classes=(IsAuthenticatedOrReadOnly, ))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
