import logging
from typing import Dict, Any, Optional,Callable
from django.utils import timezone
from .design_converter_service import DesignConverterService
from ..models import ConversionTask

logger = logging.getLogger(__name__)

class ConversionTaskService:
    """转换任务服务"""

    def __init__(self):
        self.converter_service = DesignConverterService()

    def process_conversion_task(
        self, task, progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        处理转换任务

        Args:
            task: ConversionTask实例

        Returns:
            转换结果字典
        """
        try:
            # 更新任务状态
            task.status = "processing"
            task.started_at = timezone.now()
            task.save()

            # 执行转换
            result = self.converter_service.convert_design(
                task=task,
                progress_callback=progress_callback,
            )
            task_to_update = ConversionTask.objects.get(id=task.id)

            # 更新任务状态
            task_to_update.status = "completed"
            task_to_update.progress = 100
            task_to_update.completed_at = timezone.now()
            task_to_update.llm_usage = result.llm_usage
            task_to_update.save()

            return result

        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            task.save()
            raise

    def get_task_progress(self, task) -> Dict[str, Any]:
        """获取任务进度"""
        return {
            "task_id": str(task.id),
            "status": task.status,
            "progress": task.progress,
            "error_message": task.error_message,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "input_nodes": task.input_nodes,
            "handled_nodes": task.handled_nodes,
            "hidden_nodes": task.hidden_nodes,
        }
