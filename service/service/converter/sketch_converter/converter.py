import json
import logging
import statistics
from collections import defaultdict
from openai import OpenAI

from . import config, constants, utils

# Setup logging - use Django's logging configuration
logger = logging.getLogger(__name__)


class SketchConverter:
    """
    A class to convert Sketch JSON data to a design-specific DSL.
    It encapsulates the entire conversion process, including loading data,
    parsing layers, mapping styles to tokens, and generating output files.
    """

    def __init__(self, input_file, tokens_file, dsl_output_file, report_output_file, progress_callback):
        """
        Initializes the converter with configuration.
        """
        self.input_file = input_file
        self.tokens_file = tokens_file
        self.dsl_output_file = dsl_output_file
        self.report_output_file = report_output_file

        self.sketch_data = None
        self.token_maps = {}
        self.symbol_map = {}
        self.report = defaultdict(dict)
        self.llm_client = None
        self.progress_callback = progress_callback
        if config.ENABLE_LLM_FALLBACK and config.LLM_API_KEY:
            try:
                self.llm_client = OpenAI(
                    api_key=config.LLM_API_KEY,
                    base_url=config.LLM_BASE_URL,
                )
                logger.info("OpenAI client initialized successfully.")
                self.llm_usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.llm_client = None
        else:
            logger.warning("LLM fallback is disabled or API key is not configured.")

    def run(self):
        """
        Executes the full conversion pipeline.
        """
        logger.info(f"--- Sketch-to-DSL Converter (Refactored) ---")
        logger.info("=== 转换器日志测试 ===")
        self._load_sketch_data()
        self._load_design_tokens()
        self._preprocess_symbols()
        target_layer = self._find_main_artboard()
        if not target_layer:
            logger.error("No suitable artboard or group found to process in the Sketch file.")
            return

        logger.info("Starting conversion...")
        dsl_output = self._traverse_layer(target_layer)
        self._write_dsl_output(dsl_output)
        self._write_token_report()
        logger.info("Conversion process completed.")
        return dsl_output  # 添加返回值

    def _load_sketch_data(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                self.sketch_data = json.load(f)
                logger.info(f"Successfully loaded sketch file: {self.input_file}")
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in sketch file: {self.input_file}")
            raise

    def _load_design_tokens(self):
        try:
            with open(self.tokens_file, "r", encoding="utf-8") as f:
                self.token_maps = json.load(f)
                logger.info(f"Successfully loaded design tokens: {self.tokens_file}")
        except FileNotFoundError:
            logger.warning(f"Design tokens file not found: {self.tokens_file}. Proceeding without tokens.")
            self.token_maps = {}
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in tokens file: {self.tokens_file}. Proceeding without tokens.")
            self.token_maps = {}

    def _preprocess_symbols(self):
        """Builds a map from symbolID to its semantic name."""
        pages = self.sketch_data.get("layers", [self.sketch_data])
        for page in pages:
            if "layers" not in page:
                continue
            for artboard in page.get("layers", []):
                if artboard.get("_class") in [constants.LAYER_ARTBOARD, constants.LAYER_SYMBOL_MASTER]:
                    for item in artboard.get("layers", []):
                        if item.get("_class") == constants.LAYER_SYMBOL_MASTER:
                            self.symbol_map[item.get("symbolID")] = item.get("name")
        logger.info(f"Preprocessing complete. Found {len(self.symbol_map)} symbols.")

    def _find_main_artboard(self):
        """Finds the first visible artboard or group to process, especially if the root is a page."""
        if self.sketch_data.get("_class") != constants.LAYER_PAGE:
            return self.sketch_data

        logger.info("Root node is a Page, searching for a processable artboard/group...")
        for layer in self.sketch_data.get("layers", []):
            if layer.get("_class") in [constants.LAYER_ARTBOARD, constants.LAYER_GROUP, constants.LAYER_PAGE] and layer.get("isVisible", True):
                logger.info(f"Found starting point: '{layer.get('name')}' ({layer.get('_class')})")
                return layer
        return None

    def _map_styles_to_tokens(self, layer):
        """Maps layer styles to design tokens and reports unknown styles."""
        if not self.token_maps:
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
                token = self.token_maps.get("colors", {}).get(hex_color)
                if token:
                    dsl_style["backgroundColor"] = token
                else:
                    logger.warning(f"Unknown background color: {hex_color} (Layer: '{layer_name}')")
                    dsl_style["backgroundColor"] = hex_color
                    self.report["unknown_colors"].setdefault(hex_color, []).append(layer_name)
        
        # Text Style
        if text_style := style.get("textStyle"):
            self._map_text_style(text_style, dsl_style, layer_name)

        # Borders
        if (borders := style.get("borders")) and borders and borders[0].get("isEnabled"):
            self._map_border_style(borders[0], dsl_style, layer_name)

        # Corner Radius
        if (radius := layer.get("fixedRadius")) and radius > 0:
            radius_key = str(int(radius))
            token = self.token_maps.get("radii", {}).get(radius_key)
            dsl_style["borderRadius"] = token if token else f"{radius_key}px"

        # Shadows
        if (shadows := style.get("shadows")) and shadows and shadows[0].get("isEnabled"):
            dsl_style["shadow"] = "default"  # Simplified, can be tokenized

        return dsl_style

    def _map_text_style(self, text_style, dsl_style, layer_name):
        """Helper to map text color and font."""
        attrs = text_style.get("encodedAttributes", {})
        # Text Color
        if color_attr := attrs.get("MSAttributedStringColorAttribute"):
            hex_color = utils.convert_color_to_hex(color_attr)
            if hex_color:
                token = self.token_maps.get("textColors", {}).get(hex_color)
                if token:
                    dsl_style["textColor"] = token
                else:
                    logger.warning(f"Unknown text color: {hex_color} (Layer: '{layer_name}')")
                    dsl_style["textColor"] = hex_color
                    self.report["unknown_textColors"].setdefault(hex_color, []).append(layer_name)
        # Font
        font_attrs = attrs.get("MSAttributedStringFontAttribute", {}).get("attributes", {})
        font_name, font_size = font_attrs.get("name"), font_attrs.get("size")
        if font_name and font_size:
            font_key = f"{font_name}-{int(font_size)}"
            token = self.token_maps.get("fonts", {}).get(font_key)
            if token:
                dsl_style["font"] = token
            else:
                logger.warning(f"Unknown font: '{font_key}' (Layer: '{layer_name}')")
                self.report["unknown_fonts"].setdefault(font_key, []).append(layer_name)

    def _map_border_style(self, border, dsl_style, layer_name):
        """Helper to map border width and color."""
        dsl_style["borderWidth"] = f"{border.get('thickness', 1)}px"
        if hex_color := utils.convert_color_to_hex(border.get("color")):
            token = self.token_maps.get("borderColors", {}).get(hex_color)
            if token:
                dsl_style["borderColor"] = token
            else:
                logger.warning(f"Unknown border color: {hex_color} (Layer: '{layer_name}')")
                dsl_style["borderColor"] = hex_color
                self.report["unknown_borderColors"].setdefault(hex_color, []).append(layer_name)

    def _traverse_layer(self, layer, parent_layout_type=constants.LAYOUT_ABSOLUTE):
        """Recursively traverses the layer tree to build the DSL structure."""
        # 实时进度
        if self.progress_callback:
            self.progress_callback()

        if not layer or not layer.get("isVisible", True):
            return None

        layer_class = layer.get("_class")
        frame = layer.get("frame", {})
        node = {}

        # 1. Determine node type and content
        # if layer_class == constants.LAYER_SYMBOL_INSTANCE:
        #     symbol_id = layer.get("symbolID")
        #     semantic_name = self.symbol_map.get(symbol_id, layer.get("name"))
        #     parsed_name = utils.parse_semantic_name(semantic_name)
        #     node["type"] = parsed_name.get("type", constants.NODE_UNKNOWN_COMPONENT)
        #     node["variant"] = parsed_name.get("variant")
        #     if overrides := layer.get("overrideValues"):
        #         for override in overrides:
        #             if "stringValue" in override and override["stringValue"]:
        #                 node["content"] = {"text": override["stringValue"]}
        #                 break
        # elif layer_class == constants.LAYER_TEXT:
        #     node["type"] = constants.NODE_TEXT
        #     node["content"] = {"text": layer.get("stringValue")}
        # elif layer_class in [constants.LAYER_GROUP, constants.LAYER_ARTBOARD]:
        #     node["type"] = constants.NODE_GROUP
        # elif layer_class == constants.LAYER_RECTANGLE:
        #     node["type"] = constants.NODE_RECTANGLE
        # elif layer_class == constants.LAYER_OVAL:
        #     node["type"] = constants.NODE_OVAL
        # else:
        #     logger.info(f"Ignoring layer type: {layer_class} (Name: '{layer.get('name')}')")
        #     return None
        
        node["type"] = layer_class
        node["name"] = layer.get("name")
        node["do_objectID"] = layer.get("do_objectID")

        # 2. Map styles and dimensions
        style = self._map_styles_to_tokens(layer)
        style["width"] = frame.get("width")
        style["height"] = frame.get("height")
        node["style"] = style

        # 3. Handle layout and children
        layout = {}
        children_nodes = []
        if node["type"] == constants.LAYER_GROUP and layer.get("layers"):
            child_layers = layer["layers"]
            layout_analysis = self._analyze_layout_with_llm(child_layers) if self.llm_client else None
            if layout_analysis and "layout_groups" in layout_analysis:
                # Advanced layout processing with LLM result
                layout["type"] = constants.LAYOUT_ABSOLUTE
                children_nodes = self._process_llm_layout_analysis(layout_analysis, child_layers)
            else:
                # Fallback to rule-based analysis
                layout_info = self._analyze_layout_with_rules(child_layers)
                layout.update(layout_info)
                for child in child_layers:
                    if child_node := self._traverse_layer(child, parent_layout_type=layout.get("type")):
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

        # Create virtual groups for flex/grid layouts
        for group_info in layout_analysis.get("layout_groups", []):
            group_indices = [idx for idx in group_info.get("children_indices", []) if idx < num_children]
            if not group_indices:
                continue

            group_layers = [all_child_layers[j] for j in group_indices]
            processed_indices.update(group_indices)

            min_x = min(l["frame"]["x"] for l in group_layers)
            min_y = min(l["frame"]["y"] for l in group_layers)
            max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
            max_y = max(l["frame"]["y"] + l["frame"]["height"] for l in group_layers)

            virtual_group_layout = group_info.copy()
            virtual_group_layout.update({
                "position": constants.LAYOUT_ABSOLUTE,
                "top": min_y,
                "left": min_x
            })

            virtual_group_children = []
            for child_layer in group_layers:
                # Adjust child frame relative to the new virtual group
                adjusted_layer = child_layer.copy()
                adjusted_layer['frame'] = adjusted_layer['frame'].copy()
                adjusted_layer['frame']['x'] -= min_x
                adjusted_layer['frame']['y'] -= min_y
                
                if child_node := self._traverse_layer(adjusted_layer, parent_layout_type=group_info.get("type")):
                    virtual_group_children.append(child_node)

            virtual_group = {
                "type": constants.NODE_GROUP,
                "name": f"Virtual Group - {group_info.get('type')}",
                "style": {"width": max_x - min_x, "height": max_y - min_y},
                "layout": virtual_group_layout,
                "children": virtual_group_children,
            }
            children_nodes.append(virtual_group)

        # Process outlier layers
        outlier_indices = [idx for idx in layout_analysis.get("outlier_indices", []) if idx < num_children]
        for outlier_index in outlier_indices:
            if outlier_index in processed_indices:
                continue
            if child_node := self._traverse_layer(all_child_layers[outlier_index], parent_layout_type=constants.LAYOUT_ABSOLUTE):
                children_nodes.append(child_node)
        
        return children_nodes

    def _analyze_layout_with_rules(self, layers):
        """Analyzes layout based on geometric rules."""
        if not layers or len(layers) < 2:
            return {"type": constants.LAYOUT_ABSOLUTE}
        
        layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))
        
        # Row grouping
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

        # Grid layout
        if num_rows > 1 and len(set(items_per_row)) == 1 and items_per_row[0] > 1:
            return {"type": constants.LAYOUT_GRID, "columns": items_per_row[0]}

        # Flex row
        if num_rows == 1 and items_per_row[0] > 1:
            gaps = [layers[i+1]["frame"]["x"] - (layers[i]["frame"]["x"] + layers[i]["frame"]["width"]) for i in range(len(layers) - 1)]
            if any(g < 0 for g in gaps): return {"type": constants.LAYOUT_ABSOLUTE}
            return {"type": constants.LAYOUT_FLEX, "direction": constants.LAYOUT_DIR_ROW, "gap": round(sum(gaps) / len(gaps)) if gaps else 0}

        # Flex column
        if items_per_row and all(c == 1 for c in items_per_row) and num_rows > 1:
            x_coords = [l["frame"]["x"] for l in layers]
            x_std_dev = statistics.stdev(x_coords) if len(x_coords) > 1 else 0
            if x_std_dev <= config.LAYOUT_X_THRESHOLD:
                gaps = [layers[i+1]["frame"]["y"] - (layers[i]["frame"]["y"] + layers[i]["frame"]["height"]) for i in range(len(layers) - 1)]
                if any(g < 0 for g in gaps): return {"type": constants.LAYOUT_ABSOLUTE}
                return {"type": constants.LAYOUT_FLEX, "direction": constants.LAYOUT_DIR_COLUMN, "gap": round(sum(gaps) / len(gaps)) if gaps else 0}

        logger.info("Rule-based analysis could not determine layout, falling back to absolute.")
        return {"type": constants.LAYOUT_ABSOLUTE}

    def _analyze_layout_with_llm(self, layers):
        """Analyzes layout using an LLM for complex, mixed layouts."""
        if not self.llm_client:
            logger.warning("LLM client not available. Skipping LLM layout analysis.")
            return None

        logger.info(f"Performing LLM layout analysis for {len(layers)} layers...")
        simplified_layers = [{"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")} for l in layers]
        
        # Original prompt, restored for compatibility with all models.
        prompt = f'''
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
'''
        try:
            response = self.llm_client.chat.completions.create(
                model=config.LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert assistant that analyzes UI layouts. Your only output must be a single, raw JSON object, without any markdown formatting (like ```json), comments, or explanations."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                # response_format={"type": "json_object"}, # Removed for compatibility
            )
            print(response)
            
            if response.usage:
                logger.info(f"Token usage: {response.usage.total_tokens} total tokens.")
                usage = getattr(response, "usage", None)
                if usage:
                    self.llm_usage["prompt_tokens"] += usage.prompt_tokens
                    self.llm_usage["completion_tokens"] += usage.completion_tokens
                    self.llm_usage["total_tokens"] += usage.total_tokens

            # Defensive post-processing to remove markdown, restored from original script
            response_text = response.choices[0].message.content
            logger.info(f"Raw LLM response: {response_text}")
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()

            layout_info = json.loads(response_text)
            logger.info(f"LLM analysis successful: {layout_info}")
            return layout_info
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None

    def _write_dsl_output(self, dsl_output):
        """Writes the final DSL to the output file."""
        logger.info(f"Writing DSL output to: {self.dsl_output_file}")
        try:
            with open(self.dsl_output_file, "w", encoding="utf-8") as f:
                json.dump(dsl_output, f, ensure_ascii=False, indent=4)
            logger.info("DSL file successfully generated.")
        except IOError as e:
            logger.error(f"Failed to write DSL file: {e}")

    def _write_token_report(self):
        """Writes a report of all unknown tokens found during conversion."""
        if not any(self.report.values()):
            logger.info("Design system check passed. No unknown tokens found.")
            return

        logger.warning(f"Detected unknown tokens. Generating report at: {self.report_output_file}")
        try:
            with open(self.report_output_file, "w", encoding="utf-8") as f:
                json.dump(self.report, f, ensure_ascii=False, indent=4)
            logger.info("Token report successfully generated.")
        except IOError as e:
            logger.error(f"Failed to write token report: {e}")
