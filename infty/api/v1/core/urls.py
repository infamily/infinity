from rest_framework import routers
from infty.api.v1.core import views


router = routers.DefaultRouter()

router.register(r'types', views.TypeViewSet)
router.register(r'instances', views.InstanceViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'currencies', views.CurrencyViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'contributions', views.ContributionViewSet)

router.register(r'topic_snapshots', views.TopicSnapshotViewSet)
router.register(r'comment_snapshots', views.CommentSnapshotViewSet)
router.register(r'hourprice_snapshots', views.HourPriceSnapshotViewSet)
router.register(r'currencyprice_snapshots', views.CurrencyPriceSnapshotViewSet)

router.register(r'user_balance', views.UserBalanceViewSet)
router.register(r'language_names', views.LanguageNameViewSet)

urlpatterns = router.urls
