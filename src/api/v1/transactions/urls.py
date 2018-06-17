from rest_framework import routers
from api.v1.transactions import views


router = routers.DefaultRouter()

router.register(r'currencies', views.CurrencyViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'contributions', views.ContributionViewSet)
router.register(r'topic_snapshots', views.TopicSnapshotViewSet)
router.register(r'comment_snapshots', views.CommentSnapshotViewSet)
router.register(r'hourprice_snapshots', views.HourPriceSnapshotViewSet)
router.register(r'currencyprice_snapshots', views.CurrencyPriceSnapshotViewSet)

urlpatterns = router.urls
