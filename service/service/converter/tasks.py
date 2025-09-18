import logging
from celery import shared_task
from django.utils import timezone

from .models import ConversionTask, ConversionResult
from .services import ConversionTaskService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def convert_design_file_task(self, task_id):
    """
    异步转换设计文件任务

    Args:
        task_id: 转换任务ID
    """
    return convert_design_file_task_sync(task_id, task_instance=self)


def convert_design_file_task_sync(task_id, task_instance=None):
    """
    同步转换设计文件任务

    Args:
        task_id: 转换任务ID
        task_instance: Celery任务实例（用于异步调用）
    """
    try:
        # 获取任务实例
        task = ConversionTask.objects.get(id=task_id)

        # 创建服务实例
        service = ConversionTaskService()

        # 更新进度：开始处理（仅在异步模式下）
        if task_instance:
            task_instance.update_state(state='PROGRESS', meta={'progress': 10})
        logger.info(f"开始处理转换任务: {task_id}")

        # 执行转换
        result = service.process_conversion_task(task)

        # 更新进度：转换完成（仅在异步模式下）
        if task_instance:
            task_instance.update_state(state='PROGRESS', meta={'progress': 80})

        # 保存转换结果
        conversion_result = ConversionResult.objects.create(
            task=task,
            dsl_output=result['dsl'],
            html_output=result['html'],
            token_report=result.get('report', {})
        )

        # 更新进度：保存完成（仅在异步模式下）
        if task_instance:
            task_instance.update_state(state='PROGRESS', meta={'progress': 100})

        logger.info(f"转换任务完成: {task_id}")
        return {
            'status': 'completed',
            'result_id': str(conversion_result.id),
            'task_id': task_id
        }

    except ConversionTask.DoesNotExist:
        error_msg = f"转换任务不存在: {task_id}"
        logger.error(error_msg)
        raise Exception(error_msg)

    except Exception as e:
        error_msg = f"转换任务失败: {str(e)}"
        logger.error(f"任务 {task_id} 失败: {error_msg}")

        # 更新任务状态为失败
        try:
            task = ConversionTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
        except Exception:
            pass  # 忽略更新失败的错误

        raise Exception(error_msg)
