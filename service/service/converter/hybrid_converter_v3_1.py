
import json
import os
import time
from collections import defaultdict

# --- V3.1 配置项 ---
INPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "output.json"
)
TOKENS_FILE = os.path.join(os.path.dirname(__file__), "design_tokens.json")
DSL_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "dsl_output_v3_1.json"
)
REPORT_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "token_report.json"
)

# --- 大模型 API 配置 ---
ENABLE_LLM_FALLBACK = True
LLM_API_KEY = "lm-studio"  # 在此填入你的 OpenAI API Key


# --- 辅助函数 ---
def convert_color_to_hex(color_obj):
    if not color_obj:
        return None
    r = int(color_obj.get("red", 0) * 255)
    g = int(color_obj.get("green", 0) * 255)
    b = int(color_obj.get("blue", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()


# --- V3.1 核心功能 ---

def load_design_tokens():
    """加载外部设计令牌配置文件"""
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


def preprocess_symbols(sketch_data):
    """预处理 Sketch 数据，建立 symbolID 到语义名称的映射。"""
    symbol_map = {}
    pages = sketch_data.get("layers", [sketch_data])
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


def parse_semantic_name(name):
    """解析如图 'component/button/primary' 的命名"""
    parts = name.split("/")
    if len(parts) < 2:
        return {"type": name, "variant": "default"}
    return {
        "category": parts[0],
        "type": parts[1],
        "variant": parts[2] if len(parts) > 2 else "default",
        "state": parts[3] if len(parts) > 3 else None,
    }

def map_styles_to_tokens(layer, token_maps, report):
    """(V3.1) 将图层样式映射到设计令牌，并报告未知样式。"""
    if not token_maps:
        return {}

    dsl_style = {}
    style = layer.get("style", {})
    layer_name = layer.get("name", "Unnamed")

    # 不透明度
    opacity = style.get("contextSettings", {}).get("opacity", 1.0)
    if opacity < 1.0:
        dsl_style["opacity"] = opacity

    # 背景色
    if (fills := style.get("fills")) and fills and fills[0].get("isEnabled"):
        hex_color = convert_color_to_hex(fills[0].get("color"))
        if hex_color:
            if token := token_maps.get("colors", {}).get(hex_color):
                dsl_style["backgroundColor"] = token
            else:
                print(f"[WARNING] 未知背景色: {hex_color} (图层: '{layer_name}')")
                dsl_style["backgroundColor"] = hex_color
                report["unknown_colors"][hex_color] = report["unknown_colors"].get(hex_color, []) + [layer_name]

    # 文本样式 (字体和颜色)
    if text_style := style.get("textStyle"):
        attrs = text_style.get("encodedAttributes", {})
        # 文本颜色
        if color_attr := attrs.get("MSAttributedStringColorAttribute"):
            hex_color = convert_color_to_hex(color_attr)
            if hex_color:
                if token := token_maps.get("textColors", {}).get(hex_color):
                    dsl_style["textColor"] = token
                else:
                    print(f"[WARNING] 未知文本颜色: {hex_color} (图层: '{layer_name}')")
                    dsl_style["textColor"] = hex_color
                    report["unknown_textColors"][hex_color] = report["unknown_textColors"].get(hex_color, []) + [layer_name]
        # 字体
        font_attrs = attrs.get("MSAttributedStringFontAttribute", {}).get("attributes", {})
        font_name, font_size = font_attrs.get("name"), font_attrs.get("size")
        if font_name and font_size:
            font_key = f"{font_name}-{int(font_size)}"
            if token := token_maps.get("fonts", {}).get(font_key):
                dsl_style["font"] = token
            else:
                print(f"[WARNING] 未知字体: '{font_key}' (图层: '{layer_name}')")
                report["unknown_fonts"][font_key] = report["unknown_fonts"].get(font_key, []) + [layer_name]

    # 边框
    if (borders := style.get("borders")) and borders and borders[0].get("isEnabled"):
        border = borders[0]
        thickness = border.get("thickness", 1)
        dsl_style["borderWidth"] = f"{thickness}px"
        if hex_color := convert_color_to_hex(border.get("color")):
            if token := token_maps.get("borderColors", {}).get(hex_color):
                dsl_style["borderColor"] = token
            else:
                print(f"[WARNING] 未知边框颜色: {hex_color} (图层: '{layer_name}')")
                dsl_style["borderColor"] = hex_color
                report["unknown_borderColors"][hex_color] = report["unknown_borderColors"].get(hex_color, []) + [layer_name]

    # 圆角
    if (radius := layer.get("fixedRadius")) and radius > 0:
        radius_key = str(int(radius))
        if token := token_maps.get("radii", {}).get(radius_key):
            dsl_style["borderRadius"] = token
        else:
            dsl_style["borderRadius"] = f"{radius_key}px"

    # 阴影
    if (shadows := style.get("shadows")) and shadows and shadows[0].get("isEnabled"):
        dsl_style["shadow"] = "default" # 简化处理，可扩展为令牌

    return dsl_style

def traverse_layer(layer, symbol_map, token_maps, report):
    """(V3.1) 递归遍历图层树，生成语义化 DSL 结构"""
    if not layer or not layer.get("isVisible", True):
        return None

    layer_class = layer.get("_class")

    if layer_class == "symbolInstance":
        symbol_id = layer.get("symbolID")
        semantic_name = symbol_map.get(symbol_id, layer.get("name"))
        parsed_name = parse_semantic_name(semantic_name)
        node = {
            "type": parsed_name.get("type", "UnknownComponent"),
            "variant": parsed_name.get("variant"),
            "name": layer.get("name"),
            "frame": layer.get("frame"),
            "style": map_styles_to_tokens(layer, token_maps, report),
            "children": [],
        }
        if overrides := layer.get("overrideValues"):
            for override in overrides:
                if "stringValue" in override and override["stringValue"]:
                    node["content"] = {"text": override["stringValue"]}
                    break
        return node

    elif layer_class == "text":
        return {
            "type": "Text",
            "name": layer.get("name"),
            "frame": layer.get("frame"),
            "content": {"text": layer.get("stringValue")},
            "style": map_styles_to_tokens(layer, token_maps, report),
            "children": [],
        }

    elif layer_class == "group" and layer.get("layers"):
        layout_info = analyze_layout_with_rules(layer["layers"])
        if layout_info["type"] == "absolute" and ENABLE_LLM_FALLBACK:
            layout_info = analyze_layout_with_llm(layer["layers"])
        children_nodes = [
            child_node
            for child in layer["layers"]
            if (child_node := traverse_layer(child, symbol_map, token_maps, report))
        ]
        return {
            "type": "Group",
            "name": layer.get("name"),
            "frame": layer.get("frame"),
            "layout": layout_info,
            "children": children_nodes,
        }
    else:
        return None


def write_token_report(report):
    """生成关于未知令牌的报告文件"""
    if not any(report.values()):
        print("[INFO] 设计系统检查通过，未发现未知令牌。")
        return

    summary = f"发现 {len(report.get('unknown_colors',{}))} 个未知背景色, {len(report.get('unknown_textColors',{}))} 个未知文本颜色, 等。"
    print(f"[ACTION] 检测到未知令牌，正在生成报告文件: {REPORT_OUTPUT_FILE}")
    try:
        with open(REPORT_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"[ERROR] 无法写入报告文件: {e}")

def main():
    """主函数 (V3.1)"""
    print("--- Sketch-to-DSL Converter V3.1 (Guardian Mode) ---")
    token_maps = load_design_tokens()
    report = defaultdict(dict)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            sketch_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 输入文件未找到: {INPUT_FILE}")
        return
    except json.JSONDecodeError:
        print("[ERROR] 输入文件不是有效的 JSON 格式。")
        return

    symbol_map = preprocess_symbols(sketch_data)
    print("开始转换 (语义化模式)...")
    dsl_output = traverse_layer(sketch_data, symbol_map, token_maps, report)

    print(f"转换完成，正在写入 DSL 文件: {DSL_OUTPUT_FILE}")
    try:
        with open(DSL_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(dsl_output, f, ensure_ascii=False, indent=4)
        print(f"成功！V3.1 版本的 DSL 文件已生成于 {DSL_OUTPUT_FILE}")
    except IOError as e:
        print(f"[ERROR] 无法写入 DSL 文件: {e}")

    write_token_report(report)


# --- 布局分析函数 ---
def analyze_layout_with_rules(layers):
    """(V3 Fixed) 分析子元素的布局特征 - 修复了 RuntimeError"""
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
        cols = items_per_row[0]
        h_gaps = [
            r[i + 1]["frame"]["x"] - (r[i]["frame"]["x"] + r[i]["frame"]["width"])
            for r in rows.values()
            for i in range(len(r) - 1)
            if r[i + 1]["frame"]["x"] > (r[i]["frame"]["x"] + r[i]["frame"]["width"])
        ]
        v_gaps = [
            list(rows.values())[i + 1][0]["frame"]["y"]
            - (
                list(rows.values())[i][0]["frame"]["y"]
                + list(rows.values())[i][0]["frame"]["height"]
            )
            for i in range(num_rows - 1)
            if list(rows.values())[i + 1][0]["frame"]["y"]
            > (
                list(rows.values())[i][0]["frame"]["y"]
                + list(rows.values())[i][0]["frame"]["height"]
            )
        ]
        return {
            "type": "grid",
            "columns": cols,
            "h_gap": round(sum(h_gaps) / len(h_gaps)) if h_gaps else 0,
            "v_gap": round(sum(v_gaps) / len(v_gaps)) if v_gaps else 0,
        }
    if num_rows == 1 and items_per_row[0] > 1:
        gaps = [
            layers[i + 1]["frame"]["x"] - (layers[i]["frame"]["x"] + layers[i]["frame"]["width"])
            for i in range(len(layers) - 1)
        ]
        return {
            "type": "flex",
            "direction": "row",
            "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
        }
    if items_per_row and items_per_row[0] == 1 and num_rows > 1:
        gaps = [
            layers[i + 1]["frame"]["y"] - (layers[i]["frame"]["y"] + layers[i]["frame"]["height"])
            for i in range(len(layers) - 1)
        ]
        return {
            "type": "flex",
            "direction": "column",
            "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
        }
    return {"type": "absolute"}

def analyze_layout_with_llm(layers):
    """(V3) 调用 OpenAI 模型进行布局分析"""
    print(f"\n[INFO] 规则分析失败，正在调用 OpenAI 模型分析 {len(layers)} 个图层...")
    if not LLM_API_KEY or "YOUR_OPENAI_API_KEY" in LLM_API_KEY:
        print("[WARNING] OpenAI API Key 未配置。跳过。 ")
        return {"type": "absolute"}
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url="http://localhost:1234/v1",
        )
        simplified_layers = [
            {"name": l.get("name"), "class": l.get("_class"), "frame": l.get("frame")}
            for l in layers
        ]
        prompt = f"""
You are an expert UI layout analyst. Your task is to convert a list of JSON objects representing Sketch layers into a single CSS-like layout object.

**INSTRUCTIONS:**
1. Analyze the `frame` properties (x, y, width, height) of the layers to understand their spatial arrangement.
2. Determine the most appropriate layout model: 'grid', 'flex', or 'absolute'.
3. **Grid Logic:** Infer a 'grid' if you see a multi-row, multi-column structure where items per row are consistent.
4. **Flex Logic:** Infer a 'flex' layout for single-row ('row') or single-column ('column') arrangements.
5. **Gap Calculation:** Calculate the average gap between elements. `gap` should be the space between the edge of one element and the start of the next.
6. **Output Schema:** You MUST respond with ONLY a single JSON object with the following schema:
   - `{{ "type": "grid", "columns": <number>, "gap": <number> }}`
   - `{{ "type": "flex", "direction": "row" | "column", "gap": <number> }}`
   - `{{ "type": "absolute" }}`

**EXAMPLE 1:**
Input Layers:
```json
[
  {{ "frame": {{ "x": 20, "y": 20, "width": 100, "height": 100 }} }},
  {{ "frame": {{ "x": 140, "y": 20, "width": 100, "height": 100 }} }}
]
```
Your Output:
```json
{{
  "type": "flex",
  "direction": "row",
  "gap": 20
}}
```

**EXAMPLE 2:**
Input Layers:
```json
[
  {{ "frame": {{ "x": 20, "y": 20, "width": 100, "height": 40 }} }},
  {{ "frame": {{ "x": 140, "y": 20, "width": 100, "height": 40 }} }},
  {{ "frame": {{ "x": 20, "y": 80, "width": 100, "height": 40 }} }},
  {{ "frame": {{ "x": 140, "y": 80, "width": 100, "height": 40 }} }}
]
```
Your Output:
```json
{{
  "type": "grid",
  "columns": 2,
  "gap": 20
}}
```

**TASK:**
Now, analyze the following layer data and provide the corresponding JSON output.

Input Layers:
```json
{json.dumps(simplified_layers, indent=2)}
```
"""
        print(prompt)
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assistant that analyzes UI layouts. Your only output should be a single, clean JSON object.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            # response_format={"type": "json_object"},
        )
        layout_info = json.loads(response.choices[0].message.content)
        print(f"[INFO] OpenAI 分析成功: {layout_info}")
        return layout_info
    except Exception as e:
        print(f"[ERROR] OpenAI API 调用失败: {e}")
        return {"type": "absolute"}


if __name__ == "__main__":
    main()
