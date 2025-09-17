import json
import os

# --- 配置项 ---
DSL_INPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "dsl_output_refactored.json"
)
HTML_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "media", "sketches", "output.html"
)

# 用于调试的背景色列表
DEBUG_COLORS = [
    "rgba(255, 99, 132, 0.2)",   # Red
    "rgba(54, 162, 235, 0.2)",  # Blue
    "rgba(255, 206, 86, 0.2)",  # Yellow
    "rgba(75, 192, 192, 0.2)",  # Green
    "rgba(153, 102, 255, 0.2)", # Purple
    "rgba(255, 159, 64, 0.2)",   # Orange
]

def dsl_node_to_html(node, level=0):
    """递归地将单个 DSL 节点转换为 HTML 字符串，并根据层级添加调试颜色。"""
    if not node:
        return ""

    # 1. 生成当前节点的样式
    styles = []
    node_style = node.get("style", {})
    node_layout = node.get("layout", {})

    # --- 定位和尺寸 ---
    if node_layout.get("position") == "absolute":
        styles.append("position: absolute;")
        if "top" in node_layout: styles.append(f"top: {node_layout['top']}px;")
        if "left" in node_layout: styles.append(f"left: {node_layout['left']}px;")
    
    if "width" in node_style: styles.append(f"width: {node_style['width']}px;")
    if "height" in node_style: styles.append(f"height: {node_style['height']}px;")

    # --- Flex/Grid 布局 ---
    if node_layout.get("type") == "flex":
        styles.append("display: flex;")
        styles.append(f"flex-direction: {node_layout.get('direction', 'row')};")
        if "gap" in node_layout: styles.append(f"gap: {node_layout['gap']}px;")
    elif node_layout.get("type") == "grid":
        styles.append("display: grid;")
        styles.append(f"grid-template-columns: repeat({node_layout.get('columns', 1)}, 1fr);")
        if "h_gap" in node_layout: styles.append(f"column-gap: {node_layout['h_gap']}px;")
        if "v_gap" in node_layout: styles.append(f"row-gap: {node_layout['v_gap']}px;")

    # --- 背景、边框等样式 ---
    if "backgroundColor" in node_style:
        bg_color = node_style["backgroundColor"]
        if bg_color == "color-white": styles.append("background-color: #FFFFFF;")
        elif bg_color == "color-black": styles.append("background-color: #000000;")
        else: styles.append(f"background-color: {bg_color};")
    else:
        # 如果没有背景色，则根据层级应用一个调试颜色
        debug_color = DEBUG_COLORS[level % len(DEBUG_COLORS)]
        styles.append(f"background-color: {debug_color};")
    
    if "borderColor" in node_style and "borderWidth" in node_style:
        styles.append(f"border: {node_style['borderWidth']} solid {node_style['borderColor']};")
    else:
        # 为所有没有边框的元素添加一个细边框，以便观察
        styles.append("border: 1px solid rgba(0, 0, 0, 0.1);")

    if "borderRadius" in node_style:
        radius = node_style["borderRadius"]
        if isinstance(radius, str) and radius.endswith("px"):
             styles.append(f"border-radius: {radius};")
        else:
             styles.append(f"border-radius: {radius}px;")

    # 2. 递归处理子节点
    children_html = ""
    if children := node.get("children"):
        for child in children:
            children_html += dsl_node_to_html(child, level + 1) # 传递下一层级

    # 3. 组合成最终的 HTML 元素
    style_str = " ".join(styles)
    return f'<div data-name="{node.get("name", "Unnamed")}" style="{style_str}">{children_html}</div>'


def main():
    """主函数：读取 DSL JSON 并生成 HTML 文件。"""
    print(f"--- DSL to HTML Converter ---")
    try:
        with open(DSL_INPUT_FILE, "r", encoding="utf-8") as f:
            dsl_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 输入文件未找到: {DSL_INPUT_FILE}")
        return
    except json.JSONDecodeError:
        print(f"[ERROR] 输入文件不是有效的 JSON 格式或文件为空: {DSL_INPUT_FILE}")
        return

    if not dsl_data:
        print("[WARNING] DSL 文件为空，无法生成 HTML。")
        return

    # 将根节点转换为 HTML
    body_content = dsl_node_to_html(dsl_data, level=0) # 从第 0 层开始

    # 构建完整的 HTML 页面
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSL Preview</title>
    <style>
        body {{ margin: 0; font-family: sans-serif; }}
        div {{ box-sizing: border-box; }}
    </style>
</head>
<body>
{body_content}
</body>
</html>"""

    # 写入 HTML 文件
    try:
        with open(HTML_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[SUCCESS] HTML 文件已成功生成于: {HTML_OUTPUT_FILE}")
    except IOError as e:
        print(f"[ERROR] 无法写入 HTML 文件: {e}")


if __name__ == "__main__":
    main()
