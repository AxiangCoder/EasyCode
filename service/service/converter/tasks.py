import logging
from celery import shared_task
from service.celeryapp import app
from django.utils import timezone
from django.db import transaction

from .models import ConversionTask
from .service import ConversionTaskService
from .exceptions import TaskNotFoundError, ConversionError
from .service.frontend_generation_service import FrontendGenerationService

logger = logging.getLogger(__name__)


@app.task(bind=True)
def convert_design_file_task(self, task_id: str):
    """
    Celery task to asynchronously convert a design file based on a ConversionTask.
    """
    try:
        task = ConversionTask.objects.get(id=task_id)
    except ConversionTask.DoesNotExist:
        logger.error(f"Task {task_id} not found.")
        raise TaskNotFoundError(task_id)

    service = ConversionTaskService()

    def progress_callback():
        """Updates the task progress in the database transaction-safely."""
        try:
            with transaction.atomic():
                # Use select_for_update to lock the row
                task_to_update = ConversionTask.objects.select_for_update().get(id=task_id)
                
                # Increment handled nodes
                task_to_update.handled_nodes = (task_to_update.handled_nodes or 0) + 1
                
                # Calculate progress
                if task_to_update.input_nodes and task_to_update.input_nodes > 0:
                    # Progress from 5% to 95%
                    progress = 5 + int((task_to_update.handled_nodes / task_to_update.input_nodes) * 90)
                else:
                    progress = 5 # Default progress if input_nodes is not set
                
                task_to_update.progress = min(progress, 95) # Cap at 95 until completion
                task_to_update.save(update_fields=['handled_nodes', 'progress'])

            # Update Celery task state
            self.update_state(state="PROGRESS", meta={"progress": task_to_update.progress})

        except ConversionTask.DoesNotExist:
            logger.warning(f"Task {task_id} not found during progress update. It might have been deleted.")
        except Exception as e:
            logger.error(f"Error updating progress for task {task_id}: {e}", exc_info=True)

    try:
        logger.info(f"Starting conversion task: {task_id}")
        self.update_state(state="PROGRESS", meta={"progress": 5})

        # This service method now handles the entire process
        service.process_conversion_task(task, progress_callback)

        # Final update
        task.refresh_from_db()
        task.progress = 100
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save(update_fields=['progress', 'status', 'completed_at'])

        logger.info(f"Conversion task {task_id} completed successfully.")

        # Trigger frontend project generation asynchronously
        generate_frontend_project_task.delay(str(task.result.id))
        return {
            "status": "completed",
            "result_id": str(task.result.id),
            "task_id": task_id
        }

    except Exception as e:
        logger.error(f"Conversion task {task_id} failed: {str(e)}", exc_info=True)
        try:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save(update_fields=['status', 'error_message', 'completed_at'])
        except Exception as update_error:
            logger.error(f"Failed to update task status to 'failed' for task {task_id}: {update_error}")
        
        # Re-raise as a known exception type for Celery
        raise ConversionError(message=str(e), task_id=task_id)


@app.task(bind=True)
def generate_frontend_project_task(self, conversion_result_id: str):
    """生成前端项目并更新 ConversionResult。"""
    logger.info("generate_frontend_project_task 开始执行，result_id=%s", conversion_result_id)
    service = FrontendGenerationService()
    try:
        result = service.generate_project(conversion_result_id)
        logger.info("前端项目生成成功，download_path=%s", result.project_download_path)
        return {
            "status": "completed",
            "conversion_result_id": conversion_result_id,
            "download_path": result.project_download_path,
        }
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("前端项目生成失败，result_id=%s", conversion_result_id)
        raise exc