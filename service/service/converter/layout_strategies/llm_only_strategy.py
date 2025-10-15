import logging
import json
from typing import List, Dict, Any

from .base import BaseLayoutStrategy
from ..parsers.sketch import constants
from .analysis_utils import _load_prompt, _call_llm  # 复用现有函数

logger = logging.getLogger(__name__)

class LLMOnlyStrategy(BaseLayoutStrategy):
    """
    全 LLM 布局分析策略：仅使用大模型进行分组和属性计算。
    输出格式与 HybridExpertArbitrationStrategy 一致。
    """

    def __init__(self, llm_service: Any):
        self.llm_service = llm_service

    def analyze(self, parent_layer: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 LLM 进行完整布局分析。
        """
        layers = parent_layer.get("layers", [])

        if not layers:
            return {"container_layout": {}, "layout_groups": [], "outlier_indices": list(range(len(layers)))}

        # 从 parent_layer 提取 bounds 和其他 info
        logger.info(f"Parent layer frame: {parent_layer['frame']}")
        if "frame" in parent_layer:
            frame = parent_layer["frame"]
            parent_bounds = {
                "x": frame.get("x", 0),
                "y": frame.get("y", 0),
                "width": frame.get("width", 0),
                "height": frame.get("height", 0)
            }
            parent_name = parent_layer.get("name", "Unnamed")
        else:
            # Fallback 计算
            if layers:
                parent_min_x = min(l["frame"].get("x", 0) for l in layers)
                parent_min_y = min(l["frame"].get("y", 0) for l in layers)
                parent_max_x = max(l["frame"].get("x", 0) + l["frame"].get("width", 0) for l in layers)
                parent_max_y = max(l["frame"].get("y", 0) + l["frame"].get("height", 0) for l in layers)
                parent_bounds = {
                    "x": 0, "y": 0,
                    "width": max(parent_max_x - parent_min_x, 0),
                    "height": max(parent_max_y - parent_min_y, 0)
                }
            else:
                parent_bounds = {"x": 0, "y": 0, "width": 0, "height": 0}
            parent_name = "Virtual Group"

        # 简化 layers
        simplified_layers = [
            {"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")}
            for l in layers
        ]

        prompt_template = _load_prompt("expert_layout_analysis_prompt")
        if not prompt_template:
            logger.error("专家提示词加载失败，回退到空结果。")
            return {"container_layout": {}, "layout_groups": [], "outlier_indices": list(range(len(layers)))}

        simplified_layers_json = json.dumps(simplified_layers, indent=2)
        parent_info = f"Parent container name: {parent_name}\nParent container bounds: {json.dumps(parent_bounds)}\n"
        prompt = f"{prompt_template}\n{parent_info}Input Layers:\n```json\n{simplified_layers_json}\n```"

        logger.info(f"Prompt: {prompt}")

        try:
            response = _call_llm(prompt, self.llm_service)
            layout_analysis = json.loads(response)
            logger.info(f"LLM 分析结果: {layout_analysis}")

            # 处理嵌套分组
            layout_analysis = self._process_nested_groups(layout_analysis, layers)

            # 确保输出格式一致
            return {
                "container_layout": layout_analysis.get("container_layout", {}),
                "layout_groups": layout_analysis.get("layout_groups", []),
                "outlier_indices": layout_analysis.get("outlier_indices", [])
            }
        except Exception as e:
            logger.error(f"LLM 分析失败: {e}")
            return {
                "container_layout": {"type": "absolute", "position": "absolute"},
                "layout_groups": [],
                "outlier_indices": list(range(len(layers)))
            }

    def _process_nested_groups(self, analysis: Dict[str, Any], layers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        递归处理嵌套 layout_groups。
        """
        groups = analysis.get("layout_groups", [])
        for group in groups:
            if "layout_groups" in group and group["layout_groups"]:
                sub_indices = group.get("children_indices", [])
                sub_layers = [layers[i] for i in sub_indices if i < len(layers)]
                if sub_layers:  # 避免空 layers 递归
                    sub_analysis = self.analyze(sub_layers)
                    group["layout_groups"] = sub_analysis["layout_groups"]
                    group["outlier_indices"] = sub_analysis.get("outlier_indices", [])
        return analysis
