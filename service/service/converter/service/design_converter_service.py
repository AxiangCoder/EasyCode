import json
import logging
from typing import Dict, Any, Optional,Callable
from pathlib import Path

from ..sketch_converter.converter import SketchConverter
from ..sketch_converter import config as converter_config
from ..exceptions import (
    FileProcessingError,
    ValidationError,
    ConversionError,
    UnsupportedFileFormatError,
)

from django.conf import settings

logger = logging.getLogger(__name__)

class DesignConverterService:
    """设计文件转换服务"""

    SUPPORTED_FORMATS = ["sketch", "json"]

    def __init__(self):
        self.converter_config = converter_config

    def convert_design_file(
        self,
        input_file_path: str,
        tokens_file_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
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
            self._load_design_tokens(tokens_file_path)

            # 创建转换器并执行转换
            converter = SketchConverter(
                input_file=input_file_path,
                tokens_file=tokens_file_path or settings.DEFAULT_TOKENS_INPUT,
                dsl_output_file=str(
                    self._get_output_path(output_dir, "dsl_output.json")
                ),
                report_output_file=str(
                    self._get_output_path(output_dir, "token_report.json")
                ),
                progress_callback=progress_callback,
            )

            # 执行转换
            dsl_output = converter.run()

            # 生成HTML预览
            html_output = self._generate_html_preview(dsl_output)

            # 读取令牌报告
            token_report = self._read_token_report(
                self._get_output_path(output_dir, "token_report.json")
            )

            return {
                "dsl": dsl_output,
                "html": html_output,
                "report": token_report,
                "llm_usage": getattr(converter, "llm_usage", {}),
            }

        except Exception as e:
            logger.error(f"转换失败: {e}")
            raise ConversionError(f"文件转换失败: {str(e)}")

    def _validate_input_file(self, file_path: str) -> None:
        """验证输入文件"""
        if not Path(file_path).exists():
            raise FileProcessingError(f"输入文件不存在: {file_path}", file_path)

        file_extension = Path(file_path).suffix.lower()
        if file_extension not in [".json", ".sketch"]:
            raise UnsupportedFileFormatError(file_extension, self.SUPPORTED_FORMATS)

        # 检查文件大小
        file_size = Path(file_path).stat().st_size
        if file_size > converter_config.MAX_FILE_SIZE:
            raise ValidationError(
                f"文件过大: {file_size} bytes, 最大允许: {converter_config.MAX_FILE_SIZE} bytes"
            )

    def _load_design_tokens(
        self, tokens_file_path: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """加载设计令牌配置"""
        if not tokens_file_path:
            return None

        try:
            with open(tokens_file_path, "r", encoding="utf-8") as f:
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

            temp_dir = Path(tempfile.gettempdir()) / "design_converter"
            temp_dir.mkdir(exist_ok=True)
            return temp_dir / filename

    def _generate_html_preview(self, dsl_output: Dict[str, Any]) -> str:
        pass

    def _read_token_report(self, report_path: Path) -> Dict[str, Any]:
        """读取令牌报告"""
        try:
            if report_path.exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"读取令牌报告失败: {e}")

        return {}

