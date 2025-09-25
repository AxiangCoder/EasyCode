import logging
from celery import shared_task
from service.celeryapp import app
from django.utils import timezone
from django.db.models import F

from .models import ConversionTask, ConversionResult
from .services import ConversionTaskService
import json
from .sketch_converter.utils import sum_nodes

logger = logging.getLogger(__name__)


@app.task(bind=True)
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

        try:
            with task.input_file.open("r") as f:
                file_content = f.read()
                if not file_content:
                    raise json.JSONDecodeError("Empty file content", file_content, 0)
                input_data = json.loads(file_content)

            # 使用新的 mode 参数来调用
            task.input_nodes = sum_nodes(input_data, mode="all")
            task.hidden_nodes = sum_nodes(input_data, mode="hidden")
            task.handled_nodes = 0
            task.save(update_fields=["input_nodes", "hidden_nodes", "handled_nodes"])
        except Exception as e:
            # 保持良好的日志记录习惯
            logger.error(f"Task {task_id}: Failed to calculate initial node counts. Error: {e}", exc_info=True)
            task.status = "failed"
            task.error_message = "无法解析输入文件或计算节点总数。"
            task.save(update_fields=["status", "error_message"])
            return # 失败后中止任务


        def progress_callback():
            """正确的进度回调函数"""
            try:
                # 先更新handled_nodes
                ConversionTask.objects.filter(id=task_id).update(handled_nodes=F("handled_nodes") + 1)
                
                # 再获取更新后的值计算进度
                task.refresh_from_db(fields=["handled_nodes", "hidden_nodes", "input_nodes"])
                logger.info (f"input_nodes: {task.input_nodes}")
                logger.info (f"handled_nodes: {task.handled_nodes}")
                logger.info (f"hidden_nodes: {task.hidden_nodes}")
                if task.input_nodes and task.input_nodes > 0:
                    progress = ((task.handled_nodes + task.hidden_nodes)  * 90 // task.input_nodes) + 5
                    logger.info (f"progress: {progress}")
                else:
                    progress = 5
                
                # 更新进度
                ConversionTask.objects.filter(id=task_id).update(progress=progress)
                
                if task_instance:
                    task_instance.update_state(state="PROGRESS", meta={"progress": progress})
                    
            except Exception as e:
                logger.warning(f"更新进度失败: {e}")

        # 更新进度：开始处理（仅在异步模式下）
        if task_instance:
            task_instance.update_state(state="PROGRESS", meta={"progress": 5})
        logger.info(f"开始处理转换任务: {task_id}")

        # 执行转换
        result = service.process_conversion_task(task, progress_callback)

        # 保存转换结果
        conversion_result = ConversionResult.objects.create(
            task=task,
            dsl_output=result.get("dsl", {}),
            html_output=result.get("html", ""),
            token_report=result.get("report", {}),
            llm_usage=result.get("llm_usage", {})
        )

        # 保存结果至文件
        conversion_result.save_html_to_file()
        # conversion_result.save_dsl_to_file()
        # conversion_result.save_token_report_to_file()

        # 更新进度：保存完成（仅在异步模式下）
        if task_instance:
            task_instance.update_state(state="PROGRESS", meta={"progress": 100})

        logger.info(f"转换任务完成: {task_id}")
        return {
            "status": "completed",
            "result_id": str(conversion_result.id),
            "task_id": task_id
        }

    except ConversionTask.DoesNotExist:
        from .exceptions import TaskNotFoundError
        error_msg = f"转换任务不存在: {task_id}"
        logger.error(error_msg)
        raise TaskNotFoundError(task_id)

    except Exception as e:
        from .exceptions import ConversionError

        error_msg = f"转换任务失败: {str(e)}"
        logger.error(f"任务 {task_id} 失败: {error_msg}")

        # 更新任务状态为失败
        try:
            task = ConversionTask.objects.get(id=task_id)
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
        except Exception as update_error:
            logger.warning(f"更新任务状态失败: {update_error}")

        # 抛出自定义异常
        raise ConversionError(
            message=error_msg,
            task_id=task_id
        )
