"""将 DSL 渲染为前端项目文件。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class FileArtifact:
    """代表生成前端项目时写入磁盘的单个文件。"""

    path: Path
    content: str

    def iter_segments(self) -> Iterable[str]:  # pragma: no cover - 调试辅助
        yield self.content


class FrontendRenderer:
    """将 DSL 渲染为 Vite + React + TS 项目需要的文件。"""

    PAGES_DIR = Path("src/pages")
    ROUTER_FILE = Path("src/router.tsx")
    APP_FILE = Path("src/App.tsx")

    def render_project(self, dsl: dict) -> list[FileArtifact]:
        pages = self._extract_pages(dsl)
        page_artifacts = [self._render_page_file(page) for page in pages]
        router_artifact = self._render_router_file(pages)
        app_artifact = self._render_app_file()
        return [*page_artifacts, router_artifact, app_artifact]

    def _extract_pages(self, dsl: dict) -> list[dict]:
        pages = dsl.get("children") or []
        if not pages:
            pages = [dsl]
        return pages

    def _render_page_file(self, page: dict) -> FileArtifact:
        component_name = self._to_component_name(page.get("name") or "Page")
        body = self._render_node(page)
        content = "\n".join([
            "import { FC } from 'react'",
            "",
            f"const {component_name}: FC = () => (",
            body,
            ")",
            "",
            f"export default {component_name}",
            "",
        ])
        path = self.PAGES_DIR / f"{component_name}.tsx"
        return FileArtifact(path=path, content=content)

    def _render_router_file(self, pages: list[dict]) -> FileArtifact:
        imports = []
        routes = []
        for index, page in enumerate(pages):
            component_name = self._to_component_name(page.get("name") or f"Page{index + 1}")
            route_path = f"/{component_name}"
            imports.append(f"import {component_name} from './pages/{component_name}'")
            routes.append(
                f"        {{\n            element: <{component_name} />,\n            path: '{route_path}',\n        }},"
            )
        content = "\n".join([
            "import { createBrowserRouter } from 'react-router-dom'",
            *imports,
            "",
            "export const router = createBrowserRouter([",
            *routes,
            "])",
            "",
        ])
        path = self.ROUTER_FILE
        return FileArtifact(path=path, content=content)

    def _render_app_file(self) -> FileArtifact:
        content = "\n".join([
            "import { Outlet } from 'react-router-dom'",
            "",
            "const App = () => {",
            "  return <Outlet />",
            "}",
            "",
            "export default App",
            "",
        ])
        return FileArtifact(path=self.APP_FILE, content=content)

    def _render_node(self, node: dict, depth: int = 0) -> str:
        node_type = node.get("type")
        ind = "  " * depth
        if node_type == "text":
            text_content = node.get("content", {}).get("text") or node.get("name") or ""
            return f"{ind}<span>{self._escape_jsx(text_content)}</span>"
        tag = "div" if node_type not in {"img", "text"} else "img"
        children = node.get("children") or []
        props = []
        if tag == "img":
            props.append("alt=\"\"")
        style_dict = self._convert_styles(node)
        if style_dict:
            props.append(f"style={{ {self._format_style(style_dict)} }}")
        if children:
            children_str = "\n".join(self._render_node(child, depth + 1) for child in children)
            return f"{ind}<{tag} {' '.join(props)}>\n{children_str}\n{ind}</{tag}>"
        return f"{ind}<{tag} {' '.join(props)} />" if props else f"{ind}<{tag} />"

    def _convert_styles(self, node: dict) -> dict:
        style = node.get("style") or {}
        layout = node.get("layout") or {}
        result: dict[str, str | int | float] = {}
        for key, value in style.items():
            result[self._to_camel_case(key)] = value
        position = layout.get("position")
        if position:
            result["position"] = position
        for key in ("top", "left", "right", "bottom"):
            if key in layout:
                result[key] = layout[key]
        return result

    def _format_style(self, style: dict) -> str:
        segments = []
        for key, value in style.items():
            if isinstance(value, str):
                segments.append(f"{key}: '{value}'")
            else:
                segments.append(f"{key}: {value}")
        return ", ".join(segments)

    def _to_component_name(self, name: str) -> str:
        base = ''.join(filter(str.isalnum, name)) or "Page"
        base = base[0].upper() + base[1:]
        return base if base.endswith("Page") else f"{base}Page"

    def _to_route_path(self, name: str | None) -> str:
        if not name:
            return "page"
        return '-'.join(filter(None, ''.join(ch if ch.isalnum() else ' ' for ch in name).lower().split()))

    def _to_camel_case(self, key: str) -> str:
        parts = key.replace('-', '_').split('_')
        return parts[0] + ''.join(part.capitalize() for part in parts[1:] if part)

    def _escape_jsx(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&#39;")
            .replace('"', "&quot;")
        )

