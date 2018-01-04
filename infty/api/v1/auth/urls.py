from rest_framework import routers
from infty.api.v1.auth import views


router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'tokens', views.TokenViewSet)

urlpatterns = router.urls
