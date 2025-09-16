import json
import os
import time
from collections import defaultdict

# --- V3.2 (DSL Refactor) 配置项 ---
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
# LLM_API_KEY = "AIzaSyC0kAwn91TtXRfnJnTC-qEE9dZNG0vPgS8"  # 用于本地服务，具体值取决于您的设置
# LLM_API_KEY = "lm-studio"  # 用于本地服务，具体值取决于您的设置
LLM_API_KEY = "sk-ddwxtevjbtcuqswmcarbtykkrmlwdydiqqejgqakjayzbyga"  # 用于本地服务，具体值取决于您的设置
# LLM_MODEL_NAME = "gemini-2.5-flash"  # 在此指定要调用的模型名称
# LLM_MODEL_NAME = "openai/gpt-oss-20b"  # 在此指定要调用的模型名称
LLM_MODEL_NAME = "Qwen/QwQ-32B"  # 在此指定要调用的模型名称


# --- 辅助函数 ---
def convert_color_to_hex(color_obj):
    if not color_obj:
        return None
    r = int(color_obj.get("red", 0) * 255)
    g = int(color_obj.get("green", 0) * 255)
    b = int(color_obj.get("blue", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()


# --- V3.2 核心功能 ---


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
                report["unknown_colors"][hex_color] = report["unknown_colors"].get(
                    hex_color, []
                ) + [layer_name]

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
                    report["unknown_textColors"][hex_color] = report[
                        "unknown_textColors"
                    ].get(hex_color, []) + [layer_name]
        # 字体
        font_attrs = attrs.get("MSAttributedStringFontAttribute", {}).get(
            "attributes", {}
        )
        font_name, font_size = font_attrs.get("name"), font_attrs.get("size")
        if font_name and font_size:
            font_key = f"{font_name}-{int(font_size)}"
            if token := token_maps.get("fonts", {}).get(font_key):
                dsl_style["font"] = token
            else:
                print(f"[WARNING] 未知字体: '{font_key}' (图层: '{layer_name}')")
                report["unknown_fonts"][font_key] = report["unknown_fonts"].get(
                    font_key, []
                ) + [layer_name]

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
                report["unknown_borderColors"][hex_color] = report[
                    "unknown_borderColors"
                ].get(hex_color, []) + [layer_name]

    # 圆角
    if (radius := layer.get("fixedRadius")) and radius > 0:
        radius_key = str(int(radius))
        if token := token_maps.get("radii", {}).get(radius_key):
            dsl_style["borderRadius"] = token
        else:
            dsl_style["borderRadius"] = f"{radius_key}px"

    # 阴影
    if (shadows := style.get("shadows")) and shadows and shadows[0].get("isEnabled"):
        dsl_style["shadow"] = "default"  # 简化处理，可扩展为令牌

    return dsl_style


def traverse_layer(
    layer, symbol_map, token_maps, report, parent_layout_type="absolute"
):
    """(V3.8) 递归遍历图层树，生成支持混合布局的 DSL 结构"""
    if not layer or not layer.get("isVisible", True):
        return None

    layer_class = layer.get("_class")
    frame = layer.get("frame", {})
    node = {}
    print(layer_class)

    # 1. 确定基本类型和内容
    if layer_class == "symbolInstance":
        symbol_id = layer.get("symbolID")
        semantic_name = symbol_map.get(symbol_id, layer.get("name"))
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
    else:  # 忽略其他类型的图层，如 shapePath, rectangle 等
        return None

    node["name"] = layer.get("name")

    # 2. 处理样式 (包含尺寸)
    style = map_styles_to_tokens(layer, token_maps, report)
    style["width"] = frame.get("width")
    style["height"] = frame.get("height")
    node["style"] = style

    # 3. 处理布局 (包含定位和子元素)
    layout = {}
    children_nodes = []
    if node["type"] == "Group" and layer.get("layers"):

        layout_analysis = None
        if ENABLE_LLM_FALLBACK:
            layout_analysis = analyze_layout_with_llm(layer["layers"])

        # 如果 LLM 提供了混合布局信息，则使用新逻辑
        if layout_analysis and "layout_groups" in layout_analysis:
            layout["type"] = "absolute"  # 父容器作为定位上下文
            all_child_layers = layer["layers"]
            num_children = len(all_child_layers)
            processed_indices = set()

            # 为 flex/grid 布局创建虚拟组
            for i, group_info in enumerate(layout_analysis["layout_groups"]):
                group_indices = [idx for idx in group_info.get("children_indices", []) if idx < num_children]
                if not group_indices:
                    continue

                group_layers = [all_child_layers[j] for j in group_indices]
                processed_indices.update(group_indices)

                # 计算虚拟组的边界框
                min_x = min(l["frame"]["x"] for l in group_layers)
                min_y = min(l["frame"]["y"] for l in group_layers)
                max_x = max(l["frame"]["x"] + l["frame"]["width"] for l in group_layers)
                max_y = max(
                    l["frame"]["y"] + l["frame"]["height"] for l in group_layers
                )

                # 创建虚拟组节点
                virtual_group_layout = group_info.copy()
                virtual_group_layout["position"] = "absolute"
                virtual_group_layout["top"] = min_y
                virtual_group_layout["left"] = min_x

                virtual_group = {
                    "type": "Group",
                    "name": f"Virtual Group - {group_info.get('type')}",
                    "style": {"width": max_x - min_x, "height": max_y - min_y},
                    "layout": virtual_group_layout,
                    "children": [
                        child
                        for child_layer in group_layers
                        if (
                            child := traverse_layer(
                                child_layer,
                                symbol_map,
                                token_maps,
                                report,
                                parent_layout_type=group_info.get("type"),
                            )
                        )
                    ],
                }
                children_nodes.append(virtual_group)

            # 处理离群元素
            outlier_indices = [idx for idx in layout_analysis.get("outlier_indices", []) if idx < num_children]
            for outlier_index in outlier_indices:
                if outlier_index in processed_indices:
                    continue
                child_layer = all_child_layers[outlier_index]
                if child_node := traverse_layer(
                    child_layer,
                    symbol_map,
                    token_maps,
                    report,
                    parent_layout_type="absolute",
                ):
                    children_nodes.append(child_node)

        else:  # 如果 LLM 失败或被禁用，则回退到基于规则的简单分析
            layout_info = analyze_layout_with_rules(layer["layers"])
            layout.update(layout_info)
            for child in layer["layers"]:
                if child_node := traverse_layer(
                    child,
                    symbol_map,
                    token_maps,
                    report,
                    parent_layout_type=layout.get("type"),
                ):
                    children_nodes.append(child_node)

    # 如果当前节点的父容器是定位上下文，则添加绝对定位信息
    if parent_layout_type == "absolute":
        layout["position"] = "absolute"
        layout["top"] = frame.get("y")
        layout["left"] = frame.get("x")

    node["layout"] = layout
    node["children"] = children_nodes
    return node


def write_token_report(report):
    """生成关于未知令牌的报告文件"""
    if not any(report.values()):
        print("[INFO] 设计系统检查通过，未发现未知令牌。")
        return

    summary = f"发现 {len(report.get('unknown_colors', {}))} 个未知背景色, {len(report.get('unknown_textColors', {}))} 个未知文本颜色, 等。"
    print(f"[ACTION] 检测到未知令牌，正在生成报告文件: {REPORT_OUTPUT_FILE}")
    try:
        with open(REPORT_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"[ERROR] 无法写入报告文件: {e}")


def main():
    """主函数 (V3.9) - 增加对 Page 根节点的处理"""
    print("--- Sketch-to-DSL Converter V3.9 (Page & Artboard Support) ---")
    token_maps = load_design_tokens()
    report = defaultdict(dict)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            sketch_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 输入文件未找到: {INPUT_FILE}")
        return
    except json.JSONDecodeError:
        print(f"[ERROR] 输入文件不是有效的 JSON 格式。")
        return

    # --- 新增逻辑：处理 Page 根节点 ---
    target_layer = sketch_data
    if sketch_data.get("_class") == "page":
        print("[INFO] 检测到根节点为 Page，正在查找可处理的画板...")
        # 查找第一个可见的 artboard 或 group 作为处理起点
        for layer in sketch_data.get("layers", []):
            if layer.get("_class") in ["artboard", "group"] and layer.get("isVisible", True):
                target_layer = layer
                print(f"[INFO] 找到处理起点: '{target_layer.get('name')}' ({target_layer.get('_class')})")
                break
        
        if target_layer is sketch_data: # 如果没有找到任何可处理的图层
            print("[ERROR] Page 中未找到任何可见的 Artboard 或 Group。")
            return
    # --- 结束新增逻辑 ---

    symbol_map = preprocess_symbols(sketch_data) # Symbol 预处理仍然在整个文件上进行
    print("开始转换 (语义化模式)...")
    dsl_output = traverse_layer(target_layer, symbol_map, token_maps, report)

    print(f"转换完成，正在写入 DSL 文件: {DSL_OUTPUT_FILE}")
    try:
        with open(DSL_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(dsl_output, f, ensure_ascii=False, indent=4)
        print(f"成功！V3.9 版本的 DSL 文件已生成于 {DSL_OUTPUT_FILE}")
    except IOError as e:
        print(f"[ERROR] 无法写入 DSL 文件: {e}")

    write_token_report(report)


# --- 布局分析函数 ---
def analyze_layout_with_rules(layers):
    """
    (V3.3) 分析子元素的布局特征 - 增加重叠检测.
    如果检测到 flex 布局中存在元素重叠（gap < 0），则回退到 absolute 布局,
    从而允许 LLM 进行更复杂的分析。
    """
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
            layers[i + 1]["frame"]["x"]
            - (layers[i]["frame"]["x"] + layers[i]["frame"]["width"])
            for i in range(len(layers) - 1)
        ]
        # 如果存在任何重叠（gap为负数），则认为它不是一个简单的 flex 布局
        if any(g < 0 for g in gaps):
            return {"type": "absolute"}

        return {
            "type": "flex",
            "direction": "row",
            "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
        }
    if items_per_row and items_per_row[0] == 1 and num_rows > 1:
        gaps = [
            layers[i + 1]["frame"]["y"]
            - (layers[i]["frame"]["y"] + layers[i]["frame"]["height"])
            for i in range(len(layers) - 1)
        ]
        # 如果存在任何重叠（gap为负数），则认为它不是一个简单的 flex 布局
        if any(g < 0 for g in gaps):
            return {"type": "absolute"}

        return {
            "type": "flex",
            "direction": "column",
            "gap": round(sum(gaps) / len(gaps)) if gaps else 0,
        }
    return {"type": "absolute"}


def analyze_layout_with_llm(layers):
    """(V3.7) 调用 OpenAI 模型进行高级混合布局分析"""
    print(f"\n[INFO] 规则分析失败，正在调用 OpenAI 模型分析 {len(layers)} 个图层...")
    if not LLM_API_KEY or "YOUR_OPENAI_API_KEY" in LLM_API_KEY:
        print("[WARNING] OpenAI API Key 未配置。跳过。 ")
        return None
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=LLM_API_KEY,
            # base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            # base_url="http://127.0.0.1:1234/v1",
            base_url="https://api.siliconflow.cn/v1",
        )
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
          "gap": <number>,
          "children_indices": [<index_of_child_1>, <index_of_child_2>, ...]
        }}
      ],
      "outlier_indices": [<index_of_outlier_1>, <index_of_outlier_2>, ...]
    }}
    - `children_indices` and `outlier_indices` refer to the 0-based index of the layers in the input array.
    - Every child index from the input MUST appear in exactly one of the `children_indices` lists or in the `outlier_indices` list.

**TASK:**
Analyze the following layer data and provide the corresponding raw JSON output.

Input Layers:
```json
{json.dumps(simplified_layers, indent=2)}
```
"""
        # print(prompt)
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assistant that analyzes UI layouts. Your only output must be a single, raw JSON object, without any markdown formatting (like ```json), comments, or explanations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            # response_format={"type": "json_object"},
        )

        # 打印 Token 使用情况
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            print(
                f"[INFO] Token usage: Prompt={prompt_tokens}, Completion={completion_tokens}, Total={total_tokens}"
            )

        # Defensive post-processing to remove markdown
        response_text = response.choices[0].message.content
        print(response_text)  # Print the raw response for debugging
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()

        layout_info = json.loads(response_text)
        print(f"[INFO] OpenAI 分析成功: {layout_info}")
        return layout_info
    except Exception as e:
        print(f"\033[91m[ERROR] OpenAI API 调用失败: {e}\033[0m")
        return None


if __name__ == "__main__":
    main()
