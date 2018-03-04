from rest_framework import routers
from src.api.v1.trade import views


router = routers.DefaultRouter()

router.register(r'payments', views.PaymentViewSet)

urlpatterns = router.urls
