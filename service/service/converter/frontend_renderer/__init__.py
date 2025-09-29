"""前端渲染器模块的公共接口。"""

from __future__ import annotations

from .renderer import FileArtifact, FrontendRenderer

__all__ = ["FileArtifact", "render_project"]

def render_project(dsl: dict) -> list[FileArtifact]:
    """渲染 DSL，返回需要写入模板项目的文件列表。"""

    renderer = FrontendRenderer()
    return renderer.render_project(dsl)

