import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from django.utils import timezone

# 暂时注释掉导入，避免依赖问题
from .sketch_converter.converter import SketchConverter
from .sketch_converter import config as converter_config
from .exceptions import (
    ConverterException, FileProcessingError, ValidationError,
    ConversionError, UnsupportedFileFormatError
)

logger = logging.getLogger(__name__)


class DesignConverterService:
    """设计文件转换服务"""

    SUPPORTED_FORMATS = ['sketch', 'json']

    def __init__(self):
        self.converter_config = converter_config

    def convert_design_file(
        self,
        input_file_path: str,
        tokens_file_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        转换设计文件

        Args:
            input_file_path: 输入文件路径
            tokens_file_path: 令牌文件路径
            output_dir: 输出目录

        Returns:
            包含转换结果的字典
        """
        try:
            # 验证输入文件
            self._validate_input_file(input_file_path)

            # 加载令牌配置
            token_maps = self._load_design_tokens(tokens_file_path)

            # 创建转换器并执行转换
            converter = SketchConverter(
                input_file=input_file_path,
                tokens_file=tokens_file_path or converter_config.DEFAULT_TOKENS_INPUT,
                dsl_output_file=str(self._get_output_path(output_dir, 'dsl_output.json')),
                report_output_file=str(self._get_output_path(output_dir, 'token_report.json')),
                progress_callback = progress_callback
            )

            # 执行转换
            dsl_output = converter.run()

            # 生成HTML预览
            html_output = self._generate_html_preview(dsl_output)

            # 读取令牌报告
            token_report = self._read_token_report(
                self._get_output_path(output_dir, 'token_report.json')
            )

            return {
                'dsl': dsl_output,
                'html': html_output,
                'report': token_report,
                'llm_usage': converter.llm_usage,
            }

        except Exception as e:
            logger.error(f"转换失败: {e}")
            raise ConversionError(f"文件转换失败: {str(e)}")

    def _validate_input_file(self, file_path: str) -> None:
        """验证输入文件"""
        if not Path(file_path).exists():
            raise FileProcessingError(f"输入文件不存在: {file_path}", file_path)

        file_extension = Path(file_path).suffix.lower()
        if file_extension not in ['.json', '.sketch']:
            raise UnsupportedFileFormatError(
                file_extension,
                self.SUPPORTED_FORMATS
            )

        # 检查文件大小
        file_size = Path(file_path).stat().st_size
        if file_size > converter_config.MAX_FILE_SIZE:
            raise ValidationError(
                f"文件过大: {file_size} bytes, 最大允许: {converter_config.MAX_FILE_SIZE} bytes"
            )

    def _load_design_tokens(self, tokens_file_path: Optional[str]) -> Optional[Dict[str, Any]]:
        """加载设计令牌配置"""
        if not tokens_file_path:
            return None

        try:
            with open(tokens_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"令牌文件不存在: {tokens_file_path}")
            return None
        except json.JSONDecodeError as e:
            raise ValidationError(f"令牌文件格式错误: {e}")

    def _get_output_path(self, output_dir: Optional[str], filename: str) -> Path:
        """获取输出文件路径"""
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            return output_path / filename
        else:
            # 使用临时目录
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / 'design_converter'
            temp_dir.mkdir(exist_ok=True)
            return temp_dir / filename

    def _generate_html_preview(self, dsl_output: Dict[str, Any]) -> str:
        """生成HTML预览"""
        try:
            from .dsl_to_html import dsl_node_to_html

            # 生成HTML内容
            body_content = dsl_node_to_html(dsl_output)
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSL Preview</title>
    <style>
        body {{ margin: 0; font-family: sans-serif; }}
        div {{ box-sizing: border-box; }}
    </style>
</head>
<body>
{body_content}
</body>
</html>"""

            return html_content

        except Exception as e:
            logger.error(f"HTML预览生成失败: {e}")
            return ""

    def _read_token_report(self, report_path: Path) -> Dict[str, Any]:
        """读取令牌报告"""
        try:
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"读取令牌报告失败: {e}")

        return {}


class ConversionTaskService:
    """转换任务服务"""

    def __init__(self):
        self.converter_service = DesignConverterService()

    def process_conversion_task(self, task, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        处理转换任务

        Args:
            task: ConversionTask实例

        Returns:
            转换结果字典
        """
        try:
            # 更新任务状态
            task.status = 'processing'
            task.started_at = timezone.now()
            task.save()

            # 执行转换
            result = self.converter_service.convert_design_file(
                input_file_path=task.input_file.path,
                tokens_file_path=task.design_tokens.file.path if task.design_tokens else None,
                progress_callback=progress_callback
            )

            # 更新任务状态
            task.status = 'completed'
            task.progress = 100
            task.completed_at = timezone.now()
            task.llm_usage = result.get('llm_usage', None)
            task.save()

            return result

        except Exception as e:
            # 更新任务状态为失败
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            raise

    def get_task_progress(self, task) -> Dict[str, Any]:
        """获取任务进度"""
        return {
            'task_id': str(task.id),
            'status': task.status,
            'progress': task.progress,
            'error_message': task.error_message,
            'started_at': task.started_at,
            'completed_at': task.completed_at,
            'input_nodes': task.input_nodes,
            'handled_nodes': task.handled_nodes,
            'hidden_nodes': task.hidden_nodes,
        }
