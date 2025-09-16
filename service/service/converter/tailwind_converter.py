
import json
import os
from collections import defaultdict

# --- 配置项 ---
INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'media', 'sketches', 'output.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'media', 'sketches', 'tailwind_output.json')
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# --- 核心转换逻辑 ---

def is_svg_group(layer):
    """
    判断一个图层组是否应该被视为一个 SVG。
    规则：如果一个组内主要由矢量图形构成，并且不包含文本(text)或位图(bitmap)，
    我们就认为它是一个适合被当作 SVG 处理的矢量组合。
    """
    if not layer or layer.get('_class') != 'group' or not layer.get('layers'):
        return False

    # 启发式规则：如果图层名包含“插画”，直接认为是SVG
    if '插画' in layer.get('name', ''):
        return True

    layers = layer['layers']
    has_vector_shapes = False
    has_non_vector_elements = False

    for child in layers:
        child_class = child.get('_class')
        if child_class in ['shapePath', 'shapeGroup', 'rectangle', 'oval', 'star', 'polygon', 'triangle']:
            has_vector_shapes = True
        elif child_class in ['text', 'bitmap']:
            has_non_vector_elements = True
            break

    return has_vector_shapes and not has_non_vector_elements

def convert_color_to_hex(color_obj):
    """将 Sketch 的 color 对象转换为十六进制颜色字符串"""
    if not color_obj or 'red' not in color_obj or 'green' not in color_obj or 'blue' not in color_obj:
        return ""
    r, g, b = int(color_obj['red'] * 255), int(color_obj['green'] * 255), int(color_obj['blue'] * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_background_style(layer):
    """从 layer 的 fills 属性中提取背景样式"""
    if (fills := layer.get('style', {}).get('fills')):
        for fill in reversed(fills):
            if fill.get('isEnabled'):
                if color_hex := convert_color_to_hex(fill.get('color')):
                    return f"bg-[{color_hex}]"
    return ""

def get_border_style(layer):
    """提取边框和圆角样式"""
    styles = []
    style_obj = layer.get('style', {})
    
    if (borders := style_obj.get('borders')):
        for border in reversed(borders):
            if border.get('isEnabled'):
                thickness = border.get('thickness', 1)
                if color_hex := convert_color_to_hex(border.get('color')):
                    styles.append(f"border-[{thickness}px] border-[{color_hex}]")
                break
    
    if layer.get('_class') == 'rectangle' and (fixed_radius := layer.get('fixedRadius', 0)) > 0:
        styles.append(f"rounded-[{fixed_radius}px]")
    elif layer.get('_class') == 'rectangle' and (path_points := layer.get('path', {}).get('points')):
        radii = [p.get('cornerRadius', 0) for p in path_points]
        if radii and all(r == radii[0] for r in radii) and radii[0] > 0:
            styles.append(f"rounded-[{radii[0]}px]")

    return " ".join(styles)

def analyze_layout(layers):
    """分析子元素的布局特征 (Grid, Flex, or Absolute)"""
    if not layers or len(layers) < 2:
        return {'type': 'absolute'}

    layers.sort(key=lambda l: (l['frame']['y'], l['frame']['x']))

    rows = defaultdict(list)
    y_threshold = 10
    for layer in layers:
        found_row = False
        for y_key in rows:
            if abs(layer['frame']['y'] - y_key) < y_threshold:
                rows[y_key].append(layer)
                found_row = True
                break
        if not found_row:
            rows[layer['frame']['y']].append(layer)

    num_rows = len(rows)
    items_per_row = [len(r) for r in rows.values()]
    
    if num_rows > 1 and len(set(items_per_row)) == 1 and items_per_row[0] > 1:
        cols = items_per_row[0]
        h_gaps, v_gaps = [], []
        row_items = list(rows.values())
        
        for row in row_items:
            for i in range(len(row) - 1):
                gap = row[i+1]['frame']['x'] - (row[i]['frame']['x'] + row[i]['frame']['width'])
                if gap > 0: h_gaps.append(gap)
        
        sorted_rows = sorted(rows.items())
        for i in range(len(sorted_rows) - 1):
            y1, row1 = sorted_rows[i]
            y2, _ = sorted_rows[i+1]
            gap = y2 - (y1 + row1[0]['frame']['height'])
            if gap > 0: v_gaps.append(gap)

        return {
            'type': 'grid', 'cols': cols,
            'h_gap': round(sum(h_gaps) / len(h_gaps)) if h_gaps else 0,
            'v_gap': round(sum(v_gaps) / len(v_gaps)) if v_gaps else 0
        }

    if num_rows == 1 and items_per_row[0] > 1:
        gaps = [layers[i+1]['frame']['x'] - (layers[i]['frame']['x'] + layers[i]['frame']['width']) for i in range(len(layers) - 1)]
        return {'type': 'flex-row', 'gap': round(sum(gaps) / len(gaps)) if gaps else 0}

    if items_per_row and items_per_row[0] == 1 and num_rows > 1:
        gaps = [layers[i+1]['frame']['y'] - (layers[i]['frame']['y'] + layers[i]['frame']['height']) for i in range(len(layers) - 1)]
        return {'type': 'flex-col', 'gap': round(sum(gaps) / len(gaps)) if gaps else 0}

    return {'type': 'absolute'}

def traverse_layer(layer, parent_layout_type='absolute'):
    """递归遍历图层树，生成最终的 JSON 结构"""
    if not layer or not layer.get('isVisible', True):
        return None

    styles, children_nodes = [], []
    node_ele, src = "div", None

    layer_class = layer.get('_class')
    
    if is_svg_group(layer):
        node_ele = "svg"
    elif layer_class == 'bitmap':
        node_ele = "img"
        src = layer.get('image', {}).get('_ref', '')
    elif layer_class == 'group' and layer.get('layers'):
        layout_info = analyze_layout(layer['layers'])
        
        if layout_info['type'] == 'grid':
            cols = layout_info['cols']
            styles.append(f"grid grid-cols-1 md:grid-cols-{cols}")
            if layout_info.get('h_gap') == layout_info.get('v_gap') and layout_info.get('h_gap', 0) > 0:
                styles.append(f"gap-[{layout_info['h_gap']}px]")
            else:
                if layout_info.get('h_gap', 0) > 0: styles.append(f"gap-x-[{layout_info['h_gap']}px]")
                if layout_info.get('v_gap', 0) > 0: styles.append(f"gap-y-[{layout_info['v_gap']}px]")
        elif layout_info['type'] == 'flex-row':
            styles.append("flex flex-col md:flex-row")
            if layout_info.get('gap', 0) > 0: styles.append(f"gap-[{layout_info['gap']}px]")
        elif layout_info['type'] == 'flex-col':
            styles.append("flex flex-col")
            if layout_info.get('gap', 0) > 0: styles.append(f"gap-[{layout_info['gap']}px]")
        
        for child in layer['layers']:
            if child_node := traverse_layer(child, layout_info['type']):
                children_nodes.append(child_node)
    
    frame = layer.get('frame', {})
    width, height = frame.get('width'), frame.get('height')

    if parent_layout_type == 'absolute' or node_ele in ['svg', 'img']:
        if width: styles.append(f"w-[{round(width)}px]")
        if height: styles.append(f"h-[{round(height)}px]")

    if parent_layout_type == 'absolute':
        x, y = frame.get('x', 0), frame.get('y', 0)
        styles.append(f"absolute left-[{round(x)}px] top-[{round(y)}px]")

    if bg_style := get_background_style(layer): styles.append(bg_style)
    if border_style := get_border_style(layer): styles.append(border_style)
    if any(s.startswith("p-") for s in styles): styles.append("box-border")

    node = {"ele": node_ele, "style": " ".join(styles)}
    if src: node["src"] = src
    if children_nodes: node["children"] = children_nodes

    return node

def main():
    """主函数"""
    print(f"正在读取输入文件: {INPUT_FILE}")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            sketch_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 输入文件未找到 at {INPUT_FILE}")
        return
    except json.JSONDecodeError:
        print("错误: 输入文件不是有效的 JSON 格式。")
        return

    print("开始转换...")
    tailwind_json = traverse_layer(sketch_data)
    print(f"转换完成，正在写入输出文件: {OUTPUT_FILE}")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(tailwind_json, f, ensure_ascii=False, indent=4)
        print("成功！")
    except IOError as e:
        print(f"错误: 无法写入文件 at {OUTPUT_FILE}. {e}")

if __name__ == '__main__':
    main()
