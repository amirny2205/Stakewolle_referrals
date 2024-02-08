from .views import UserViewSetUpdated
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("auth/users", UserViewSetUpdated)

urlpatterns = router.urls
