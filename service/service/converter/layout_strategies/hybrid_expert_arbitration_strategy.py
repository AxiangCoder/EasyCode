import logging
import statistics
from typing import List, Dict, Any

from .base import BaseLayoutStrategy
from ..parsers.sketch import constants
from . import analysis_utils

try:
    from statistics import variance
except ImportError:
    def variance(data):
        if len(data) < 2:
            raise statistics.StatisticsError("variance requires at least two data points")
        mean_val = statistics.mean(data)
        return sum((x - mean_val) ** 2 for x in data) / (len(data) - 1)

logger = logging.getLogger(__name__)

class HybridExpertArbitrationStrategy(BaseLayoutStrategy):
    """
    策略一：“混合专家-仲裁”模式。
    该策略结合了基于几何规则的“专家”和基于 LLM 的“语义专家”，
    并行生成候选布局组，然后由一个仲裁者根据明确的规则解决冲突，选出最优方案。
    """

    def __init__(self, llm_service: Any):
        """
        初始化策略。
        :param llm_service: 一个实现了 .chat() 方法的 LLM 服务客户端实例。
        """
        self.llm_service = llm_service

    def analyze(self, layers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行一个分阶段的、自底向上的布局分析。
        """
        # --- 阶段一：分组 ---
        rule_based_groups = analysis_utils.analyze_with_rules(layers)
        logger.info(f"规则分析找到 {len(rule_based_groups)} 个潜在组。")

        llm_analysis = analysis_utils.analyze_with_llm(layers, self.llm_service) if self.llm_service else None
        llm_groups = llm_analysis.get("layout_groups", []) if llm_analysis else []
        logger.info(f"LLM 原始分析找到 {len(llm_groups)} 个潜在组。")

        validated_llm_groups = analysis_utils.validate_groups_geometry(llm_groups, layers)
        if len(llm_groups) > len(validated_llm_groups):
            logger.info(f"LLM 分析在校验后剩下 {len(validated_llm_groups)} 个有效组。")
        
        all_candidate_groups = rule_based_groups + validated_llm_groups

        if not all_candidate_groups:
            logger.info("所有分析方法均未找到任何组。")
            return {"container_layout": {}, "layout_groups": [], "outlier_indices": list(range(len(layers)))}

        resolved_groups = analysis_utils.resolve_conflicts(all_candidate_groups, layers)
        logger.info(f"冲突解决后找到 {len(resolved_groups)} 个最终组。")

        processed_indices = set()
        for group in resolved_groups:
            processed_indices.update(group['children_indices'])
        all_indices = set(range(len(layers)))
        outlier_indices = sorted(list(all_indices - processed_indices))

        # --- 阶段二：父容器布局确定 ---
        top_level_items = []
        for group in resolved_groups:
            group_layers = [layers[i] for i in group['children_indices']]
            if not group_layers:
                continue
            min_x = min(l["frame"]["x"] for l in group_layers)
            min_y = min(l["frame"]["y"] for l in group_layers)
            max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
            max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)
            top_level_items.append({"frame": {"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y}})
        
        for index in outlier_indices:
            top_level_items.append({"frame": layers[index]["frame"]})

        container_layout = {}
        if len(top_level_items) > 1:
            centers_x = [b['frame']['x'] + b['frame']['width'] / 2 for b in top_level_items]
            centers_y = [b['frame']['y'] + b['frame']['height'] / 2 for b in top_level_items]
            container_direction = constants.LAYOUT_DIR_COLUMN
            try:
                variance_x = variance(centers_x)
                variance_y = variance(centers_y)
                if variance_x > variance_y:
                    container_direction = constants.LAYOUT_DIR_ROW
            except statistics.StatisticsError:
                pass
            
            container_min_x = min(b["frame"]["x"] for b in top_level_items)
            container_min_y = min(b["frame"]["y"] for b in top_level_items)
            container_max_x = max(b["frame"]["x"] + b["frame"]["width"] for b in top_level_items)
            container_max_y = max(b["frame"]["y"] + b["frame"]["height"] for b in top_level_items)
            container_bounds = {
                "x": container_min_x, "y": container_min_y,
                "width": container_max_x - container_min_x,
                "height": container_max_y - container_min_y
            }

            alignment_info = analysis_utils.analyze_alignment(
                group_layers=top_level_items,
                group_bounds=container_bounds,
                direction=container_direction
            )

            container_layout = {
                "type": constants.LAYOUT_FLEX,
                "direction": container_direction
            }
            container_layout.update(alignment_info)
            container_layout.setdefault("justifyContent", "flex-start")
            container_layout.setdefault("alignItems", "flex-start")

        return {
            "container_layout": container_layout,
            "layout_groups": resolved_groups,
            "outlier_indices": outlier_indices
        }
