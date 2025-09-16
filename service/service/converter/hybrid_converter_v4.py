
import json
import os
import time
from collections import defaultdict

# --- V4 配置项 ---
INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'media', 'sketches', 'output.json')
TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'design_tokens.json')
DSL_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'media', 'sketches', 'dsl_output_v4.json')
REPORT_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'media', 'sketches', 'token_report.json')

# --- 大模型 API 配置 ---
ENABLE_LLM_FALLBACK = True
LLM_API_KEY = "YOUR_OPENAI_API_KEY" # 在此填入你的 OpenAI API Key

# --- 辅助函数 ---
def convert_color_to_hex(color_obj):
    if not color_obj: return None
    r, g, b = int(color_obj.get('red', 0)*255), int(color_obj.get('green', 0)*255), int(color_obj.get('blue', 0)*255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()

# --- V4 核心功能 ---

def load_design_tokens():
    try:
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            print(f"[INFO] 成功加载设计令牌文件: {TOKENS_FILE}")
            return json.load(f)
    except FileNotFoundError: print(f"[WARNING] 设计令牌文件未找到: {TOKENS_FILE}。"); return {}
    except json.JSONDecodeError: print(f"[WARNING] 设计令牌文件格式错误。"); return {}

def preprocess_symbols(sketch_data):
    symbol_map = {}
    pages = sketch_data.get('layers', [sketch_data])
    for page in pages:
        if 'layers' not in page: continue
        for artboard in page['layers']:
            if artboard.get('_class') in ['artboard', 'symbolMaster']:
                for item in artboard.get('layers', []):
                    if item.get('_class') == 'symbolMaster': symbol_map[item.get('symbolID')] = item.get('name')
    print(f"[INFO] 预处理完成，找到 {len(symbol_map)} 个主元件(Symbols)。")
    return symbol_map

def parse_semantic_name(name):
    parts = name.split('/')
    if len(parts) < 2: return {'type': name, 'variant': 'default'}
    return {'category': parts[0], 'type': parts[1], 'variant': parts[2] if len(parts) > 2 else 'default', 'state': parts[3] if len(parts) > 3 else None}

def map_styles_to_tokens(layer, token_maps, report):
    if not token_maps: return {}
    dsl_style, style, layer_name = {}, layer.get('style', {}), layer.get('name', 'Unnamed')
    if (fills := style.get('fills')) and fills and fills[0].get('isEnabled'):
        hex_color = convert_color_to_hex(fills[0].get('color'))
        if hex_color:
            if token := token_maps.get('colors', {}).get(hex_color):
                dsl_style['backgroundColor'] = token
            else:
                print(f"[WARNING] 发现未令牌化的颜色: {hex_color} (应用于图层: '{layer_name}')")
                dsl_style['backgroundColor'] = hex_color; dsl_style['untokenized'] = True
                report["unknown_colors"][hex_color] = report["unknown_colors"].get(hex_color, []) + [layer_name]
    if (text_style := style.get('textStyle')):
        attrs = text_style.get('encodedAttributes', {})
        font_attrs = attrs.get('MSAttributedStringFontAttribute', {}).get('attributes', {})
        font_name, font_size = font_attrs.get('name'), font_attrs.get('size')
        if font_name and font_size:
            font_key = f"{font_name}-{int(font_size)}"
            if token := token_maps.get('fonts', {}).get(font_key):
                dsl_style['font'] = token
            else:
                print(f"[WARNING] 发现未令牌化的字体: '{font_key}' (应用于图层: '{layer_name}')")
                report["unknown_fonts"][font_key] = report["unknown_fonts"].get(font_key, []) + [layer_name]
    return dsl_style

def traverse_layer(layer, symbol_map, token_maps, report):
    """(V4) 递归遍历图层树，生成语义化 DSL 结构"""
    if not layer or not layer.get('isVisible', True): return None
    layer_class = layer.get('_class')

    if layer_class == 'symbolInstance':
        symbol_id = layer.get('symbolID')
        semantic_name = symbol_map.get(symbol_id, layer.get('name'))
        parsed_name = parse_semantic_name(semantic_name)
        node = {
            "type": parsed_name.get('type', 'UnknownComponent"), "variant": parsed_name.get('variant'),
            "name": layer.get('name'), "frame": layer.get('frame'),
            "style": map_styles_to_tokens(layer, token_maps, report), "children": []
        }
        if overrides := layer.get('overrideValues'):
            for override in overrides:
                if 'stringValue' in override and override['stringValue']:
                    node['content'] = {'text': override['stringValue']}; break
        return node

    elif layer_class == 'text':
        return {
            "type": 'Text', "name": layer.get('name'), "frame": layer.get('frame'),
            "content": {'text': layer.get('stringValue')},
            "style": map_styles_to_tokens(layer, token_maps, report), "children": []
        }

    elif layer_class == 'group' and layer.get('layers'):
        layout_info = analyze_layout_with_rules(layer['layers'])
        if layout_info['type'] == 'absolute' and ENABLE_LLM_FALLBACK:
            layout_info = analyze_layout_with_llm(layer['layers'])
        children_nodes = [child_node for child in layer['layers'] if (child_node := traverse_layer(child, symbol_map, token_maps, report))]
        return {
            "type": 'Group', "name": layer.get('name', 'Unnamed Group'), "frame": layer.get('frame'),
            "layout": layout_info, "children": children_nodes
        }
    else:
        return None

def write_token_report(report):
    if not report["unknown_colors"] and not report["unknown_fonts"]:
        print("[INFO] 设计系统检查通过，未发现未知令牌。"); return
    summary = f"发现 {len(report['unknown_colors'])} 个未知颜色和 {len(report['unknown_fonts'])} 个未知字体。请与设计师确认并更新 design_tokens.json。"
    report_data = {"summary": summary, **report}
    print(f"[ACTION] 检测到未知令牌，正在生成报告文件: {REPORT_OUTPUT_FILE}")
    try:
        with open(REPORT_OUTPUT_FILE, 'w', encoding='utf-8') as f: json.dump(report_data, f, ensure_ascii=False, indent=4)
    except IOError as e: print(f"[ERROR] 无法写入报告文件: {e}")

def main():
    print("--- Sketch-to-DSL Converter V4 (Guardian & Resilient) ---")
    token_maps, report = load_design_tokens(), {"unknown_colors": {}, "unknown_fonts": {}}
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f: sketch_data = json.load(f)
    except FileNotFoundError: print(f"[ERROR] 输入文件未找到: {INPUT_FILE}"); return
    except json.JSONDecodeError: print("[ERROR] 输入文件不是有效的 JSON 格式。"); return

    symbol_map = preprocess_symbols(sketch_data)
    print("开始转换 (语义化模式)...")
    dsl_output = traverse_layer(sketch_data, symbol_map, token_maps, report)
    print(f"转换完成，正在写入 DSL 文件: {DSL_OUTPUT_FILE}")
    try:
        with open(DSL_OUTPUT_FILE, 'w', encoding='utf-8') as f: json.dump(dsl_output, f, ensure_ascii=False, indent=4)
        print(f"成功！V4 版本的 DSL 文件已生成于 {DSL_OUTPUT_FILE}")
    except IOError as e: print(f"[ERROR] 无法写入 DSL 文件: {e}")
    write_token_report(report)

# --- 布局分析函数 ---
def analyze_layout_with_rules(layers):
    if not layers or len(layers) < 2: return {'type': 'absolute'}
    layers.sort(key=lambda l: (l['frame']['y'], l['frame']['x']))
    rows = defaultdict(list)
    for layer in layers: next((r for k, r in rows.items() if abs(layer['frame']['y'] - k) < 10), rows[layer['frame']['y']]).append(layer)
    num_rows, items_per_row = len(rows), [len(r) for r in rows.values()]
    if num_rows > 1 and len(set(items_per_row)) == 1 and items_per_row[0] > 1:
        cols = items_per_row[0]
        h_gaps = [r[i+1]['frame']['x'] - (r[i]['frame']['x'] + r[i]['frame']['width']) for r in rows.values() for i in range(len(r)-1) if r[i+1]['frame']['x'] > (r[i]['frame']['x'] + r[i]['frame']['width'])]
        v_gaps = [list(rows.values())[i+1][0]['frame']['y'] - (list(rows.values())[i][0]['frame']['y'] + list(rows.values())[i][0]['frame']['height']) for i in range(num_rows-1) if list(rows.values())[i+1][0]['frame']['y'] > (list(rows.values())[i][0]['frame']['y'] + list(rows.values())[i][0]['frame']['height'])]
        return {'type': 'grid', 'columns': cols, 'h_gap': round(sum(h_gaps)/len(h_gaps)) if h_gaps else 0, 'v_gap': round(sum(v_gaps)/len(v_gaps)) if v_gaps else 0}
    if num_rows == 1 and items_per_row[0] > 1:
        gaps = [layers[i+1]['frame']['x'] - (layers[i]['frame']['x'] + layers[i]['frame']['width']) for i in range(len(layers)-1)]
        return {'type': 'flex', 'direction': 'row', 'gap': round(sum(gaps)/len(gaps)) if gaps else 0}
    if items_per_row and items_per_row[0] == 1 and num_rows > 1:
        gaps = [layers[i+1]['frame']['y'] - (layers[i]['frame']['y'] + layers[i]['frame']['height']) for i in range(len(layers)-1)]
        return {'type': 'flex', 'direction': 'column', 'gap': round(sum(gaps)/len(gaps)) if gaps else 0}
    return {'type': 'absolute'}

def analyze_layout_with_llm(layers):
    """(V4) 调用 OpenAI 模型进行布局分析，包含重试和精简数据逻辑"""
    print(f"\n[INFO] 规则分析失败，正在调用 OpenAI 模型分析 {len(layers)} 个图层...")
    if not LLM_API_KEY or "YOUR_OPENAI_API_KEY" in LLM_API_KEY: print("[WARNING] OpenAI API Key 未配置。跳过。 "); return {'type': 'absolute'}
    
    simplified_layers = []
    for l in layers:
        frame = l.get('frame', {})
        simplified_layers.append({
            'name': l.get('name'), 'class': l.get('_class'),
            'frame': {'x': round(frame.get('x',0)), 'y': round(frame.get('y',0)), 'w': round(frame.get('width',0)), 'h': round(frame.get('height',0))}
        })

    prompt = f"""Analyze the layout of the following JSON array of Sketch layers... Layers data: {json.dumps(simplified_layers, indent=2)}"""

    for attempt in range(3):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=LLM_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You are an expert assistant... Respond ONLY with a single, clean JSON object."}, {"role": "user", "content": prompt}],
                temperature=0.1, response_format={"type": "json_object"}
            )
            layout_info = json.loads(response.choices[0].message.content)
            print(f"[INFO] OpenAI 分析成功: {layout_info}")
            return layout_info
        except Exception as e:
            print(f"[WARNING] API 调用尝试 {attempt + 1}/3 失败: {e}")
            if attempt < 2: time.sleep(2) # 等待2秒后重试
            else: print(f"[ERROR] OpenAI API 调用在3次尝试后彻底失败。"); return {'type': 'absolute'}
    return {'type': 'absolute'}

if __name__ == '__main__':
    main()
