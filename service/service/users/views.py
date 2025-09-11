from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import User
from .serializers import UserSerializer, UserCreateSerializer

# Create your views here.

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    def get_serializer_class(self):
        # 根据不同的动作（action），使用不同的序列化器
        # 如果是创建用户，使用 UserCreateSerializer
        if self.action == 'create':
            return UserCreateSerializer
        # 对于其他操作（查询、更新、删除），使用 UserSerializer
        return UserSerializer

    def get_permissions(self):
        # 如果是创建用户，允许任何人访问
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        # 对于其他操作，只允许管理员访问
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
