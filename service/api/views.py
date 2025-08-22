from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from .serializers import SketchFileSerializer
from .utils import extract_sketch_file
import os

class SketchFileViewSet(ViewSet):
    """处理Sketch文件上传的视图集"""
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = SketchFileSerializer
    
    def create(self, request):
        """
        处理文件上传并解压
        
        上传.sketch文件，文件会被解压到media目录下的同名文件夹中
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 解压.sketch文件
            output_dir = extract_sketch_file(serializer.validated_data['file'])
            
            # 返回解压后的目录路径
            return Response({
                'message': '文件处理成功',
                'output_directory': os.path.basename(output_dir)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )