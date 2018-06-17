from rest_framework import routers
from api.v1.meta import views

router = routers.DefaultRouter()

router.register(r'types', views.TypeViewSet)
router.register(r'schemas', views.SchemaViewSet)
router.register(r'instances', views.InstanceViewSet)
router.register(r'instances_bulk', views.InstanceBulkViewSet)

urlpatterns = router.urls
