from rest_framework import routers
from src.api.v1.meta import views

router = routers.DefaultRouter()

router.register(r'types', views.TypeViewSet)
router.register(r'instances', views.InstanceViewSet)

urlpatterns = router.urls
