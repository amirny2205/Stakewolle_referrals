from .views import UserViewSetUpdated, ReferralCodeList, ReferralCodeDetail
from rest_framework.routers import DefaultRouter
from django.urls import path


router = DefaultRouter()
router.register("auth/users", UserViewSetUpdated)

urlpatterns = router.urls

urlpatterns += [
    path('my_referral_codes/', ReferralCodeList.as_view()),
    path('my_referral_codes/<str:pk>/', ReferralCodeDetail.as_view()),
]
