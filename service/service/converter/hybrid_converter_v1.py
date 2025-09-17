import json
import os
import time
import statistics
from collections import defaultdict

# --- V3.12 (Refactored) 配置项 ---
INPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "6B6771BA-E1C8-40F1-938C-19EDD4C50371.json"
)
TOKENS_FILE = os.path.join(os.path.dirname(__file__), "design_tokens.json")
DSL_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "dsl_output_v3_2.json"
)
REPORT_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "token_report.json"
)

# --- 大模型 API 配置 ---
ENABLE_LLM_FALLBACK = True
LLM_API_KEY = "sk-ddwxtevjbtcuqswmcarbtykkrmlwdydiqqejgqakjayzbyga"  # 硅基流动
LLM_MODEL_NAME = "Qwen/QwQ-32B"  # 硅基流动


# --- 辅助函数 ---
def convert_color_to_hex(color_obj):
    """将 Sketch 的颜色对象转换为十六进制颜色字符串。"""
    if not color_obj:
        return None
    r = int(color_obj.get("red", 0) * 255)
    g = int(color_obj.get("green", 0) * 255)
    b = int(color_obj.get("blue", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()

def parse_semantic_name(name):
    """解析如图 'component/button/primary' 的命名。"""
    parts = name.split("/")
    if len(parts) < 2:
        return {"type": name, "variant": "default"}
    return {
        "category": parts[0],
        "type": parts[1],
        "variant": parts[2] if len(parts) > 2 else "default",
        "state": parts[3] if len(parts) > 3 else None,
    }


class SketchConverter:
    """
    (V3.12) 封装了从 Sketch JSON 转换为 DSL 的核心逻辑。
    此次重构旨在提高代码的可维护性和可扩展性。
    """

    def __init__(self, sketch_data):
        print("--- Sketch-to-DSL Converter V3.12 (Refactored) ---")
        self.sketch_data = sketch_data
        self.token_maps = self._load_design_tokens()
        self.symbol_map = self._preprocess_symbols()
        self.report = defaultdict(dict)
        self.llm_client = None

        if ENABLE_LLM_FALLBACK and LLM_API_KEY and "YOUR_API_KEY" not in LLM_API_KEY:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(
                    api_key=LLM_API_KEY,
                    base_url="https://api.siliconflow.cn/v1",
                )
                print("[INFO] LLM 客户端已初始化。")
            except ImportError:
                print("[WARNING] 未安装 'openai' 库，无法使用 LLM 功能。")
            except Exception as e:
                print(f"\033[91m[ERROR] 初始化 LLM 客户端失败: {e}\033[0m")

    def _load_design_tokens(self):
        """加载外部设计令牌配置文件。"""
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                print(f"[INFO] 成功加载设计令牌文件: {TOKENS_FILE}")
                return json.load(f)
        except FileNotFoundError:
            print(f"[WARNING] 设计令牌文件未找到: {TOKENS_FILE}。")
            return {}
        except json.JSONDecodeError:
            print(f"[WARNING] 设计令牌文件格式错误。")
            return {}

    def _preprocess_symbols(self):
        """预处理 Sketch 数据，建立 symbolID 到语义名称的映射。"""
        symbol_map = {}
        pages = self.sketch_data.get("layers", [self.sketch_data])
        for page in pages:
            if "layers" not in page:
                continue
            for artboard in page["layers"]:
                if artboard.get("_class") in ["artboard", "symbolMaster"]:
                    for item in artboard.get("layers", []):
                        if item.get("_class") == "symbolMaster":
                            symbol_map[item.get("symbolID")] = item.get("name")
        print(f"[INFO] 预处理完成，找到 {len(symbol_map)} 个主元件(Symbols)。")
        return symbol_map

    def convert(self):
        """执行转换过程并保存输出文件。"""
        print("开始转换 (语义化模式)...")
        target_layer = self._find_target_layer()
        if not target_layer:
            return None

        dsl_output = self._traverse_layer(target_layer)

        print(f"转换完成，正在写入 DSL 文件: {DSL_OUTPUT_FILE}")
        try:
            with open(DSL_OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(dsl_output, f, ensure_ascii=False, indent=4)
            print(f"成功！V3.12 版本的 DSL 文件已生成于 {DSL_OUTPUT_FILE}")
        except IOError as e:
            print(f"[ERROR] 无法写入 DSL 文件: {e}")

        self._write_token_report()
        return dsl_output

    def _find_target_layer(self):
        """从根数据中找到要处理的第一个有效图层（Artboard 或 Group）。"""
        root = self.sketch_data
        if root.get("_class") == "page":
            print("[INFO] 检测到根节点为 Page，正在查找可处理的画板...")
            for layer in root.get("layers", []):
                if layer.get("_class") in ["artboard", "group"] and layer.get("isVisible", True):
                    print(f"[INFO] 找到处理起点: '{layer.get('name')}' ({layer.get('_class')})")
                    return layer
            print("[ERROR] Page 中未找到任何可见的 Artboard 或 Group。")
            return None
        return root

    def _traverse_layer(self, layer, parent_layout_type="absolute"):
        """递归遍历图层，将其转换为 DSL 节点。"""
        if not layer or not layer.get("isVisible", True):
            return None

        node = self._create_base_node(layer)
        if not node:
            return None

        self._apply_styles_to_node(node, layer)
        self._process_layout_and_children(node, layer, parent_layout_type)

        return node

    def _create_base_node(self, layer):
        """根据图层类型创建基础 DSL 节点。"""
        layer_class = layer.get("_class")
        node = {"name": layer.get("name")}

        if layer_class == "symbolInstance":
            symbol_id = layer.get("symbolID")
            semantic_name = self.symbol_map.get(symbol_id, layer.get("name"))
            parsed_name = parse_semantic_name(semantic_name)
            node["type"] = parsed_name.get("type", "UnknownComponent")
            node["variant"] = parsed_name.get("variant")
            if overrides := layer.get("overrideValues"):
                for override in overrides:
                    if "stringValue" in override and override["stringValue"]:
                        node["content"] = {"text": override["stringValue"]}
                        break
        elif layer_class == "text":
            node["type"] = "Text"
            node["content"] = {"text": layer.get("stringValue")}
        elif layer_class in ["group", "artboard"]:
            node["type"] = "Group"
        elif layer_class in ["oval", "rectangle", "shapePath"]:
            node["type"] = "Shape"
        else:
            return None
        return node

    def _apply_styles_to_node(self, node, layer):
        """将图层样式映射到 DSL 节点的 style 属性。"""
        dsl_style = {}
        style = layer.get("style", {})
        layer_name = layer.get("name", "Unnamed")

        # (此部分逻辑与旧版 map_styles_to_tokens 函数基本相同)
        opacity = style.get("contextSettings", {}).get("opacity", 1.0)
        if opacity < 1.0:
            dsl_style["opacity"] = opacity

        if (fills := style.get("fills")) and fills and fills[0].get("isEnabled"):
            hex_color = convert_color_to_hex(fills[0].get("color"))
            if hex_color:
                if token := self.token_maps.get("colors", {}).get(hex_color):
                    dsl_style["backgroundColor"] = token
                else:
                    dsl_style["backgroundColor"] = hex_color
                    self.report["unknown_colors"][hex_color] = self.report["unknown_colors"].get(hex_color, []) + [layer_name]

        if text_style := style.get("textStyle"):
            attrs = text_style.get("encodedAttributes", {})
            if color_attr := attrs.get("MSAttributedStringColorAttribute"):
                hex_color = convert_color_to_hex(color_attr)
                if hex_color:
                    if token := self.token_maps.get("textColors", {}).get(hex_color):
                        dsl_style["textColor"] = token
                    else:
                        dsl_style["textColor"] = hex_color
                        self.report["unknown_textColors"][hex_color] = self.report["unknown_textColors"].get(hex_color, []) + [layer_name]
            font_attrs = attrs.get("MSAttributedStringFontAttribute", {}).get("attributes", {})
            font_name, font_size = font_attrs.get("name"), font_attrs.get("size")
            if font_name and font_size:
                font_key = f"{font_name}-{int(font_size)}"
                if token := self.token_maps.get("fonts", {}).get(font_key):
                    dsl_style["font"] = token
                else:
                    self.report["unknown_fonts"][font_key] = self.report["unknown_fonts"].get(font_key, []) + [layer_name]

        if (borders := style.get("borders")) and borders and borders[0].get("isEnabled"):
            border = borders[0]
            dsl_style["borderWidth"] = f'{border.get("thickness", 1)}px'
            if hex_color := convert_color_to_hex(border.get("color")):
                if token := self.token_maps.get("borderColors", {}).get(hex_color):
                    dsl_style["borderColor"] = token
                else:
                    dsl_style["borderColor"] = hex_color
                    self.report["unknown_borderColors"][hex_color] = self.report["unknown_borderColors"].get(hex_color, []) + [layer_name]

        radius = layer.get("fixedRadius", 0)
        if not radius and "points" in layer and layer.get("points"):
            radius = layer["points"][0].get("cornerRadius", 0)
        if radius > 0:
            radius_key = str(int(radius))
            if token := self.token_maps.get("radii", {}).get(radius_key):
                dsl_style["borderRadius"] = token
            else:
                dsl_style["borderRadius"] = f"{radius_key}px"

        if (shadows := style.get("shadows")) and shadows and shadows[0].get("isEnabled"):
            dsl_style["shadow"] = "default"

        frame = layer.get("frame", {})
        dsl_style["width"] = frame.get("width")
        dsl_style["height"] = frame.get("height")
        node["style"] = dsl_style

    def _process_layout_and_children(self, node, layer, parent_layout_type):
        """处理节点的布局和子节点。"""
        layout = {}
        children_nodes = []

        if node["type"] == "Group" and layer.get("layers"):
            # 优先处理 FreeformGroupLayout
            if layer.get("groupLayout", {}).get("_class") == "MSImmutableFreeformGroupLayout":
                layout["type"] = "absolute"
                for child in layer["layers"]:
                    if child_node := self._traverse_layer(child, parent_layout_type="absolute"):
                        children_nodes.append(child_node)
            else:
                # 否则，回退到基于规则的自动布局分析
                # (此处为简化，未包含复杂的 LLM 混合布局逻辑)
                layout_info = self._analyze_layout_with_rules(layer["layers"])
                layout.update(layout_info)
                for child in layer["layers"]:
                    if child_node := self._traverse_layer(child, parent_layout_type=layout.get("type")):
                        children_nodes.append(child_node)

        if parent_layout_type == "absolute":
            frame = layer.get("frame", {})
            layout["position"] = "absolute"
            layout["top"] = frame.get("y")
            layout["left"] = frame.get("x")

        node["layout"] = layout
        node["children"] = children_nodes

    def _calculate_average_gap(self, layers, direction):
        """根据图层列表和方向精确计算平均间距。"""
        if len(layers) < 2:
            return 0
        if direction == "column":
            layers.sort(key=lambda l: l["frame"]["y"])
            gaps = [layers[i + 1]["frame"]["y"] - (layers[i]["frame"]["y"] + layers[i]["frame"]["height"]) for i in range(len(layers) - 1)]
        else:
            layers.sort(key=lambda l: l["frame"]["x"])
            gaps = [layers[i + 1]["frame"]["x"] - (layers[i]["frame"]["x"] + layers[i]["frame"]["width"]) for i in range(len(layers) - 1)]
        if not gaps or any(g < 0 for g in gaps):
            return 0
        return round(sum(gaps) / len(gaps))

    def _analyze_layout_with_rules(self, layers):
        """分析子元素的布局特征。"""
        if not layers or len(layers) < 2:
            return {"type": "absolute"}
        layers.sort(key=lambda l: (l["frame"]["y"], l["frame"]["x"]))

        rows = defaultdict(list)
        y_threshold = 10
        for layer in layers:
            found_row = False
            for y_key in list(rows.keys()):
                if abs(layer["frame"]["y"] - y_key) < y_threshold:
                    rows[y_key].append(layer)
                    found_row = True
                    break
            if not found_row:
                rows[layer["frame"]["y"]].append(layer)

        num_rows, items_per_row = len(rows), [len(r) for r in rows.values()]

        if num_rows > 1 and len(set(items_per_row)) == 1 and items_per_row[0] > 1:
            return {"type": "grid", "columns": items_per_row[0]}

        if num_rows == 1 and items_per_row[0] > 1:
            gap = self._calculate_average_gap(layers, "row")
            return {"type": "flex", "direction": "row", "gap": gap}

        if items_per_row and all(count == 1 for count in items_per_row) and num_rows > 1:
            x_coords = [l["frame"]["x"] for l in layers]
            x_threshold = 5
            x_std_dev = statistics.stdev(x_coords) if len(x_coords) > 1 else 0
            if x_std_dev <= x_threshold:
                gap = self._calculate_average_gap(layers, "column")
                return {"type": "flex", "direction": "column", "gap": gap}

        print("[INFO] 规则分析无法确定布局，回退到 absolute。")
        return {"type": "absolute"}

    def _write_token_report(self):
        """生成关于未知令牌的报告文件。"""
        if not any(self.report.values()):
            print("[INFO] 设计系统检查通过，未发现未知令牌。")
            return

        print(f"[ACTION] 检测到未知令牌，正在生成报告文件: {REPORT_OUTPUT_FILE}")
        try:
            with open(REPORT_OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.report, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"[ERROR] 无法写入报告文件: {e}")


def main():
    """主函数：加载数据并启动转换器。"""
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            sketch_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 输入文件未找到: {INPUT_FILE}")
        return
    except json.JSONDecodeError:
        print(f"[ERROR] 输入文件不是有效的 JSON 格式。")
        return

    converter = SketchConverter(sketch_data)
    converter.convert()


if __name__ == "__main__":
    main()