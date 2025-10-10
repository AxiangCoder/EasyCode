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

# Setup logging
logger = logging.getLogger(__name__)


class SketchParser(BaseParser):
    """
    Parses Sketch JSON data into a design-specific DSL.
    This class implements the BaseParser interface for Sketch files.
    """

    def __init__(self, source_data: dict, tokens_data: dict):
        """
        Initializes the parser with source data and design tokens.
        """
        super().__init__(source_data, tokens_data)
        self.symbol_map = {}
        self.report = defaultdict(lambda: defaultdict(list))
        self.llm_service = None
        self.llm_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        try:
            self.llm_service = LLMClient(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.llm_service = None

    @staticmethod
    def count_nodes(source_data: dict, mode: str = "all") -> int:
        """Counts nodes in the Sketch data.

        :param source_data: 已解析的 Sketch 数据。
        :param mode: 'all' 统计所有节点；'hidden' 仅统计不可见节点。
        """

        if mode not in {"all", "hidden"}:
            raise ValueError("mode 必须为 'all' 或 'hidden'")

        def _count_recursive(node):
            if isinstance(node, list):
                return sum(_count_recursive(item) for item in node)

            if not isinstance(node, dict):
                return 0

            is_visible = node.get("isVisible", True)
            count_this_node = 0
            if mode == "all":
                count_this_node = 1
            elif mode == "hidden" and not is_visible:
                count_this_node = 1

            children_count = 0
            if not utils.is_export(node) and isinstance(node.get("layers"), list):
                children_count = _count_recursive(node.get("layers"))

            return count_this_node + children_count

        return _count_recursive(source_data)

    def run(self, progress_callback=None) -> tuple:
        """
        Executes the full conversion pipeline.
        """
        logger.info("--- Sketch-to-DSL Converter --- ")
        self.progress_callback = progress_callback

        self._preprocess_symbols()
        target_layer = self._find_main_artboard()
        if not target_layer:
            logger.error("No suitable artboard or group found to process.")
            return {}, {}

        logger.info("Starting conversion...")
        dsl_output = self._traverse_layer(target_layer)
        logger.info("Conversion process completed.")

        if self.llm_service:
            self.llm_usage = self.llm_service.usage

        metadata = {
            "token_report": self.report,
            "llm_usage": self.llm_usage,
        }

        return dsl_output, metadata

    def _preprocess_symbols(self):
        """Builds a map from symbolID to its semantic name."""
        pages = self.source_data.get("layers", [self.source_data])
        for page in pages:
            if "layers" not in page:
                continue
            for artboard in page.get("layers", []):
                if artboard.get("_class") in [
                    constants.LAYER_ARTBOARD,
                    constants.LAYER_SYMBOL_MASTER,
                ]:
                    for item in artboard.get("layers", []):
                        if item.get("_class") == constants.LAYER_SYMBOL_MASTER:
                            self.symbol_map[item.get("symbolID")] = item.get("name")
        logger.info(f"Preprocessing complete. Found {len(self.symbol_map)} symbols.")

    def _find_main_artboard(self):
        """Finds the first visible artboard or group to process."""
        if self.source_data.get("_class") in [
            constants.LAYER_PAGE,
            constants.LAYER_ARTBOARD,
            constants.LAYER_GROUP,
        ]:
            logger.info(
                f"Found starting point: '{self.source_data.get('name')}' ({self.source_data.get('_class')})"
            )
            return self.source_data
        return None

    def _map_styles_to_tokens(self, layer):
        """Maps layer styles to design tokens and reports unknown styles."""
        dsl_style = {}
        style = layer.get("style", {})
        layer_name = layer.get("name", "Unnamed")

        # Opacity
        opacity = style.get("contextSettings", {}).get("opacity", 1.0)
        if opacity < 1.0:
            dsl_style["opacity"] = opacity

        # Background Color (Fills)
        if (fills := style.get("fills")) and fills and fills[0].get("isEnabled"):
            hex_color = utils.convert_color_to_hex(fills[0].get("color"))
            if hex_color:
                token = self.tokens_data.get("colors", {}).get(hex_color)
                if token:
                    dsl_style["backgroundColor"] = token
                else:
                    logger.warning(
                        f"Unknown background color: {hex_color} (Layer: '{layer_name}')"
                    )
                    dsl_style["backgroundColor"] = hex_color
                    self.report["unknown_colors"][hex_color].append(layer_name)

        # Text Style
        if text_style := style.get("textStyle"):
            self._map_text_style(text_style, dsl_style, layer_name)

        # Borders
        if (
            (borders := style.get("borders"))
            and borders
            and borders[0].get("isEnabled")
        ):
            self._map_border_style(borders[0], dsl_style, layer_name)

        # Corner Radius
        if (radius := layer.get("fixedRadius")) and radius > 0:
            radius_key = str(int(radius))
            token = self.tokens_data.get("radii", {}).get(radius_key)
            dsl_style["borderRadius"] = token if token else f"{radius_key}px"

        # Shadows
        if (
            (shadows := style.get("shadows"))
            and shadows
            and shadows[0].get("isEnabled")
        ):
            dsl_style["shadow"] = "default"  # Simplified, can be tokenized

        return dsl_style

    def _map_text_style(self, text_style, dsl_style, layer_name):
        """Helper to map text color and font."""
        attrs = text_style.get("encodedAttributes", {})
        # Text Color
        if color_attr := attrs.get("MSAttributedStringColorAttribute"):
            hex_color = utils.convert_color_to_hex(color_attr)
            if hex_color:
                token = self.tokens_data.get("textColors", {}).get(hex_color)
                if token:
                    dsl_style["textColor"] = token
                else:
                    logger.warning(
                        f"Unknown text color: {hex_color} (Layer: '{layer_name}')"
                    )
                    dsl_style["textColor"] = hex_color
                    self.report["unknown_textColors"][hex_color].append(layer_name)
        # Font
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
                logger.warning(f"Unknown font: '{font_key}' (Layer: '{layer_name}')")
                self.report["unknown_fonts"][font_key].append(layer_name)

    def _map_border_style(self, border, dsl_style, layer_name):
        """Helper to map border width and color."""
        dsl_style["borderWidth"] = f"{border.get('thickness', 1)}px"
        if hex_color := utils.convert_color_to_hex(border.get("color")):
            token = self.tokens_data.get("borderColors", {}).get(hex_color)
            if token:
                dsl_style["borderColor"] = token
            else:
                logger.warning(
                    f"Unknown border color: {hex_color} (Layer: '{layer_name}')"
                )
                dsl_style["borderColor"] = hex_color
                self.report["unknown_borderColors"][hex_color].append(layer_name)

    def _sort_layers(self, layers, layout_info):
        """Sorts a list of layers by visual coordinates based on layout info."""
        direction = layout_info.get("direction")
        layout_type = layout_info.get("type")

        # For rows and grids, the primary order is left-to-right, top-to-bottom.
        if direction == constants.LAYOUT_DIR_ROW or layout_type == constants.LAYOUT_GRID:
            layers.sort(key=lambda l: (l["frame"]["x"], l["frame"]["y"]))
        # For columns, the primary order is top-to-bottom, left-to-right.
        elif direction == constants.LAYOUT_DIR_COLUMN:
            layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))
        # Default fallback sort (e.g., if layout is unknown) is top-to-bottom.
        else:
            layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))
        return layers

    def _traverse_layer(self, layer, parent_layout_type=constants.LAYOUT_ABSOLUTE):
        """Recursively traverses the layer tree to build the DSL structure."""
        if not layer or not layer.get("isVisible", True):
            return None

        layer_class = layer.get("_class")
        frame = layer.get("frame", {})
        node = {}

        # 1. Determine node type and content
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
                f"Ignoring layer type: {layer_class} (Name: '{layer.get('name')}')"
            )
            node["type"] = constants.NODE_UNKNOWN_COMPONENT
            node["class"] = layer_class

        node["name"] = layer.get("name")
        node["do_objectID"] = layer.get("do_objectID")

        # 2. Map styles and dimensions
        style = self._map_styles_to_tokens(layer)
        style["width"] = frame.get("width")
        style["height"] = frame.get("height")
        node["style"] = style

        if self.progress_callback:
            self.progress_callback()

        if utils.is_export(layer):
            node["exportOptions"] = layer.get("exportOptions")
            node["type"] = constants.NODE_IMAGE
            return node

        # 3. Handle layout and children
        layout = {}
        children_nodes = []
        is_root_page = node.get("type") == constants.NODE_PAGE and parent_layout_type == constants.LAYOUT_ABSOLUTE
        if layer.get("layers") and len(layer.get("layers")) > 0:
            child_layers = layer["layers"]
            if is_root_page:
                for child in child_layers:
                    if child_node := self._traverse_layer(
                        child, parent_layout_type=constants.LAYOUT_ABSOLUTE
                    ):
                        children_nodes.append(child_node)
            else:
                # 1. Try rule-based analysis first
                layout_analysis = self._analyze_layout_with_rules(child_layers)

                # 2. If rules fail, fallback to LLM
                if not layout_analysis.get("layout_groups"):
                    logger.info("Rule-based analysis was inconclusive. Falling back to LLM.")
                    layout_analysis = (
                        self._analyze_layout_with_llm(child_layers, layer.get("do_objectID"))
                        if self.llm_service
                        else None
                    )

                # 3. Process the analysis result (from either rules or LLM)
                if layout_analysis and layout_analysis.get("layout_groups"):
                    logger.info("Processing layout analysis...")
                    layout["type"] = constants.LAYOUT_ABSOLUTE
                    children_nodes = self._process_layout_analysis(
                        layout_analysis, child_layers
                    )
                else:  # Both failed, treat as absolute
                    logger.info("All analysis failed. Treating as absolute.")
                    layout["type"] = constants.LAYOUT_ABSOLUTE
                    for child in child_layers:
                        if child_node := self._traverse_layer(
                            child, parent_layout_type=constants.LAYOUT_ABSOLUTE
                        ):
                            children_nodes.append(child_node)
                            
        if parent_layout_type == constants.LAYOUT_ABSOLUTE and not is_root_page:
            layout["position"] = constants.LAYOUT_ABSOLUTE
            layout["top"] = frame.get("y")
            layout["left"] = frame.get("x")

        node["layout"] = layout
        node["children"] = children_nodes
        return node

    def _process_layout_analysis(self, layout_analysis, all_child_layers):
        """Creates virtual groups and processes outliers based on LLM analysis."""
        children_nodes = []
        num_children = len(all_child_layers)
        processed_indices = set()

        for group_info in layout_analysis.get("layout_groups", []):
            group_indices = [
                idx
                for idx in group_info.get("children_indices", [])
                if idx < num_children
            ]
            if not group_indices:
                continue

            group_layers = [all_child_layers[j] for j in group_indices]
            
            self._sort_layers(group_layers, group_info)

            processed_indices.update(group_indices)

            min_x = min(l["frame"]["x"] for l in group_layers)
            min_y = min(l["frame"]["y"] for l in group_layers)
            max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
            max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)

            virtual_group_layout = group_info.copy()
            virtual_group_layout.update(
                {"position": constants.LAYOUT_ABSOLUTE, "top": min_y, "left": min_x}
            )

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

            virtual_group = {
                "type": constants.NODE_GROUP,
                "group_identifier": f"Virtual Group - {group_info.get('type')}",
                "do_objectID": str(uuid.uuid4()),
                "style": {"width": max_x - min_x, "height": max_y - min_y},
                "layout": virtual_group_layout,
                "children": virtual_group_children,
            }
            children_nodes.append(virtual_group)

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

    def _analyze_layout_with_rules(self, layers):
        """Analyzes layout based on geometric rules, capable of finding multiple groups."""
        if not layers or len(layers) < 2:
            return {"type": constants.LAYOUT_ABSOLUTE}

        # Create a mutable list of layers with their original indices
        indexed_layers = [{"layer": layer, "original_index": i} for i, layer in enumerate(layers)]

        layout_groups = []
        outlier_indices = []

        while len(indexed_layers) > 1:
            # --- Find Best Column ---
            best_col = []
            remaining_layers = list(indexed_layers)
            for i in range(len(remaining_layers)):
                for j in range(i + 1, len(remaining_layers)):
                    col_candidate = [remaining_layers[i], remaining_layers[j]]
                    x_coords = [l["layer"]["frame"]["x"] for l in col_candidate]
                    if statistics.stdev(x_coords) < config.LAYOUT_X_THRESHOLD:
                        # Greedily add more layers to this column
                        for k in range(len(remaining_layers)):
                            if k != i and k != j:
                                temp_candidate = col_candidate + [remaining_layers[k]]
                                temp_x_coords = [l["layer"]["frame"]["x"] for l in temp_candidate]
                                if statistics.stdev(temp_x_coords) < config.LAYOUT_X_THRESHOLD:
                                    col_candidate = temp_candidate
                        if len(col_candidate) > len(best_col):
                            best_col = col_candidate
            
            # --- Find Best Row ---
            best_row = []
            for i in range(len(remaining_layers)):
                for j in range(i + 1, len(remaining_layers)):
                    row_candidate = [remaining_layers[i], remaining_layers[j]]
                    y_coords = [l["layer"]["frame"]["y"] for l in row_candidate]
                    if statistics.stdev(y_coords) < config.LAYOUT_Y_THRESHOLD:
                        # Greedily add more layers to this row
                        for k in range(len(remaining_layers)):
                            if k != i and k != j:
                                temp_candidate = row_candidate + [remaining_layers[k]]
                                temp_y_coords = [l["layer"]["frame"]["y"] for l in temp_candidate]
                                if statistics.stdev(temp_y_coords) < config.LAYOUT_Y_THRESHOLD:
                                    row_candidate = temp_candidate
                        if len(row_candidate) > len(best_row):
                            best_row = row_candidate

            # Decide whether to form a group
            if len(best_col) > 1 and len(best_col) >= len(best_row):
                group_layers_indexed = best_col
                direction = constants.LAYOUT_DIR_COLUMN
            elif len(best_row) > 1:
                group_layers_indexed = best_row
                direction = constants.LAYOUT_DIR_ROW
            else:
                # No more groups can be formed
                break

            group_info = {"type": constants.LAYOUT_FLEX, "direction": direction}
            group_layers = [item["layer"] for item in group_layers_indexed]
            self._calculate_layout_properties(group_info, group_layers)
            group_info["children_indices"] = [item["original_index"] for item in group_layers_indexed]
            layout_groups.append(group_info)

            # Remove grouped layers from the list
            indexed_layers = [item for item in indexed_layers if item not in group_layers_indexed]

        # Add remaining as outliers
        outlier_indices.extend([item["original_index"] for item in indexed_layers])

        # 新增: 解决分组冲突
        layout_groups = self._resolve_group_conflicts(layout_groups, layers)

        if not layout_groups:
            return {"type": constants.LAYOUT_ABSOLUTE}
        
        return {"layout_groups": layout_groups, "outlier_indices": outlier_indices}

    def _load_prompt(self, prompt_name: str) -> str:
        """Loads a prompt from the prompts directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompts", f"{prompt_name}.md")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found at {prompt_path}")
            return ""

    def _analyze_layout_with_llm(self, layers, do_objectID):
        """Analyzes layout using a hybrid approach: LLM for grouping, Python for calculations."""
        if not self.llm_service:
            logger.warning("LLM client not available. Skipping LLM layout analysis.")
            return None

        logger.info(f"Performing LLM layout grouping for {len(layers)} layers...")
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

            # Python-based calculation for gap, padding, etc.
            for group in layout_analysis.get("layout_groups", []):
                group_indices = group.get("children_indices", [])
                group_layers = [layers[i] for i in group_indices]
                self._calculate_layout_properties(group, group_layers)

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

            logger.info(f"Hybrid LLM analysis successful: {layout_analysis}")
            return layout_analysis
        except Exception as e:
            logger.error(f"Hybrid LLM analysis failed: {e}")
            logger.warning("Falling back to rule-based layout analysis.")
            return self._analyze_layout_with_rules(layers)

    def _calculate_layout_properties(self, group_info, group_layers):
        """Calculates gap, padding, and alignment for a given group of layers."""
        if not group_layers:
            return

        layout_type = group_info.get("type")
        direction = group_info.get("direction")

        if layout_type == constants.LAYOUT_FLEX:
            if direction == constants.LAYOUT_DIR_COLUMN:
                group_layers.sort(key=lambda l: l["frame"]["y"])
                gaps = [
                    group_layers[i + 1]["frame"]["y"] - (group_layers[i]["frame"]["y"] + group_layers[i]["frame"]["height"])
                    for i in range(len(group_layers) - 1)
                ]
                group_info["gap"] = round(statistics.mean(gaps)) if gaps else 0
            elif direction == constants.LAYOUT_DIR_ROW:
                group_layers.sort(key=lambda l: l["frame"]["x"])
                gaps = [
                    group_layers[i + 1]["frame"]["x"] - (group_layers[i]["frame"]["x"] + group_layers[i]["frame"]["width"])
                    for i in range(len(group_layers) - 1)
                ]
                group_info["gap"] = round(statistics.mean(gaps)) if gaps else 0

        # Set default values for other properties
        group_info.setdefault("padding", {"top": 0, "right": 0, "bottom": 0, "left": 0})
        group_info.setdefault("justifyContent", "flex-start")
        group_info.setdefault("alignItems", "flex-start")
        group_info.setdefault("position", "relative")


    def _call_llm(self, prompt):
        """Helper for LLM calls."""
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

    def _resolve_group_conflicts(self, groups: List[Dict[str, Any]], layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolves conflicts between groups by selecting the one with stronger alignment (lower variance)."""
        from statistics import variance

        resolved_groups = []
        seen_indices = set()

        for group in sorted(groups, key=lambda g: len(g['children_indices']), reverse=True):  # 优先大组
            indices = set(group['children_indices'])
            if indices.isdisjoint(seen_indices):  # 无冲突，直接添加
                resolved_groups.append(group)
                seen_indices.update(indices)
            else:
                # 有冲突，计算对齐强度（方差越小越强）
                conflicting = indices.intersection(seen_indices)
                if conflicting:
                    # 对于 row 组，检查 Y 方差；对于 column，检查 X 方差
                    if group['direction'] == constants.LAYOUT_DIR_ROW:
                        y_coords = [layers[i]["frame"]["y"] for i in group['children_indices']]
                        strength = variance(y_coords) if len(y_coords) > 1 else float('inf')
                    else:
                        x_coords = [layers[i]["frame"]["x"] for i in group['children_indices']]
                        strength = variance(x_coords) if len(x_coords) > 1 else float('inf')
                    
                    # 如果强度（方差）小于阈值（如 25），则覆盖冲突部分
                    if strength < 25:
                        # 移除冲突组，从 resolved_groups 中删除
                        resolved_groups = [g for g in resolved_groups if not set(g['children_indices']).intersection(conflicting)]
                        resolved_groups.append(group)
                        seen_indices = set().union(*(set(g['children_indices']) for g in resolved_groups))
        
        return resolved_groups