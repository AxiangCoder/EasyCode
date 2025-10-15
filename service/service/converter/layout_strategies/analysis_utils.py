import json
import logging
import os
import statistics
from typing import List, Dict, Any

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

def validate_groups_geometry(groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                y_coords = [l["frame"]["y"] for l in group_layers]
                if statistics.stdev(y_coords) >= config.LAYOUT_Y_THRESHOLD:
                    is_geometrically_valid = False
                    logger.warning(f"一个 COLUMN 组因 Y 坐标方差过大而被拒绝。索引: {group_indices}")
        except statistics.StatisticsError:
            is_geometrically_valid = False
            logger.warning(f"计算建议组的标准差时出错，已拒绝。索引: {group_indices}")

        if is_geometrically_valid:
            validated_groups.append(group)
    
    return validated_groups

def analyze_with_rules(layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    基于几何规则分析布局，找出所有潜在的（包括重叠的）组。
    """
    if not layers or len(layers) < 2:
        return []

    num_layers = len(layers)
    all_groups = []

    for i in range(num_layers):
        current_col_indices = {i}
        for j in range(num_layers):
            if i == j:
                continue
            if abs(layers[j]['frame']['x'] - layers[i]['frame']['x']) < config.LAYOUT_X_THRESHOLD:
                current_col_indices.add(j)
        if len(current_col_indices) > 1:
            all_groups.append({
                "type": constants.LAYOUT_FLEX,
                "direction": constants.LAYOUT_DIR_COLUMN,
                "children_indices": sorted(list(current_col_indices))
            })

    for i in range(num_layers):
        current_row_indices = {i}
        for j in range(num_layers):
            if i == j:
                continue
            if abs(layers[j]['frame']['y'] - layers[i]['frame']['y']) < config.LAYOUT_Y_THRESHOLD:
                current_row_indices.add(j)
        if len(current_row_indices) > 1:
            all_groups.append({
                "type": constants.LAYOUT_FLEX,
                "direction": constants.LAYOUT_DIR_ROW,
                "children_indices": sorted(list(current_row_indices))
            })

    final_groups = []
    seen_groups = set()
    for group in all_groups:
        group_key = (group['direction'], frozenset(group['children_indices']))
        if group_key not in seen_groups:
            seen_groups.add(group_key)
            group_layers = [layers[i] for i in group["children_indices"]]

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
                continue

            calculate_properties(group_info=group, group_layers=group_layers)
            final_groups.append(group)

    return final_groups

def analyze_with_llm(layers: List[Dict[str, Any]], llm_service: Any):
    """
    使用LLM进行语义分组。
    """
    logger.info(f"正在为 {len(layers)} 个图层执行 LLM 布局分组...")
    simplified_layers = [
        {"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")}
        for l in layers
    ]

    # 新增：计算父容器 bounds
    if layers:
        parent_min_x = min(l["frame"]["x"] for l in layers)
        parent_min_y = min(l["frame"]["y"] for l in layers)
        parent_max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in layers)
        parent_max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in layers)
        parent_bounds = {
            "width": parent_max_x - parent_min_x,
            "height": parent_max_y - parent_min_y
        }
        parent_info = f"Parent container bounds: {json.dumps(parent_bounds)}\n"
    else:
        parent_info = ""

    prompt_template = _load_prompt("layout_grouping_prompt")
    if not prompt_template:
        return None

    simplified_layers_json = json.dumps(simplified_layers, indent=2)
    prompt = f"{prompt_template}\n{parent_info}Input Layers:\n```json\n{simplified_layers_json}\n```"

    logger.info(f"Prompt: {prompt}")

    try:
        response = _call_llm(prompt, llm_service)
        layout_analysis = json.loads(response)

        for group in layout_analysis.get("layout_groups", []):
            group_indices = group.get("children_indices", [])
            group_layers = [layers[i] for i in group_indices]
            calculate_properties(group, group_layers)

        logger.info(f"LLM 分析成功（未校验）: {layout_analysis}")
        return layout_analysis
    except Exception as e:
        logger.error(f"LLM 分析失败: {e}")
        return None

def resolve_conflicts(groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    解决候选组之间的冲突。
    """
    resolved_groups = []
    seen_indices = set()

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

def analyze_spacing(group_layers: List[Dict[str, Any]], direction: str) -> Dict[str, Any]:
    """
    分析组内间距。
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

    if len(gaps) == 1:
        spacing_info["gap"] = round(gaps[0])
        return spacing_info

    if statistics.stdev(gaps) < 2:
        spacing_info["gap"] = round(statistics.mean(gaps))
    else:
        spacing_info["spacings"] = [round(g) for g in gaps]

    return spacing_info

def analyze_alignment(group_layers: List[Dict[str, Any]], group_bounds: Dict[str, float], direction: str) -> Dict[str, str]:
    """
    分析组内对齐方式。
    """
    alignment_info = {}
    cross_axis_coords = []
    cross_axis_sizes = []
    if direction == constants.LAYOUT_DIR_ROW:
        container_size = group_bounds["height"]
        container_start = group_bounds["y"]
        for layer in group_layers:
            cross_axis_coords.append(layer["frame"]["y"])
            cross_axis_sizes.append(layer["frame"]["height"])
    else:  # COLUMN
        container_size = group_bounds["width"]
        container_start = group_bounds["x"]
        for layer in group_layers:
            cross_axis_coords.append(layer["frame"]["x"])
            cross_axis_sizes.append(layer["frame"]["width"])

    is_centered = True
    for coord, size in zip(cross_axis_coords, cross_axis_sizes):
        center_offset = (coord + size / 2) - (container_start + container_size / 2)
        if abs(center_offset) > 2:
            is_centered = False
            break
    if is_centered:
        alignment_info["alignItems"] = "center"

    return alignment_info

def calculate_properties(group_info: Dict[str, Any], group_layers: List[Dict[str, Any]]):
    "为给定的图层组计算所有布局属性。" 
    if not group_layers or len(group_layers) < 2:
        group_info.setdefault("gap", 0)
        return

    layout_type = group_info.get("type")
    direction = group_info.get("direction")

    if layout_type == constants.LAYOUT_GRID and not direction:
        direction = constants.LAYOUT_DIR_COLUMN

    if not direction:
        group_info.setdefault("gap", 0)
        return

    if direction == constants.LAYOUT_DIR_COLUMN:
        group_layers.sort(key=lambda l: l["frame"]["y"])
    else:
        group_layers.sort(key=lambda l: l["frame"]["x"])

    spacing_info = analyze_spacing(group_layers, direction)
    group_info.update(spacing_info)

    min_x = min(l["frame"]["x"] for l in group_layers)
    min_y = min(l["frame"]["y"] for l in group_layers)
    max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
    max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)
    group_bounds = {"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y}

    alignment_info = analyze_alignment(group_layers, group_bounds, direction)
    group_info.update(alignment_info)

    group_info.setdefault("padding", {"top": 0, "right": 0, "bottom": 0, "left": 0})
    group_info.setdefault("justifyContent", "flex-start")
    group_info.setdefault("alignItems", "flex-start")
    group_info.setdefault("position", "relative")

def _load_prompt(prompt_name: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "..", "parsers", "sketch", "prompts", f"{prompt_name}.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"提示文件未找到: {prompt_path}")
        return ""

def _call_llm(prompt: str, llm_service: Any) -> str:
    response = llm_service.chat(
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
