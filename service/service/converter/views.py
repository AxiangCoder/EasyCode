import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import DesignTokens, ConversionTask, ConversionResult
from .serializers import (
    DesignTokensSerializer, DesignTokensListSerializer,
    ConversionTaskSerializer, ConversionTaskDetailSerializer,
    ConversionResultSerializer
)
from .permissions import (
    CanConvertDesign, CanManageDesignTokens,
    CanViewConversionResults, IsOwnerOrReadOnly
)
from .services import ConversionTaskService
from .exceptions import ConverterException


@extend_schema(tags=['设计令牌模块'])
class DesignTokensViewSet(viewsets.ModelViewSet):
    """设计令牌管理视图集"""
    queryset = DesignTokens.objects.all()
    permission_classes = [IsAuthenticated, CanManageDesignTokens]

    def get_serializer_class(self):
        if self.action == 'list':
            return DesignTokensListSerializer
        return DesignTokensSerializer

    def get_queryset(self):
        """只返回当前用户创建的或公开的设计令牌"""
        return self.queryset.filter(creator=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(tags=['转换任务模块'])
class ConversionTaskViewSet(viewsets.ModelViewSet):
    """转换任务管理视图集"""
    queryset = ConversionTask.objects.all()
    permission_classes = [IsAuthenticated, CanConvertDesign, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversionTaskDetailSerializer
        return ConversionTaskSerializer

    def get_queryset(self):
        """只返回当前用户创建的任务"""
        return self.queryset.filter(creator=self.request.user)

    def perform_create(self, serializer):
        task = serializer.save(creator=self.request.user)

        # 同步执行转换任务（注释掉异步调用）
        from .tasks import convert_design_file_task
        convert_design_file_task.delay(str(task.id))

        # 使用同步版本执行转换任务
        # from .tasks import convert_design_file_task_sync
        # from .exceptions import ConverterException

        """ try:
            result = convert_design_file_task_sync(str(task.id))
            print(f"同步任务执行完成: {result}")
        except ConverterException:
            # 自定义异常会由全局异常处理器处理
            raise
        except Exception as e:
            # 其他异常包装为ConverterException
            from .exceptions import ConversionError
            raise ConversionError(
                message=f"转换任务执行失败: {str(e)}",
                task_id=str(task.id)
            ) """

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取任务进度"""
        task = self.get_object()
        service = ConversionTaskService()

        progress_data = service.get_task_progress(task)
        return Response(progress_data)

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重新执行转换任务"""
        task = self.get_object()

        # 检查任务状态
        if task.status == 'processing':
            return Response(
                {'error': '任务正在执行中'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 重置任务状态
        task.status = 'pending'
        task.progress = 0
        task.error_message = ''
        task.started_at = None
        task.completed_at = None
        task.save()

        # 同步执行任务（注释掉异步调用）
        # from .tasks import convert_design_file_task
        # convert_design_file_task.delay(str(task.id))

        # 使用同步版本重试转换任务
        from .tasks import convert_design_file_task_sync
        from .exceptions import ConverterException, ConversionError

        try:
            result = convert_design_file_task_sync(str(task.id))
            print(f"同步重试任务执行完成: {result}")
        except ConverterException:
            # 自定义异常会由全局异常处理器处理
            raise
        except Exception as e:
            # 其他异常包装为ConverterException
            raise ConversionError(
                message=f"转换任务重试失败: {str(e)}",
                task_id=str(task.id)
            )

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消转换任务"""
        task = self.get_object()

        if task.status not in ['pending', 'processing']:
            return Response(
                {'error': '只能取消待处理或执行中的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = 'failed'
        task.error_message = '用户取消'
        task.completed_at = timezone.now()
        task.save()

        serializer = self.get_serializer(task)
        return Response(serializer.data)


@extend_schema(tags=['转换结果模块'])
class ConversionResultViewSet(viewsets.ReadOnlyModelViewSet):
    """转换结果查看视图集"""
    queryset = ConversionResult.objects.all()
    serializer_class = ConversionResultSerializer
    permission_classes = [IsAuthenticated, CanViewConversionResults]

    def get_queryset(self):
        """只返回当前用户任务的结果"""
        return self.queryset.filter(task__creator=self.request.user)

    @action(detail=True, methods=['get'])
    def download_dsl(self, request, pk=None):
        """下载DSL结果文件"""
        result = self.get_object()

        # 创建文件内容
        dsl_content = json.dumps(result.dsl_output, ensure_ascii=False, indent=2)
        file_content = ContentFile(dsl_content.encode('utf-8'))

        # 返回文件响应
        response = FileResponse(
            file_content,
            content_type='application/json',
            as_attachment=True,
            filename=f'{result.task.name}_dsl.json'
        )
        return response

    @action(detail=True, methods=['get'])
    def download_html(self, request, pk=None):
        """下载HTML预览文件"""
        result = self.get_object()

        if not result.html_output:
            return Response(
                {'error': 'HTML预览不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 创建文件内容
        file_content = ContentFile(result.html_output.encode('utf-8'))

        # 返回文件响应
        response = FileResponse(
            file_content,
            content_type='text/html',
            as_attachment=True,
            filename=f'{result.task.name}_preview.html'
        )
        return response

    @action(detail=True, methods=['get'])
    def download_report(self, request, pk=None):
        """下载令牌报告文件"""
        result = self.get_object()

        # 创建文件内容
        report_content = json.dumps(result.token_report, ensure_ascii=False, indent=2)
        file_content = ContentFile(report_content.encode('utf-8'))

        # 返回文件响应
        response = FileResponse(
            file_content,
            content_type='application/json',
            as_attachment=True,
            filename=f'{result.task.name}_token_report.json'
        )
        return response