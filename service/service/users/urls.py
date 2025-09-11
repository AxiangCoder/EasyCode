from rest_framework.routers import DefaultRouter
from .views import UserView



router = DefaultRouter()
router.register(r'users', UserView, basename='user')

urlpatterns = router.urls