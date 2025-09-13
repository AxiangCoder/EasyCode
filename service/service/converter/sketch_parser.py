import json
from typing import Dict, Any

def load_sketch(sketch_file):
    with open(sketch_file, 'r') as f:
        sketch = f.read()
    return json.loads(sketch)

def filter_sketch_data(data):
    """
    递归地过滤 Sketch JSON 字典，只保留必要的属性。

    该函数会检查 'isVisible' 键，并过滤掉任何隐藏的对象。
    它保留了一组预定义的属性，包括 '_class'、'name'、'frame'、
    'rotation'、'layers'，以及整个 'style' 字典。

    参数:
        data (dict or list): Sketch JSON 数据，已作为 Python 字典加载。

    返回:
        dict or list: 包含过滤后数据的新字典或列表。
    """
    # 需要保留在最终输出中的键
    keys_to_keep = {'_class', 'name', 'frame', 'rotation', 'layers', 'style', 'do_objectID'}
    # 在 'frame' 字典中需要保留的键
    frame_keys_to_keep = {'height', 'width', 'x', 'y'}
    # 包含需要递归过滤的列表的键
    list_keys = {'layers'}

    # 如果数据是列表，则处理列表中的每个项目
    if isinstance(data, list):
        filtered_list = []
        for item in data:
            result = filter_sketch_data(item)
            # 如果过滤结果不为空，则添加到列表中
            if result:
                filtered_list.append(result)
        return filtered_list

    # 如果数据是字典，则处理其键和值
    elif isinstance(data, dict):
        # 检查 'isVisible' 属性。如果存在且为 False，返回一个空字典以将其过滤掉。
        if 'isVisible' in data and not data['isVisible']:
            return {}

        filtered_dict = {}
        for key, value in data.items():
            if key == 'style':
                # 特殊处理 'style' 字段，递归保留其所有内容
                filtered_dict[key] = value
            # 过滤顶层键
            elif key in keys_to_keep:
                if key == 'frame' and isinstance(value, dict):
                    # 过滤 'frame' 字典，只保留指定的键
                    filtered_frame = {k: v for k, v in value.items() if k in frame_keys_to_keep}
                    filtered_dict[key] = filtered_frame
                elif key in list_keys and isinstance(value, list):
                    # 递归过滤图层列表
                    filtered_dict[key] = filter_sketch_data(value)
                elif isinstance(value, dict):
                    # 递归过滤其他嵌套的字典
                    filtered_dict[key] = filter_sketch_data(value)
                elif key == 'do_objectID':
                    filtered_dict['id'] = value
                else:
                    # 保留其他简单的键和它们的值
                    filtered_dict[key] = value
        return filtered_dict
    else:
        # 对于非字典/列表类型，按原样返回其值
        return data

