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
            task.phase = "dsl_conversion"
            task.started_at = timezone.now()
            task.progress = max(task.progress, 5)
            task.save(update_fields=[
                "status",
                "phase",
                "started_at",
                "progress",
            ])

            # 执行转换
            result = self.converter_service.convert_design(
                task=task,
                progress_callback=progress_callback,
            )

            try:
                archived_path = result.save_dsl_to_file()
                if archived_path:
                    logger.info("Task %s: DSL archived to %s", task.id, archived_path)
            except Exception as archive_exc:  # pylint: disable=broad-except
                logger.error(
                    "Task %s: Failed to archive DSL output: %s",
                    task.id,
                    archive_exc,
                    exc_info=True,
                )
                raise

            task_to_update = ConversionTask.objects.get(id=task.id)

            # 更新任务状态
            task_to_update.phase = "frontend_generation"
            task_to_update.progress = 70
            task_to_update.save(update_fields=[
                "phase",
                "progress",
            ])

            return result

        except Exception as e:
            # 更新任务状态为失败
            task_to_update = ConversionTask.objects.get(id=task.id)
            task_to_update.status = "failed"
            task_to_update.phase = "dsl_conversion"
            task_to_update.error_message = str(e)
            task_to_update.completed_at = timezone.now()
            task_to_update.save(update_fields=[
                "status",
                "phase",
                "error_message",
                "completed_at",
            ])
            raise

    def get_task_progress(self, task) -> Dict[str, Any]:
        """获取任务进度"""
        return {
            "task_id": str(task.id),
            "status": task.status,
            "progress": task.progress,
            "phase": task.phase,
            "error_message": task.error_message,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "input_nodes": task.input_nodes,
            "handled_nodes": task.handled_nodes,
            "hidden_nodes": task.hidden_nodes,
        }
