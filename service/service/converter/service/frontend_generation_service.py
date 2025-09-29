"""前端项目生成服务，将 DSL 渲染成可下载的项目压缩包。"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Optional

from django.conf import settings
from django.db import transaction

from ..frontend_renderer import FileArtifact, render_project
from ..models import ConversionResult

logger = logging.getLogger(__name__)


class FrontendGenerationService:
    """负责将 DSL 渲染写入模板，并生成压缩包。"""

    TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "project_templates" / "vite-react-ts-tailwind"
    BASE_OUTPUT_DIR = Path(getattr(settings, "MEDIA_ROOT", Path.cwd())) / "conversion_out"

    def generate_project(
        self,
        result_id: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> ConversionResult:
        conversion_result = ConversionResult.objects.select_related("task").get(id=result_id)

        if not conversion_result.dsl_output:
            raise ValueError("ConversionResult 缺少 DSL 输出，无法生成前端项目。")

        logger.info("开始生成前端项目压缩包，result_id=%s", result_id)

        artifacts = render_project(conversion_result.dsl_output)

        if progress_callback:
            progress_callback(80)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            shutil.copytree(self.TEMPLATE_DIR, tmp_path, dirs_exist_ok=True)
            if progress_callback:
                progress_callback(85)
            self._write_artifacts(tmp_path, artifacts)
            if progress_callback:
                progress_callback(90)

            task_output_dir = self.BASE_OUTPUT_DIR / str(conversion_result.task_id)
            task_output_dir.mkdir(parents=True, exist_ok=True)
            archive_base = task_output_dir / "code"
            archive_zip_path = archive_base.with_suffix(".zip")
            if archive_zip_path.exists():
                archive_zip_path.unlink()
            archive_path = Path(shutil.make_archive(str(archive_base), "zip", tmp_path))

        if progress_callback:
            progress_callback(95)

        relative_archive_path = Path("conversion_out") / str(conversion_result.task_id) / "code.zip"

        logger.info(
            "前端项目压缩包生成完成: result_id=%s, path=%s",
            result_id,
            archive_path,
        )

        with transaction.atomic():
            conversion_result.project_download_path = str(relative_archive_path)
            conversion_result.save(update_fields=["project_download_path"])

        return conversion_result

    def _write_artifacts(self, tmp_path: Path, artifacts: list[FileArtifact]) -> None:
        for artifact in artifacts:
            target_path = tmp_path / artifact.path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(artifact.content, encoding="utf-8")

