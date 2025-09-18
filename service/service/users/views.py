from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.

@extend_schema(tags=['用户管理模块'])
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
            # self.permission_classes = [IsAdminUser]
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    

@extend_schema(tags=['用户认证模块'])
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user, many=False)
            return Response(status=status.HTTP_200_OK, data={'token': token.key, 'user': user_serializer.data})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
@extend_schema(tags=['用户认证模块'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
