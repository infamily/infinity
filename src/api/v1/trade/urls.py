from rest_framework import routers
from api.v1.trade import views


router = routers.DefaultRouter()

router.register(r'payments', views.PaymentViewSet)
router.register(r'reserves', views.ReserveListViewSet)

urlpatterns = router.urls
