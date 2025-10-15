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
from ...layout_strategies.llm_only_strategy import LLMOnlyStrategy

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

        # 初始化布局策略
        self.layout_strategy = LLMOnlyStrategy(self.llm_service)

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

        # 步骤 4: 后处理 - 修正页面级组件的定位 (修复 SKETCH-26)
        # 根据业务规则，作为独立页面的顶层画板(Artboard)不应使用绝对定位。
        # 此处遍历 DSL 根节点的直接子节点（即页面级组件），并移除任何可能被错误添加的绝对定位。
        if dsl_output and dsl_output.get("children"):
            for page_component_node in dsl_output["children"]:
                layout = page_component_node.get("layout", {})
                if layout.get("position") == constants.LAYOUT_ABSOLUTE:
                    logger.debug(f"为页面组件 '{page_component_node.get('name')}' 移除绝对定位。")
                    del layout["position"]
                    if "top" in layout:
                        del layout["top"]
                    if "left" in layout:
                        del layout["left"]

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
        # 新增日志：打印正在分析的节点信息
        if layer:
            node_id = layer.get("do_objectID", "Unknown")
            node_name = layer.get("name", "Unnamed")
            logger.info(f"Analyzing layout for node: ID={node_id}, Name={node_name}")

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
        
        if layer.get("layers") and len(layer.get("layers")) > 0:
            child_layers = layer["layers"]

            # 如果是顶层页面节点，其子节点（画板）不应被包裹在虚拟组中
            if layer_class == constants.LAYER_PAGE:
                # 分析其子节点（画板）的整体布局
                final_analysis = self.layout_strategy.analyze(layer)
                # 将容器布局应用到页面节点自身
                layout.update(final_analysis.get("container_layout", {}))
                
                # 直接递归遍历子节点（画板），不创建虚拟组
                for child in child_layers:
                    if child_node := self._traverse_layer(
                        child, parent_layout_type=layout.get("type")
                    ):
                        children_nodes.append(child_node)
            else:
                # 对于所有其他节点，使用标准布局分析（可能会创建虚拟组）
                final_analysis = self.layout_strategy.analyze(layer)

                if final_analysis and (final_analysis.get("layout_groups") or final_analysis.get("outlier_indices")):
                    # 使用最终分析结果处理子节点
                    # 容器的布局由策略决定
                    layout.update(final_analysis.get("container_layout", {"type": constants.LAYOUT_ABSOLUTE}))
                    
                    children_nodes = self._process_layout_analysis(
                        final_analysis,
                        all_child_layers=layer["layers"],  # 用 layer["layers"]
                        parent_layout=layout
                    )
                else:  # 所有方法都未能找到任何组
                    logger.info("所有分析方法均未找到任何组，将作为绝对定位处理。")
                    layout["type"] = constants.LAYOUT_ABSOLUTE
                    for child in layer["layers"]:
                        if child_node := self._traverse_layer(
                            child, parent_layout_type=constants.LAYOUT_ABSOLUTE
                        ):
                            children_nodes.append(child_node)
                            
        # 智能选择定位方式：根据布局类型和父容器类型决定
        layout_type = layout.get("type", constants.LAYOUT_ABSOLUTE)
        
        # 对于页面级组件（PAGE 和 ARTBOARD），优先使用布局分析的结果
        if layer_class in [constants.LAYER_PAGE, constants.LAYER_ARTBOARD]:
            # 页面级组件根据布局类型智能选择定位方式
            if layout_type == constants.LAYOUT_FLEX:
                layout["position"] = "relative"  # flex 布局使用相对定位
            elif layout_type == constants.LAYOUT_GRID:
                layout["position"] = "relative"  # grid 布局使用相对定位
            else:
                # 绝对布局或未识别时，使用绝对定位
                layout["position"] = constants.LAYOUT_ABSOLUTE
                layout["top"] = frame.get("y")
                layout["left"] = frame.get("x")
        else:
            # 非页面级组件，如果父容器是绝对布局，则当前节点也需要绝对定位的坐标
            if parent_layout_type == constants.LAYOUT_ABSOLUTE:
                layout["position"] = constants.LAYOUT_ABSOLUTE
                layout["top"] = frame.get("y")
                layout["left"] = frame.get("x")
        
        node["layout"] = layout
        node["children"] = children_nodes
        return node

    def _process_layout_analysis(self, layout_analysis, all_child_layers, parent_layout: Dict[str, Any]):
        """
        根据最终的布局分析结果（已解决冲突），创建虚拟组并处理离群点。
        """
        children_nodes = []
        num_children = len(all_child_layers)
        processed_indices = set()
        parent_layout_type = parent_layout.get("type", constants.LAYOUT_ABSOLUTE)

        # 用于排序的临时列表
        sortable_children = []

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

            virtual_group_layout = group_info.copy()
            # 如果父容器是绝对布局，则虚拟组也绝对定位
            if parent_layout_type == constants.LAYOUT_ABSOLUTE:
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
            sortable_children.append({"node": virtual_group, "x": min_x, "y": min_y})

        # 处理离群点
        outlier_indices = [
            idx
            for idx in layout_analysis.get("outlier_indices", [])
            if idx < num_children
        ]
        for outlier_index in outlier_indices:
            if outlier_index in processed_indices:
                continue
            
            outlier_layer = all_child_layers[outlier_index]
            if child_node := self._traverse_layer(
                outlier_layer,
                parent_layout_type=parent_layout_type,
            ):
                sortable_children.append({"node": child_node, "x": outlier_layer["frame"]["x"], "y": outlier_layer["frame"]["y"]})

        # 如果父容器是流式布局，则根据其方向对子元素排序
        if parent_layout_type == constants.LAYOUT_FLEX:
            sort_key = "y" if parent_layout.get("direction") == constants.LAYOUT_DIR_COLUMN else "x"
            sortable_children.sort(key=lambda item: item[sort_key])

        children_nodes = [item["node"] for item in sortable_children]
        return children_nodes

