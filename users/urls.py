from rest_framework.routers import DefaultRouter
from .views import ReferralCodeViewSet, ReferralsViewSet, UserViewSetUpdated


router = DefaultRouter()
router.register("auth/users", UserViewSetUpdated)
router.register("my_referral_codes", ReferralCodeViewSet)
router.register("my_referrals", ReferralsViewSet)

urlpatterns = router.urls
