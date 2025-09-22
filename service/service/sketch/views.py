from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Sketch
from .serializers import SketchSerializer
from rest_framework.parsers import MultiPartParser, FormParser


@extend_schema(tags=['草图模块'])
class SketchView(viewsets.ModelViewSet):
    queryset = Sketch.objects.all()
    serializer_class = SketchSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['post', 'delete']
    # def get(self, request):
    #     sketches = Sketch.objects.all()
    #     serializer = SketchSerializer(sketches, many=True)
    #     return Response(serializer.data)  
        # 重写 perform_create 方法，在保存新对象前执行自定义逻辑
    def perform_create(self, serializer):
        # 从 request.user 中获取当前认证的用户实例
        # 并将其作为 creator 字段的值，保存到数据库
        serializer.save(creator=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """正确删除草图（软删除）"""
        sketch = self.get_object()
        sketch.is_delete = True
        sketch.save()
        return Response(status=status.HTTP_204_NO_CONTENT)