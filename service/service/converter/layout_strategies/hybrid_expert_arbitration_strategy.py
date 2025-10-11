import json
import logging
import os
import statistics
from typing import List, Dict, Any

from .base import BaseLayoutStrategy
from ..parsers.sketch import config, constants

try:
    from statistics import variance
except ImportError:
    # 为 Python 3.8 之前的版本提供一个简单的 variance 实现
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
        执行完整的混合布局分析。
        :param layers: 要分析的图层列表。
        :return: 一个包含 'layout_groups' 和 'outlier_indices' 的字典。
        """
        # 1. 从几何规则引擎获取所有可能的候选组
        rule_based_groups = self._analyze_with_rules(layers)
        logger.info(f"规则分析找到 {len(rule_based_groups)} 个潜在组。")

        # 2. 从 LLM 获取语义候选组
        llm_analysis = self._analyze_with_llm(layers) if self.llm_service else None
        llm_groups = llm_analysis.get("layout_groups", []) if llm_analysis else []
        logger.info(f"LLM 原始分析找到 {len(llm_groups)} 个潜在组。")

        # 3. 对 LLM 的结果进行几何合理性校验
        validated_llm_groups = self._validate_groups_geometry(llm_groups, layers)
        if len(llm_groups) > len(validated_llm_groups):
            logger.info(f"LLM 分析在校验后剩下 {len(validated_llm_groups)} 个有效组。")

        # 4. 合并所有候选组并通过冲突解决机制进行仲裁
        all_candidate_groups = rule_based_groups + validated_llm_groups

        if not all_candidate_groups:
            logger.info("所有分析方法均未找到任何组。")
            return {"layout_groups": [], "outlier_indices": list(range(len(layers)))}

        logger.info(f"在 {len(all_candidate_groups)} 个总候选组中解决冲突。")
        resolved_groups = self._resolve_conflicts(all_candidate_groups, layers)
        logger.info(f"冲突解决后找到 {len(resolved_groups)} 个最终组。")

        # 5. 确定未被任何组包含的离群点
        processed_indices = set()
        for group in resolved_groups:
            processed_indices.update(group['children_indices'])

        all_indices = set(range(len(layers)))
        outlier_indices = sorted(list(all_indices - processed_indices))

        # 6. 分析容器的主布局方向
        container_direction = constants.LAYOUT_DIR_COLUMN  # 默认为列
        top_level_items_bounds = []

        # 获取所有组的边界
        for group in resolved_groups:
            group_layers = [layers[i] for i in group['children_indices']]
            if not group_layers:
                continue
            min_x = min(l["frame"]["x"] for l in group_layers)
            min_y = min(l["frame"]["y"] for l in group_layers)
            max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
            max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)
            top_level_items_bounds.append({"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y})

        # 获取所有离群点的边界
        for index in outlier_indices:
            top_level_items_bounds.append(layers[index]["frame"])

        if len(top_level_items_bounds) > 1:
            centers_x = [b['x'] + b['width'] / 2 for b in top_level_items_bounds]
            centers_y = [b['y'] + b['height'] / 2 for b in top_level_items_bounds]
            try:
                variance_x = variance(centers_x)
                variance_y = variance(centers_y)
                if variance_x > variance_y:
                    container_direction = constants.LAYOUT_DIR_ROW
            except statistics.StatisticsError:
                # 如果只有一个元素或方差无法计算，则保持默认值
                pass
        
        container_layout = {
            "type": constants.LAYOUT_FLEX,
            "direction": container_direction
        }

        final_analysis = {
            "container_layout": container_layout,
            "layout_groups": resolved_groups,
            "outlier_indices": outlier_indices
        }

        return final_analysis

    def _validate_groups_geometry(self, groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对一组候选组进行几何合理性校验，过滤掉不符合基本对齐规则的组。
        :param groups: 从某个引擎（如 LLM）返回的候选组列表。
        :param layers: 原始图层列表，用于获取坐标。
        :return: 只包含通过了校验的组的新列表。
        """
        validated_groups = []
        if not groups:
            return []
            
        for group in groups:
            group_indices = group.get("children_indices", [])
            group_layers = [layers[i] for i in group_indices if i < len(layers)]

            if len(group_layers) < 2:
                continue

            is_geometrically_valid = True
            direction = group.get("direction")
            try:
                if direction == constants.LAYOUT_DIR_ROW:
                    y_coords = [l["frame"]["y"] for l in group_layers]
                    if statistics.stdev(y_coords) >= config.LAYOUT_Y_THRESHOLD:
                        is_geometrically_valid = False
                        logger.warning(f"一个 ROW 组因 Y 坐标方差过大而被拒绝。索引: {group_indices}")
                elif direction == constants.LAYOUT_DIR_COLUMN:
                    x_coords = [l["frame"]["x"] for l in group_layers]
                    if statistics.stdev(x_coords) >= config.LAYOUT_X_THRESHOLD:
                        is_geometrically_valid = False
                        logger.warning(f"一个 COLUMN 组因 X 坐标方差过大而被拒绝。索引: {group_indices}")
            except statistics.StatisticsError:
                is_geometrically_valid = False
                logger.warning(f"计算建议组的标准差时出错，已拒绝。索引: {group_indices}")

            if is_geometrically_valid:
                validated_groups.append(group)
        
        return validated_groups

    def _analyze_with_rules(self, layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于几何规则分析布局，找出所有潜在的（包括重叠的）组。
        此函数取代了旧的贪心算法，作为候选生成引擎。
        """
        if not layers or len(layers) < 2:
            return []

        num_layers = len(layers)
        all_groups = []

        # 识别所有垂直或水平对齐的图层集合
        # 查找列
        for i in range(num_layers):
            current_col_indices = {i}
            for j in range(num_layers):
                if i == j:
                    continue
                # 检查与当前列的第一个元素的对齐情况
                if abs(layers[j]['frame']['x'] - layers[i]['frame']['x']) < config.LAYOUT_X_THRESHOLD:
                    current_col_indices.add(j)
            if len(current_col_indices) > 1:
                all_groups.append({
                    "type": constants.LAYOUT_FLEX,
                    "direction": constants.LAYOUT_DIR_COLUMN,
                    "children_indices": sorted(list(current_col_indices))
                })

        # 查找行
        for i in range(num_layers):
            current_row_indices = {i}
            for j in range(num_layers):
                if i == j:
                    continue
                # 检查与当前行的第一个元素的对齐情况
                if abs(layers[j]['frame']['y'] - layers[i]['frame']['y']) < config.LAYOUT_Y_THRESHOLD:
                    current_row_indices.add(j)
            if len(current_row_indices) > 1:
                all_groups.append({
                    "type": constants.LAYOUT_FLEX,
                    "direction": constants.LAYOUT_DIR_ROW,
                    "children_indices": sorted(list(current_row_indices))
                })

        # 对找到的组进行去重和最终验证
        final_groups = []
        seen_groups = set()
        for group in all_groups:
            # 使用 frozenset 作为键来确保唯一性
            group_key = (group['direction'], frozenset(group['children_indices']))
            if group_key not in seen_groups:
                seen_groups.add(group_key)
                group_layers = [layers[i] for i in group["children_indices"]]

                # 对整个组的对齐情况进行最终验证
                try:
                    if group['direction'] == constants.LAYOUT_DIR_COLUMN:
                        coords = [l['frame']['x'] for l in group_layers]
                        if statistics.stdev(coords) >= config.LAYOUT_X_THRESHOLD:
                            continue
                    else:  # ROW
                        coords = [l['frame']['y'] for l in group_layers]
                        if statistics.stdev(coords) >= config.LAYOUT_Y_THRESHOLD:
                            continue
                except statistics.StatisticsError:
                    continue  # 如果标准差计算失败（例如只有一个元素），则跳过

                # 计算组的布局属性（如 gap）
                self._calculate_properties(group_info=group, group_layers=group_layers)
                final_groups.append(group)

        return final_groups

    def _analyze_with_llm(self, layers: List[Dict[str, Any]]):
        """
        使用混合方法分析布局：LLM 负责分组，Python 负责计算。
        作为语义分析引擎，与规则分析并行工作。
        """
        logger.info(f"正在为 {len(layers)} 个图层执行 LLM 布局分组...")
        # 简化图层信息，减少 prompt 的 token 数量
        simplified_layers = [
            {"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")}
            for l in layers
        ]

        prompt_template = self._load_prompt("layout_grouping_prompt")
        if not prompt_template:
            return None

        simplified_layers_json = json.dumps(simplified_layers, indent=2)
        prompt = f"{prompt_template}\nInput Layers:\n```json\n{simplified_layers_json}\n```"

        try:
            response = self._call_llm(prompt)
            layout_analysis = json.loads(response)

            # 对 LLM 返回的每个组，使用 Python 计算其精确的布局属性
            for group in layout_analysis.get("layout_groups", []):
                group_indices = group.get("children_indices", [])
                group_layers = [layers[i] for i in group_indices]
                self._calculate_properties(group, group_layers)

            # TODO: 这个后处理逻辑可能需要重新评估或移除，因为它可能与新的冲突解决机制重叠。
            def post_process_groups(layout_analysis):
                groups = layout_analysis.get("layout_groups", [])
                outliers = layout_analysis.get("outlier_indices", [])
                
                potential_row = []
                for i in range(len(layers)):
                    if i in outliers or any(i in g["children_indices"] for g in groups):
                        continue
                    potential_row.append(i)
                
                if len(potential_row) >= 3:
                    y_values = [layers[i]["frame"]["y"] for i in potential_row]
                    widths = [layers[i]["frame"]["width"] for i in potential_row]
                    heights = [layers[i]["frame"]["height"] for i in potential_row]
                    names = [layers[i].get("name", "") for i in potential_row]
                    
                    if max(y_values) - min(y_values) < 5:
                        if statistics.stdev(widths) < 5 and statistics.stdev(heights) < 5:
                            common_keywords = set.intersection(*[set(n.split()) for n in names if n])
                            if len(common_keywords) > 0 or any("备份" in n for n in names):
                                groups.append({
                                    "type": "flex",
                                    "direction": "row",
                                    "children_indices": sorted(potential_row)
                                })
                                outliers = [o for o in outliers if o not in potential_row]
                
                return {
                    "layout_groups": groups,
                    "outlier_indices": outliers
                }
            
            layout_analysis = post_process_groups(layout_analysis)

            logger.info(f"LLM 分析成功（未校验）: {layout_analysis}")
            return layout_analysis
        except Exception as e:
            logger.error(f"LLM 分析失败: {e}")
            return None

    def _resolve_conflicts(self, groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解决候选组之间的冲突，选择对齐更强（方差更小）或更大的组。
        这是混合分析策略的核心仲裁者。
        """
        resolved_groups = []
        seen_indices = set()

        # 按组成员数量降序排序，优先处理更大的组
        for group in sorted(groups, key=lambda g: len(g['children_indices']), reverse=True):
            indices = set(group['children_indices'])
            
            if indices.isdisjoint(seen_indices):
                resolved_groups.append(group)
                seen_indices.update(indices)
            else:
                conflicting = indices.intersection(seen_indices)
                if conflicting:
                    if group['direction'] == constants.LAYOUT_DIR_ROW:
                        y_coords = [layers[i]["frame"]["y"] for i in group['children_indices']]
                        strength = variance(y_coords) if len(y_coords) > 1 else float('inf')
                    else:  # COLUMN
                        x_coords = [layers[i]["frame"]["x"] for i in group['children_indices']]
                        strength = variance(x_coords) if len(x_coords) > 1 else float('inf')
                    
                    if strength < 25:
                        resolved_groups = [g for g in resolved_groups if not set(g['children_indices']).intersection(conflicting)]
                        resolved_groups.append(group)
                        seen_indices = set().union(*(set(g['children_indices']) for g in resolved_groups))
        
        return resolved_groups

    def _analyze_spacing(self, group_layers: List[Dict[str, Any]], direction: str) -> Dict[str, Any]:
        """
        分析一个组内的间距，并决定使用 gap 还是独立的 margin。
        :param group_layers: 已排序的图层组。
        :param direction: 布局方向 ('row' or 'column')。
        :return: 包含间距策略的字典。
        """
        spacing_info = {}
        if direction == constants.LAYOUT_DIR_COLUMN:
            gaps = [
                group_layers[i + 1]["frame"]["y"] - (group_layers[i]["frame"]["y"] + group_layers[i]["frame"]["height"])
                for i in range(len(group_layers) - 1)
            ]
        else:  # LAYOUT_DIR_ROW
            gaps = [
                group_layers[i + 1]["frame"]["x"] - (group_layers[i]["frame"]["x"] + group_layers[i]["frame"]["width"])
                for i in range(len(group_layers) - 1)
            ]

        if not gaps:
            return {"gap": 0}

        # 如果只有一个间距（即只有两个元素），则间距必然是一致的
        if len(gaps) == 1:
            spacing_info["gap"] = round(gaps[0])
            return spacing_info

        # 如果间距的标准差小于一个阈值（例如2px），则认为间距是一致的
        if statistics.stdev(gaps) < 2:
            spacing_info["gap"] = round(statistics.mean(gaps))
        else:
            # 否则，我们记录下每个独立的间距值，以便渲染器进行像素级还原
            spacing_info["spacings"] = [round(g) for g in gaps]

        return spacing_info

    def _analyze_alignment(self, group_layers: List[Dict[str, Any]], group_bounds: Dict[str, float], direction: str) -> Dict[str, str]:
        """
        分析组内元素的对齐方式。
        :param group_layers: 图层组。
        :param group_bounds: 组的边界框 (x, y, width, height)。
        :param direction: 布局方向。
        :return: 包含 justifyContent 和 alignItems 的字典。
        """
        alignment_info = {}

        # --- 分析 Align Items (交叉轴对齐) ---
        cross_axis_coords = []
        cross_axis_sizes = []
        if direction == constants.LAYOUT_DIR_ROW:
            # 对于行布局，交叉轴是垂直的
            container_size = group_bounds["height"]
            container_start = group_bounds["y"]
            for layer in group_layers:
                cross_axis_coords.append(layer["frame"]["y"])
                cross_axis_sizes.append(layer["frame"]["height"])
        else:  # COLUMN
            # 对于列布局，交叉轴是水平的
            container_size = group_bounds["width"]
            container_start = group_bounds["x"]
            for layer in group_layers:
                cross_axis_coords.append(layer["frame"]["x"])
                cross_axis_sizes.append(layer["frame"]["width"])

        # 检查是否居中对齐 (center)
        is_centered = True
        for coord, size in zip(cross_axis_coords, cross_axis_sizes):
            center_offset = (coord + size / 2) - (container_start + container_size / 2)
            if abs(center_offset) > 2:  # 允许2px的误差
                is_centered = False
                break
        if is_centered:
            alignment_info["alignItems"] = "center"

        # TODO: 在此添加对 flex-start, flex-end, stretch 的逻辑判断

        # --- 分析 Justify Content (主轴对齐) ---
        # TODO: 在此添加对 space-between, center, flex-end 的逻辑判断

        return alignment_info

    def _calculate_properties(self, group_info: Dict[str, Any], group_layers: List[Dict[str, Any]]):
        """为给定的图层组计算所有布局属性（作为协调者）。"""
        if not group_layers or len(group_layers) < 2:
            group_info.setdefault("gap", 0)
            return

        layout_type = group_info.get("type")
        direction = group_info.get("direction")

        # 对于 grid 布局，如果缺少方向，则暂时假定为列布局以计算 gap
        if layout_type == constants.LAYOUT_GRID and not direction:
            direction = constants.LAYOUT_DIR_COLUMN

        if not direction:  # 如果仍然没有方向，无法继续
            group_info.setdefault("gap", 0)
            return

        # 1. 排序图层
        if direction == constants.LAYOUT_DIR_COLUMN:
            group_layers.sort(key=lambda l: l["frame"]["y"])
        else:  # ROW
            group_layers.sort(key=lambda l: l["frame"]["x"])

        # 2. 分析间距策略 (gap vs margin)
        spacing_info = self._analyze_spacing(group_layers, direction)
        group_info.update(spacing_info)

        # 3. 计算边界框并分析对齐方式
        min_x = min(l["frame"]["x"] for l in group_layers)
        min_y = min(l["frame"]["y"] for l in group_layers)
        max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
        max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)
        group_bounds = {"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y}

        alignment_info = self._analyze_alignment(group_layers, group_bounds, direction)
        group_info.update(alignment_info)

        # 4. 设置默认值 (如果之前的分析没有提供)
        group_info.setdefault("padding", {"top": 0, "right": 0, "bottom": 0, "left": 0})
        group_info.setdefault("justifyContent", "flex-start")
        group_info.setdefault("alignItems", "flex-start")
        group_info.setdefault("position", "relative")

    def _load_prompt(self, prompt_name: str) -> str:
        """从 prompts 目录加载指定的提示模板。"""
        # 路径相对于此文件，向上到 converter/，然后向下到 parsers/sketch/prompts
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "parsers", "sketch", "prompts", f"{prompt_name}.md")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"提示文件未找到: {prompt_path}")
            return ""

    def _call_llm(self, prompt: str) -> str:
        """对 LLM 调用的封装。"""
        response = self.llm_service.chat(
            model=config.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "Output only raw JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        text = response.choices[0].message.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return text
