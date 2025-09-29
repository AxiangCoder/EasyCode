import json
import logging
from typing import Dict, Any, Optional, Callable

from ..models import ConversionTask, ConversionResult
from .. import parsers
from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class DesignConverterService:
    """Orchestrates the design conversion process using a pluggable parser architecture."""

    def convert_design(self, task: ConversionTask, progress_callback: Optional[Callable] = None) -> ConversionResult:
        """
        Performs the full conversion workflow for a given task.

        1.  Pre-calculates node count.
        2.  Executes the appropriate parser.
        3.  Saves all results to the database.

        :param task: The ConversionTask instance to process.
        :param progress_callback: Optional callback for progress tracking.
        :return: The created ConversionResult instance.
        """
        try:
            # 1. Get Parser and Source Data
            ParserClass = parsers.get_parser_class(task.source_type)
            source_data = self._get_source_data(task)
            tokens_data = self._get_tokens_data(task)

            # 2. Pre-calculation and immediate update
            total_nodes = ParserClass.count_nodes(source_data)
            task.input_nodes = total_nodes
            task.save(update_fields=['input_nodes'])
            logger.info(f"Task {task.id}: Pre-calculated input nodes: {total_nodes}")

            # 3. Execute Conversion
            parser = ParserClass(source_data, tokens_data)
            dsl_dict, metadata_dict = parser.run(progress_callback=progress_callback)
            logger.info(f"Task {task.id}: Conversion executed successfully.")

            # 4. Save Results
            result = ConversionResult.objects.create(
                task=task,
                dsl_output=dsl_dict,
                token_report=metadata_dict.get("token_report", {}),
                llm_usage=metadata_dict.get("llm_usage", {}),
            )
            logger.info(f"Task {task.id}: Conversion result saved successfully.")

            return result

        except Exception as e:
            logger.error(f"Task {task.id}: Conversion failed. Reason: {str(e)}", exc_info=True)
            raise ConversionError(f"文件转换失败: {str(e)}")

    def _get_source_data(self, task: ConversionTask) -> Dict[str, Any]:
        """Retrieves source data from file or URL based on task type."""
        if task.source_type == 'sketch':
            if not task.input_file:
                raise ValueError("Sketch source type requires an input file.")
            try:
                with task.input_file.open('r') as f:
                    # Read the file content as text and then parse it as JSON
                    content = f.read()
                    return json.loads(content)
            except Exception as e:
                raise IOError(f"Failed to read or parse Sketch file: {task.input_file.name}. Error: {e}")

        elif task.source_type == 'figma':
            # Here you would implement fetching data from Figma API using task.source_url
            raise NotImplementedError("Figma parser is not yet implemented.")
        else:
            raise ValueError(f"Unsupported source type: {task.source_type}")

    def _get_tokens_data(self, task: ConversionTask) -> Dict[str, Any]:
        """Loads design tokens data if available."""
        if not task.design_tokens or not task.design_tokens.file:
            return {}
        try:
            with task.design_tokens.file.open('r') as f:
                content = f.read()
                return json.loads(content)
        except Exception as e:
            logger.warning(f"Could not load design tokens for task {task.id}. Reason: {e}")
            return {}