from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserView, LoginView, LogoutView



router = DefaultRouter()
router.register(r'users', UserView, basename='user')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]