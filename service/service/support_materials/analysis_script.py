import json
from collections import defaultdict

def analyze_missing_nodes():
    # 1. Load data
    try:
        with open('_ori.json', 'r', encoding='utf-8') as f:
            sketch_data = json.load(f)
        with open('missing_nodes.json', 'r', encoding='utf-8') as f:
            missing_nodes_list = json.load(f)
    except FileNotFoundError as e:
        return f"Error: {e.filename} not found."
    except json.JSONDecodeError as e:
        return f"Error decoding JSON from {e.doc}: {e.msg}"

    # 2. Create a lookup map for quick access to nodes and their parents
    node_map = {}
    def build_map(node, parent=None):
        if isinstance(node, dict) and 'do_objectID' in node:
            node_map[node['do_objectID']] = {'node': node, 'parent': parent}
            if 'layers' in node and isinstance(node['layers'], list):
                for child in node['layers']:
                    build_map(child, node)
        elif isinstance(node, list):
            for item in node:
                build_map(item, parent)

    build_map(sketch_data)

    # 3. Initialize analysis results structure
    analysis = {
        "node_is_hidden": defaultdict(list),
        "parent_is_hidden": defaultdict(lambda: defaultdict(list)),
        "unsupported_class": defaultdict(lambda: defaultdict(list)),
        "unknown": defaultdict(list)
    }
    
    supported_classes = {
        "symbolInstance", "text", "group", "rectangle", "oval", "page",
        "artboard", "shapePath", "shapeGroup", "bitmap", "triangle"
    }


    # 4. Analyze each missing node
    for missing_node_info in missing_nodes_list:
        node_id = missing_node_info.get('do_objectID')
        if not node_id or node_id not in node_map:
            analysis["unknown"]["nodes_not_in_ori"].append(missing_node_info)
            continue

        map_entry = node_map[node_id]
        node = map_entry['node']
        parent = map_entry['parent']
        node_class = node.get('_class')

        # Reason 1: The node itself is hidden
        if not node.get('isVisible', True):
            analysis["node_is_hidden"][node_class].append(node_id)
            continue

        # Reason 2: The parent node is hidden
        if parent and not parent.get('isVisible', True):
            parent_id = parent.get('do_objectID')
            parent_class = parent.get('_class')
            key = f"`{parent_class}` (ID: `{parent_id}`)"
            analysis["parent_is_hidden"][key][node_class].append(node_id)
            continue
            
        # Reason 3: Unsupported class
        if node_class not in supported_classes:
            analysis["unsupported_class"][node_class]['nodes'].append(node_id)
            continue

        # Reason 4: Unknown
        analysis["unknown"][node_class].append(node_id)

    # 5. Generate Markdown Report
    report = ["# Missing Nodes Analysis Report"]

    total_missing = len(missing_nodes_list)
    report.append(f"\n**Total missing nodes analyzed: {total_missing}**\n")

    report.append("## 1. Reason: Node Itself is Hidden (`isVisible: false`)")
    hidden_self_total = sum(len(ids) for ids in analysis["node_is_hidden"].values())
    report.append(f"**Total Nodes: {hidden_self_total}**\n")
    if hidden_self_total > 0:
        for node_class, ids in sorted(analysis["node_is_hidden"].items()):
            report.append(f"- **`{node_class}`** (Count: {len(ids)})")
            report.append("  - Object IDs: `" + ", ".join(ids) + "`")
    else:
        report.append("No nodes were found to be missing because they were individually hidden.")
    report.append("\n---\n")

    report.append("## 2. Reason: Parent Node is Hidden")
    hidden_parent_total = sum(len(ids) for parent in analysis["parent_is_hidden"].values() for ids in parent.values())
    report.append(f"**Total Nodes: {hidden_parent_total}**\n")
    if hidden_parent_total > 0:
        for parent_key, children in sorted(analysis["parent_is_hidden"].items()):
            parent_total = sum(len(ids) for ids in children.values())
            report.append(f"### Parent: {parent_key}")
            report.append(f"- **Total Children Missing:** {parent_total}")
            for node_class, ids in sorted(children.items()):
                report.append(f"  - **`{node_class}`** (Count: {len(ids)})")
                report.append("    - Object IDs: `" + ", ".join(ids) + "`")
            report.append("")
    else:
        report.append("No nodes were found to be missing because their parent was hidden.")
    report.append("\n---\n")

    report.append("## 3. Reason: Unsupported Class")
    unsupported_total = sum(len(data['nodes']) for data in analysis["unsupported_class"].values())
    report.append(f"**Total Nodes: {unsupported_total}**\n")
    if unsupported_total > 0:
        for node_class, data in sorted(analysis["unsupported_class"].items()):
            report.append(f"- **`{node_class}`** (Count: {len(data['nodes'])})")
            report.append("  - Object IDs: `" + ", ".join(data['nodes']) + "`")
    else:
        report.append("No nodes were found to be missing due to having an unsupported class. The converter handles all classes found in the missing nodes list.")
    report.append("\n---\n")

    report.append("## 4. Reason: Unknown")
    unknown_total = sum(len(ids) for ids in analysis["unknown"].values())
    report.append(f"**Total Nodes: {unknown_total}**\n")
    if unknown_total > 0:
        report.append("These nodes and their parents are marked as visible, and their class is supported. The reason for their exclusion is not immediately clear from visibility or class checks. This may be due to edge cases in the conversion logic.\n")
        for node_class, ids in sorted(analysis["unknown"].items()):
            if node_class == "unknown_id":
                report.append("- **Nodes not found in _ori.json** (Count: {len(ids)})")
                report.append("  - These nodes from `missing_nodes.json` could not be found in `_ori.json` for analysis.")
            else:
                report.append(f"- **`{node_class}`** (Count: {len(ids)})")
                report.append("  - Object IDs: `" + ", ".join(ids) + "`")
    else:
        report.append("No nodes with unknown reasons for exclusion.")

    return "\n".join(report)

if __name__ == "__main__":
    result_markdown = analyze_missing_nodes()
    print(result_markdown)