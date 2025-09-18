from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DesignTokensViewSet, ConversionTaskViewSet, ConversionResultViewSet

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'tokens', DesignTokensViewSet, basename='designtokens')
router.register(r'tasks', ConversionTaskViewSet, basename='conversiontask')
router.register(r'results', ConversionResultViewSet, basename='conversionresult')

# URL模式
urlpatterns = [
    # 包含路由器的URL
    path('', include(router.urls)),
]
