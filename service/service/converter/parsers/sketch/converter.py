import json
import logging
import os
import statistics
import uuid
from collections import defaultdict
from openai import OpenAI
from typing import List, Dict, Any

from . import config, constants, utils
from ..base import BaseParser
from ...service.llm_service import LLMClient

# 设置日志记录
logger = logging.getLogger(__name__)


class SketchParser(BaseParser):
    """
    将 Sketch JSON 数据解析为特定于设计的 DSL (领域特定语言)。
    该类为 Sketch 文件实现了 BaseParser 接口。
    """

    def __init__(self, source_data: dict, tokens_data: dict):
        """
        使用源数据和设计令牌 (design tokens) 初始化解析器。

        :param source_data: 从 Sketch 文件解析出的原始 JSON 数据。
        :param tokens_data: 包含颜色、字体、间距等的设计令牌数据。
        """
        super().__init__(source_data, tokens_data)
        # 用于存储 symbolID 到其语义化名称的映射
        self.symbol_map = {}
        # 用于生成报告，记录转换过程中遇到的未知令牌等问题
        self.report = defaultdict(lambda: defaultdict(list))
        # LLM 服务客户端
        self.llm_service = None
        # 记录 LLM 使用情况的统计信息
        self.llm_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        try:
            # 尝试初始化 LLM 客户端
            self.llm_service = LLMClient(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        except Exception as e:
            logger.error(f"初始化 LLM 客户端失败: {e}")
            self.llm_service = None

    @staticmethod
    def count_nodes(source_data: dict, mode: str = "all") -> int:
        """递归计算 Sketch 数据中的节点数量。

        :param source_data: 已解析的 Sketch 数据。
        :param mode: 'all' 统计所有节点；'hidden' 仅统计不可见节点。
        :return: 节点总数。
        """

        if mode not in {"all", "hidden"}:
            raise ValueError("mode 参数必须是 'all' 或 'hidden'")

        def _count_recursive(node):
            # 如果是列表，则递归计算列表中每个元素的节点数
            if isinstance(node, list):
                return sum(_count_recursive(item) for item in node)

            # 如果不是字典，则不是一个有效的节点
            if not isinstance(node, dict):
                return 0

            is_visible = node.get("isVisible", True)
            count_this_node = 0
            if mode == "all":
                count_this_node = 1
            elif mode == "hidden" and not is_visible:
                count_this_node = 1

            children_count = 0
            # 如果节点不是导出项且包含子图层，则递归计算子图层的节点数
            if not utils.is_export(node) and isinstance(node.get("layers"), list):
                children_count = _count_recursive(node.get("layers"))

            return count_this_node + children_count

        return _count_recursive(source_data)

    def run(self, progress_callback=None) -> tuple:
        """
        执行完整的转换流程，从 Sketch JSON 到 DSL。
        
        :param progress_callback: 一个可选的回调函数，用于报告转换进度。
        :return: 一个元组，包含 DSL 输出和元数据。
        """
        logger.info("--- Sketch-to-DSL 转换器启动 ---")
        self.progress_callback = progress_callback

        # 步骤 1: 预处理 Symbols，建立 symbolID -> name 的映射
        self._preprocess_symbols()
        
        # 步骤 2: 找到要处理的主要画板或图层组
        target_layer = self._find_main_artboard()
        if not target_layer:
            logger.error("未找到合适的画板或图层组进行处理。")
            return {}, {}

        logger.info("开始转换...")
        # 步骤 3: 从目标图层开始，递归遍历并生成 DSL
        dsl_output = self._traverse_layer(target_layer)
        logger.info("转换过程完成。")

        # 如果使用了 LLM，记录其 token 使用量
        if self.llm_service:
            self.llm_usage = self.llm_service.usage

        # 准备包含报告和 LLM 使用情况的元数据
        metadata = {
            "token_report": self.report,
            "llm_usage": self.llm_usage,
        }

        return dsl_output, metadata

    def _preprocess_symbols(self):
        """
        构建一个从 symbolID 到其语义化名称的映射。
        这对于解析 Symbol 实例至关重要，因为它允许我们获取组件的原始名称。
        """
        pages = self.source_data.get("layers", [self.source_data])
        for page in pages:
            if "layers" not in page:
                continue
            for artboard in page.get("layers", []):
                # 遍历画板或 Symbol Master
                if artboard.get("_class") in [
                    constants.LAYER_ARTBOARD,
                    constants.LAYER_SYMBOL_MASTER,
                ]:
                    for item in artboard.get("layers", []):
                        # 找到 Symbol Master 定义并存储其 ID 和名称
                        if item.get("_class") == constants.LAYER_SYMBOL_MASTER:
                            self.symbol_map[item.get("symbolID")] = item.get("name")
        logger.info(f"符号预处理完成。找到 {len(self.symbol_map)} 个符号。")

    def _find_main_artboard(self):
        """
        找到第一个可见的画板或顶层组作为转换的起点。
        通常，一个 Sketch 文件只包含一个主要的设计内容。
        """
        if self.source_data.get("_class") in [
            constants.LAYER_PAGE,
            constants.LAYER_ARTBOARD,
            constants.LAYER_GROUP,
        ]:
            logger.info(
                f"找到转换起点: '{self.source_data.get('name')}' ({self.source_data.get('_class')})"
            )
            return self.source_data
        return None

    def _map_styles_to_tokens(self, layer):
        """
        将图层的样式属性映射到设计令牌 (Design Tokens)。
        如果找不到对应的令牌，则直接使用原始样式值，并记录在报告中。
        """
        dsl_style = {}
        style = layer.get("style", {})
        layer_name = layer.get("name", "Unnamed")

        # 透明度
        opacity = style.get("contextSettings", {}).get("opacity", 1.0)
        if opacity < 1.0:
            dsl_style["opacity"] = opacity

        # 背景色 (Fills)
        if (fills := style.get("fills")) and fills and fills[0].get("isEnabled"):
            hex_color = utils.convert_color_to_hex(fills[0].get("color"))
            if hex_color:
                token = self.tokens_data.get("colors", {}).get(hex_color)
                if token:
                    dsl_style["backgroundColor"] = token
                else:
                    # 未找到颜色令牌，记录并使用原始值
                    logger.warning(
                        f"未知的背景色: {hex_color} (图层: '{layer_name}')"
                    )
                    dsl_style["backgroundColor"] = hex_color
                    self.report["unknown_colors"][hex_color].append(layer_name)

        # 文本样式
        if text_style := style.get("textStyle"):
            self._map_text_style(text_style, dsl_style, layer_name)

        # 边框
        if (
            (borders := style.get("borders"))
            and borders
            and borders[0].get("isEnabled")
        ):
            self._map_border_style(borders[0], dsl_style, layer_name)

        # 圆角
        if (radius := layer.get("fixedRadius")) and radius > 0:
            radius_key = str(int(radius))
            token = self.tokens_data.get("radii", {}).get(radius_key)
            dsl_style["borderRadius"] = token if token else f"{radius_key}px"

        # 阴影 (简化处理)
        if (
            (shadows := style.get("shadows"))
            and shadows
            and shadows[0].get("isEnabled")
        ):
            dsl_style["shadow"] = "default"  # 简化处理，未来可以令牌化

        return dsl_style

    def _map_text_style(self, text_style, dsl_style, layer_name):
        """辅助函数，用于映射文本颜色和字体。"""
        attrs = text_style.get("encodedAttributes", {})
        # 文本颜色
        if color_attr := attrs.get("MSAttributedStringColorAttribute"):
            hex_color = utils.convert_color_to_hex(color_attr)
            if hex_color:
                token = self.tokens_data.get("textColors", {}).get(hex_color)
                if token:
                    dsl_style["textColor"] = token
                else:
                    logger.warning(
                        f"未知的文本颜色: {hex_color} (图层: '{layer_name}')"
                    )
                    dsl_style["textColor"] = hex_color
                    self.report["unknown_textColors"][hex_color].append(layer_name)
        # 字体
        font_attrs = attrs.get("MSAttributedStringFontAttribute", {}).get(
            "attributes", {}
        )
        font_name, font_size = font_attrs.get("name"), font_attrs.get("size")
        if font_name and font_size:
            font_key = f"{font_name}-{int(font_size)}"
            token = self.tokens_data.get("fonts", {}).get(font_key)
            if token:
                dsl_style["font"] = token
            else:
                logger.warning(f"未知的字体: '{font_key}' (图层: '{layer_name}')")
                self.report["unknown_fonts"][font_key].append(layer_name)

    def _map_border_style(self, border, dsl_style, layer_name):
        """辅助函数，用于映射边框宽度和颜色。"""
        dsl_style["borderWidth"] = f"{border.get('thickness', 1)}px"
        if hex_color := utils.convert_color_to_hex(border.get("color")):
            token = self.tokens_data.get("borderColors", {}).get(hex_color)
            if token:
                dsl_style["borderColor"] = token
            else:
                logger.warning(
                    f"未知的边框颜色: {hex_color} (图层: '{layer_name}')"
                )
                dsl_style["borderColor"] = hex_color
                self.report["unknown_borderColors"][hex_color].append(layer_name)

    def _sort_layers(self, layers, layout_info):
        """
        根据布局信息（行或列），按视觉坐标对图层列表进行排序。
        这确保了在生成代码时，DOM 元素的顺序与视觉顺序一致。
        """
        direction = layout_info.get("direction")
        layout_type = layout_info.get("type")

        # 对于行或网格布局，主要按从左到右，再从上到下排序
        if direction == constants.LAYOUT_DIR_ROW or layout_type == constants.LAYOUT_GRID:
            layers.sort(key=lambda l: (l["frame"]["x"], l["frame"]["y"]))
        # 对于列布局，主要按从上到下，再从左到右排序
        elif direction == constants.LAYOUT_DIR_COLUMN:
            layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))
        # 默认回退排序（例如布局未知时），按从上到下排序
        else:
            layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))
        return layers

    def _traverse_layer(self, layer, parent_layout_type=constants.LAYOUT_ABSOLUTE):
        """
        递归遍历图层树，构建 DSL 结构。
        这是解析器的核心，负责节点类型判断、样式映射和布局分析。
        """
        if not layer or not layer.get("isVisible", True):
            return None

        layer_class = layer.get("_class")
        frame = layer.get("frame", {})
        node = {}

        # 步骤 1: 确定节点类型和内容
        if layer_class == constants.LAYER_SYMBOL_INSTANCE:
            symbol_id = layer.get("symbolID")
            semantic_name = self.symbol_map.get(symbol_id, layer.get("name"))
            parsed_name = utils.parse_semantic_name(semantic_name)
            node["type"] = parsed_name.get("type", constants.NODE_UNKNOWN_COMPONENT)
            node["variant"] = parsed_name.get("variant")
            if overrides := layer.get("overrideValues"):
                for override in overrides:
                    if "stringValue" in override and override["stringValue"]:
                        node["content"] = {"text": override["stringValue"]}
                        break
        elif layer_class == constants.LAYER_TEXT:
            node["type"] = constants.NODE_TEXT
            node["content"] = {"text": layer.get("stringValue")}
        elif layer_class == constants.LAYER_GROUP:
            node["type"] = constants.NODE_GROUP
        elif layer_class == constants.LAYER_RECTANGLE:
            node["type"] = constants.NODE_RECTANGLE
        elif layer_class == constants.LAYER_OVAL:
            node["type"] = constants.NODE_OVAL
        elif layer_class == constants.LAYER_PAGE:
            node["type"] = constants.NODE_PAGE
        elif layer_class == constants.LAYER_ARTBOARD:
            node["type"] = constants.NODE_ARTBOARD
        elif layer_class == constants.LAYER_SHAPE_PATH:
            node["type"] = constants.NODE_SHAPE_PATH
        elif layer_class == constants.LAYER_SHAPE_GROUP:
            node["type"] = constants.NODE_SHAPE_GROUP
        elif layer_class == constants.LAYER_BITMAP:
            node["type"] = constants.NODE_BITMAP
        elif layer_class == constants.LAYER_TRIANGLE:
            node["type"] = constants.NODE_TRIANGLE
        else:
            logger.info(
                f"忽略未知图层类型: {layer_class} (名称: '{layer.get('name')}')"
            )
            node["type"] = constants.NODE_UNKNOWN_COMPONENT
            node["class"] = layer_class

        node["name"] = layer.get("name")
        node["do_objectID"] = layer.get("do_objectID")

        # 步骤 2: 映射样式和尺寸
        style = self._map_styles_to_tokens(layer)
        style["width"] = frame.get("width")
        style["height"] = frame.get("height")
        node["style"] = style

        if self.progress_callback:
            self.progress_callback()

        # 如果图层被标记为可导出项，则将其视为图片节点，并终止递归
        if utils.is_export(layer):
            node["exportOptions"] = layer.get("exportOptions")
            node["type"] = constants.NODE_IMAGE
            return node

        # 步骤 3: 处理布局和子节点 (核心逻辑)
        layout = {}
        children_nodes = []
        is_root_page = node.get("type") == constants.NODE_PAGE and parent_layout_type == constants.LAYOUT_ABSOLUTE
        
        if layer.get("layers") and len(layer.get("layers")) > 0:
            child_layers = layer["layers"]
            if is_root_page:
                # 如果是根页面，其子节点（画板）通常是绝对定位的
                for child in child_layers:
                    if child_node := self._traverse_layer(
                        child, parent_layout_type=constants.LAYOUT_ABSOLUTE
                    ):
                        children_nodes.append(child_node)
            else:
                # --- 混合布局分析策略 ---
                # 1. 从几何规则引擎获取所有可能的候选组
                rule_based_groups = self._analyze_layout_with_rules(child_layers)
                logger.info(f"规则分析找到 {len(rule_based_groups)} 个潜在组。")

                # 2. 从 LLM 获取语义候选组
                llm_analysis = (
                    self._analyze_layout_with_llm(child_layers, layer.get("do_objectID"))
                    if self.llm_service
                    else None
                )
                llm_groups = llm_analysis.get("layout_groups", []) if llm_analysis else []
                logger.info(f"LLM 分析找到 {len(llm_groups)} 个潜在组。")

                # 3. 合并所有候选组并通过冲突解决机制进行仲裁
                all_candidate_groups = rule_based_groups + llm_groups

                if all_candidate_groups:
                    logger.info(f"在 {len(all_candidate_groups)} 个总候选组中解决冲突。")
                    resolved_groups = self._resolve_group_conflicts(all_candidate_groups, child_layers)
                    logger.info(f"冲突解决后找到 {len(resolved_groups)} 个最终组。")

                    # 确定未被任何组包含的离群点
                    processed_indices = set()
                    for group in resolved_groups:
                        processed_indices.update(group['children_indices'])
                    
                    all_indices = set(range(len(child_layers)))
                    outlier_indices = sorted(list(all_indices - processed_indices))

                    final_analysis = {
                        "layout_groups": resolved_groups,
                        "outlier_indices": outlier_indices
                    }

                    # 使用最终分析结果处理子节点
                    layout["type"] = constants.LAYOUT_ABSOLUTE
                    children_nodes = self._process_layout_analysis(
                        final_analysis, child_layers
                    )
                else:  # 所有方法都未能找到任何组
                    logger.info("所有分析方法均未找到任何组，将作为绝对定位处理。")
                    layout["type"] = constants.LAYOUT_ABSOLUTE
                    for child in child_layers:
                        if child_node := self._traverse_layer(
                            child, parent_layout_type=constants.LAYOUT_ABSOLUTE
                        ):
                            children_nodes.append(child_node)
                            
        # 如果父容器是绝对布局，则当前节点也需要绝对定位的坐标
        if parent_layout_type == constants.LAYOUT_ABSOLUTE and not is_root_page:
            layout["position"] = constants.LAYOUT_ABSOLUTE
            layout["top"] = frame.get("y")
            layout["left"] = frame.get("x")

        node["layout"] = layout
        node["children"] = children_nodes
        return node

    def _process_layout_analysis(self, layout_analysis, all_child_layers):
        """
        根据最终的布局分析结果（已解决冲突），创建虚拟组并处理离群点。
        """
        children_nodes = []
        num_children = len(all_child_layers)
        processed_indices = set()

        # 为每个最终确定的布局组创建一个虚拟组节点
        for group_info in layout_analysis.get("layout_groups", []):
            group_indices = [
                idx
                for idx in group_info.get("children_indices", [])
                if idx < num_children
            ]
            if not group_indices:
                continue

            group_layers = [all_child_layers[j] for j in group_indices]
            
            # 对虚拟组内的图层进行排序，以保证 DOM 顺序正确
            self._sort_layers(group_layers, group_info)

            processed_indices.update(group_indices)

            # 计算虚拟组的边界框
            min_x = min(l["frame"]["x"] for l in group_layers)
            min_y = min(l["frame"]["y"] for l in group_layers)
            max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
            max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)

            # 虚拟组本身在父容器中是绝对定位的
            virtual_group_layout = group_info.copy()
            virtual_group_layout.update(
                {"position": constants.LAYOUT_ABSOLUTE, "top": min_y, "left": min_x}
            )

            # 递归处理虚拟组的子节点，并调整其坐标为相对于虚拟组
            virtual_group_children = []
            for child_layer in group_layers:
                adjusted_layer = child_layer.copy()
                adjusted_layer["frame"] = adjusted_layer["frame"].copy()
                adjusted_layer["frame"]["x"] -= min_x
                adjusted_layer["frame"]["y"] -= min_y

                if child_node := self._traverse_layer(
                    adjusted_layer, parent_layout_type=group_info.get("type")
                ):
                    virtual_group_children.append(child_node)

            # 创建虚拟组节点
            virtual_group = {
                "type": constants.NODE_GROUP,
                "group_identifier": f"Virtual Group - {group_info.get('type')}",
                "do_objectID": str(uuid.uuid4()),
                "style": {"width": max_x - min_x, "height": max_y - min_y},
                "layout": virtual_group_layout,
                "children": virtual_group_children,
            }
            children_nodes.append(virtual_group)

        # 处理离群点，它们被视为父容器中的绝对定位元素
        outlier_indices = [
            idx
            for idx in layout_analysis.get("outlier_indices", [])
            if idx < num_children
        ]
        for outlier_index in outlier_indices:
            if outlier_index in processed_indices:
                continue
            if child_node := self._traverse_layer(
                all_child_layers[outlier_index],
                parent_layout_type=constants.LAYOUT_ABSOLUTE,
            ):
                children_nodes.append(child_node)

        return children_nodes

    def _analyze_layout_with_rules(self, layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                self._calculate_layout_properties(group_info=group, group_layers=group_layers)
                final_groups.append(group)

        return final_groups

    def _load_prompt(self, prompt_name: str) -> str:
        """从 prompts 目录加载指定的提示模板。"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompts", f"{prompt_name}.md")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"提示文件未找到: {prompt_path}")
            return ""

    def _analyze_layout_with_llm(self, layers, do_objectID):
        """
        使用混合方法分析布局：LLM 负责分组，Python 负责计算。
        作为语义分析引擎，与规则分析并行工作。
        """
        if not self.llm_service:
            logger.warning("LLM 客户端不可用，跳过 LLM 布局分析。")
            return None

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
                self._calculate_layout_properties(group, group_layers)

            # TODO: 这个后处理逻辑可能需要重新评估或移除，因为它可能与新的冲突解决机制重叠。
            # 新增：后处理以修复水平分组 bug，考虑相似性
            def post_process_groups(layout_analysis):
                groups = layout_analysis.get("layout_groups", [])
                outliers = layout_analysis.get("outlier_indices", [])
                
                # 检测潜在水平行候选
                potential_row = []
                for i in range(len(layers)):
                    if i in outliers or any(i in g["children_indices"] for g in groups):
                        continue
                    potential_row.append(i)
                
                if len(potential_row) >= 3:  # 至少3个元素视为潜在行
                    y_values = [layers[i]["frame"]["y"] for i in potential_row]
                    widths = [layers[i]["frame"]["width"] for i in potential_row]
                    heights = [layers[i]["frame"]["height"] for i in potential_row]
                    names = [layers[i].get("name", "") for i in potential_row]
                    
                    # 检查 y 相近
                    if max(y_values) - min(y_values) < 5:
                        # 检查尺寸相似：标准差小
                        if statistics.stdev(widths) < 5 and statistics.stdev(heights) < 5:
                            # 检查名称相似：至少一半包含共同关键词（如 "矩形" 或 "备份"）
                            common_keywords = set.intersection(*[set(n.split()) for n in names if n])
                            if len(common_keywords) > 0 or any("备份" in n for n in names):  # 示例规则，可调整
                                groups.append({
                                    "type": "flex",
                                    "direction": "row",
                                    "children_indices": sorted(potential_row)
                                })
                                # 从 outliers 或其他组移除
                                outliers = [o for o in outliers if o not in potential_row]
                
                return {
                    "layout_groups": groups,
                    "outlier_indices": outliers
                }
            
            # 调用后处理
            layout_analysis = post_process_groups(layout_analysis)

            logger.info(f"混合 LLM 分析成功: {layout_analysis}")
            return layout_analysis
        except Exception as e:
            logger.error(f"混合 LLM 分析失败: {e}")
            # LLM 分析失败时，返回空结果，让冲突解决机制处理
            return None

    def _calculate_layout_properties(self, group_info, group_layers):
        """为给定的图层组计算 gap, padding 和对齐方式。"""
        if not group_layers:
            return

        layout_type = group_info.get("type")
        direction = group_info.get("direction")

        if layout_type == constants.LAYOUT_FLEX:
            if direction == constants.LAYOUT_DIR_COLUMN:
                group_layers.sort(key=lambda l: l["frame"]["y"])
                # 计算垂直方向的 gap
                gaps = [
                    group_layers[i + 1]["frame"]["y"] - (group_layers[i]["frame"]["y"] + group_layers[i]["frame"]["height"])
                    for i in range(len(group_layers) - 1)
                ]
                group_info["gap"] = round(statistics.mean(gaps)) if gaps else 0
            elif direction == constants.LAYOUT_DIR_ROW:
                group_layers.sort(key=lambda l: l["frame"]["x"])
                # 计算水平方向的 gap
                gaps = [
                    group_layers[i + 1]["frame"]["x"] - (group_layers[i]["frame"]["x"] + group_layers[i]["frame"]["width"])
                    for i in range(len(group_layers) - 1)
                ]
                group_info["gap"] = round(statistics.mean(gaps)) if gaps else 0

        # 设置其他 flex 属性的默认值
        group_info.setdefault("padding", {"top": 0, "right": 0, "bottom": 0, "left": 0})
        group_info.setdefault("justifyContent", "flex-start")
        group_info.setdefault("alignItems", "flex-start")
        group_info.setdefault("position", "relative")


    def _call_llm(self, prompt):
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
        # 从 markdown 代码块中提取 JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return text

    def _resolve_group_conflicts(self, groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解决候选组之间的冲突，选择对齐更强（方差更小）或更大的组。
        这是混合分析策略的核心仲裁者。
        """
        from statistics import variance

        resolved_groups = []
        seen_indices = set()

        # 按组成员数量降序排序，优先处理更大的组
        for group in sorted(groups, key=lambda g: len(g['children_indices']), reverse=True):
            indices = set(group['children_indices'])
            
            # 如果当前组与已选中的组没有冲突，直接添加
            if indices.isdisjoint(seen_indices):
                resolved_groups.append(group)
                seen_indices.update(indices)
            else:
                # 如果存在冲突
                conflicting = indices.intersection(seen_indices)
                if conflicting:
                    # 计算当前组的“对齐强度”（方差越小，对齐越强）
                    if group['direction'] == constants.LAYOUT_DIR_ROW:
                        y_coords = [layers[i]["frame"]["y"] for i in group['children_indices']]
                        strength = variance(y_coords) if len(y_coords) > 1 else float('inf')
                    else: # COLUMN
                        x_coords = [layers[i]["frame"]["x"] for i in group['children_indices']]
                        strength = variance(x_coords) if len(x_coords) > 1 else float('inf')
                    
                    # 如果当前组的对齐强度足够高（方差足够小），则它有权“覆盖”之前的选择
                    if strength < 25: # 阈值可以调整
                        # 从已选中的组中，移除所有与当前组有冲突的旧组
                        resolved_groups = [g for g in resolved_groups if not set(g['children_indices']).intersection(conflicting)]
                        # 添加当前这个更强的组
                        resolved_groups.append(group)
                        # 更新已处理的索引集合
                        seen_indices = set().union(*(set(g['children_indices']) for g in resolved_groups))
        
        return resolved_groups
