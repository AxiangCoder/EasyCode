import json
import logging
import statistics
from collections import defaultdict
from openai import OpenAI

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
        if not self.tokens_data:
            return {}

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
        if layer.get("layers") and len(layer.get("layers")) > 0:
            child_layers = layer["layers"]
            layout_analysis = (
                self._analyze_layout_with_llm(child_layers, layer.get("do_objectID"))
                if self.llm_service
                else None
            )
            if layout_analysis and "layout_groups" in layout_analysis:
                layout["type"] = constants.LAYOUT_ABSOLUTE
                children_nodes = self._process_llm_layout_analysis(
                    layout_analysis, child_layers
                )
            else:
                layout_info = self._analyze_layout_with_rules(child_layers)
                layout.update(layout_info)
                for child in child_layers:
                    if child_node := self._traverse_layer(
                        child, parent_layout_type=layout.get("type")
                    ):
                        children_nodes.append(child_node)

        if parent_layout_type == constants.LAYOUT_ABSOLUTE:
            layout["position"] = constants.LAYOUT_ABSOLUTE
            layout["top"] = frame.get("y")
            layout["left"] = frame.get("x")

        node["layout"] = layout
        node["children"] = children_nodes
        return node

    def _process_llm_layout_analysis(self, layout_analysis, all_child_layers):
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
                "name": f"Virtual Group - {group_info.get('type')}",
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
        """Analyzes layout based on geometric rules."""
        if not layers or len(layers) < 2:
            return {"type": constants.LAYOUT_ABSOLUTE}

        layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))

        rows = defaultdict(list)
        for layer in layers:
            found = False
            for y_key in list(rows.keys()):
                if abs(layer["frame"]["y"] - y_key) < config.LAYOUT_Y_THRESHOLD:
                    rows[y_key].append(layer)
                    found = True
                    break
            if not found:
                rows[layer["frame"]["y"]].append(layer)

        num_rows, items_per_row = len(rows), [len(r) for r in rows.values()]

        if num_rows > 1 and len(set(items_per_row)) == 1 and items_per_row[0] > 1:
            return {"type": constants.LAYOUT_GRID, "columns": items_per_row[0]}

        if num_rows == 1 and items_per_row[0] > 1:
            gaps = [
                layers[i + 1]["frame"]["x"]
                - (layers[i]["frame"]["x"] + layers[i]["frame"]["width"])
                for i in range(len(layers) - 1)
            ]
            if any(g < 0 for g in gaps):
                return {"type": constants.LAYOUT_ABSOLUTE}
            return {
                "type": constants.LAYOUT_FLEX,
                "direction": constants.LAYOUT_DIR_ROW,
                "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
            }

        if items_per_row and all(c == 1 for c in items_per_row) and num_rows > 1:
            x_coords = [l["frame"]["x"] for l in layers]
            x_std_dev = statistics.stdev(x_coords) if len(x_coords) > 1 else 0
            if x_std_dev <= config.LAYOUT_X_THRESHOLD:
                gaps = [
                    layers[i + 1]["frame"]["y"]
                    - (layers[i]["frame"]["y"] + layers[i]["frame"]["height"])
                    for i in range(len(layers) - 1)
                ]
                if any(g < 0 for g in gaps):
                    return {"type": constants.LAYOUT_ABSOLUTE}
                return {
                    "type": constants.LAYOUT_FLEX,
                    "direction": constants.LAYOUT_DIR_COLUMN,
                    "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
                }

        logger.info(
            "Rule-based analysis could not determine layout, falling back to absolute."
        )
        return {"type": constants.LAYOUT_ABSOLUTE}

    def _analyze_layout_with_llm(self, layers, do_objectID):
        """Analyzes layout using an LLM for complex, mixed layouts."""
        if not self.llm_service:
            logger.warning("LLM client not available. Skipping LLM layout analysis.")
            return None

        logger.info(f"Performing LLM layout analysis for {len(layers)} layers...")
        simplified_layers = [
            {"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")}
            for l in layers
        ]

        prompt = f"""
You are an expert UI layout analyst. Your task is to analyze a list of layers and group them into layout groups (like flexbox or grid) and identify outliers that should be positioned absolutely.

**INSTRUCTIONS:**
1.  Analyze the `frame` properties (x, y, width, height) of the layers. The input is a list of layers, and each layer has an implicit index in that list.
2.  Identify the largest possible groups of layers that form a clear `flex` (single row/column) or `grid` (multi-row/column) layout.
3.  Any layer that does not fit into a clear layout group is an "outlier".
4.  You MUST respond with ONLY a single, raw JSON object. Do not use markdown. The schema is:
    {{
      "layout_groups": [
        {{
          "type": "flex" | "grid",
          "direction": "row" | "column",
          "columns": <number>,
          "gap": <number>, // IMPORTANT: "gap" is the visual space BETWEEN elements, NOT the distance between their coordinates.
          "children_indices": [<index_of_child_1>, <index_of_child_2>, ...]
        }}
      ],
      "outlier_indices": [<index_of_outlier_1>, <index_of_outlier_2>, ...]
    }}
    - `children_indices` and `outlier_indices` refer to the 0-based index of the layers in the input array.
    - Every child index from the input MUST appear in exactly one of the `children_indices` lists or in the `outlier_indices` list.

**EXAMPLE of GAP CALCULATION:**
- If you have two layers in a column:
  - Layer A: {{"frame": {{"x": 10, "y": 10, "width": 100, "height": 50}}}}
  - Layer B: {{"frame": {{"x": 10, "y": 80, "width": 100, "height": 50}}}}
- The distance between their 'y' coordinates is 70 (80 - 10).
- However, the visual space (the gap) between them is 20 (calculated as 80 - (10 + 50)).
- **You should return 20 as the `gap` value.**

**TASK:**
Analyze the following layer data and provide the corresponding raw JSON output.

Input Layers:
```json
{json.dumps(simplified_layers, indent=2)}
```
"""
        try:
            response = self.llm_service.chat(
                model=config.LLM_MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert assistant that analyzes UI layouts. Your only output must be a single, raw JSON object, without any markdown formatting (like ```json), comments, or explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            response_text = response.choices[0].message.content
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )

            layout_info = json.loads(response_text)
            logger.info(f"LLM analysis successful: {layout_info}")
            return layout_info
        except Exception as e:
            logger.error(f"LLM API call failed: {do_objectID}:{e}")
            return None