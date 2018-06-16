from rest_framework import routers
from src.api.v1.core import views


router = routers.DefaultRouter()

router.register(r'comments', views.CommentViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'topics_test', views.TopicLimitOffsetViewSet)
router.register(r'user_balance', views.UserBalanceViewSet)
router.register(r'language_names', views.LanguageNameViewSet)

urlpatterns = router.urls
