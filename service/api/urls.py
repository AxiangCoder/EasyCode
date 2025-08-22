from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SketchFileViewSet

router = DefaultRouter()
router.register(r'sketch-files', SketchFileViewSet, basename='sketch-files')

urlpatterns = [
    path('', include(router.urls)),
]