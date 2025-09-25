
def convert_color_to_hex(color_obj):
    """Converts a Sketch color object to a HEX string."""
    if not color_obj:
        return None
    r = int(color_obj.get("red", 0) * 255)
    g = int(color_obj.get("green", 0) * 255)
    b = int(color_obj.get("blue", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()

def parse_semantic_name(name):
    """Parses a semantic name like 'component/button/primary' into a dict."""
    parts = name.split("/")
    if len(parts) < 2:
        return {"type": name, "variant": "default"}
    return {
        "category": parts[0],
        "type": parts[1],
        "variant": parts[2] if len(parts) > 2 else "default",
        "state": parts[3] if len(parts) > 3 else None,
    }

# 判断是否是导出节点（切图）
def is_export (node):
    exportOptions = node.get("exportOptions", {})
    len_num = len(exportOptions.get("exportFormats", []))
    return  len_num > 0

def sum_nodes (node, mode = "all"):
    if not isinstance(node, dict):
        raise (TypeError, "node must be a dictionary")
    count = 0
    if mode == "all":
        count += 1
        if not is_export(node):
            count += sum([sum_nodes(item, mode) for item in node.get("layers", [])])

    else:
        def count_hidden_nodes(node):
            count = len(node.get("layers", []))
            if count == 0:
                return  count
            count += sum([count_hidden_nodes(item) for item in node.get("layers", [])])
            return count
        if node.get("isVisible", True):
            if not is_export(node):
                count += sum([sum_nodes(item, mode) for item in node.get("layers", [])])
        else:
            print(node.get("do_objectID"))
            print(node.get("isVisible", True))
            count += 1
            if not is_export(node):
                count += sum([count_hidden_nodes(item) for item in node.get("layers", [])])
    return count
