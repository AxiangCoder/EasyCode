from rest_framework.routers import DefaultRouter
from .views import SketchView


router = DefaultRouter()
router.register(r'sketch', SketchView, basename='sketch')

urlpatterns = router.urls