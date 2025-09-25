
import json

def find_missing_nodes(dsl_file, ori_file):
    with open(dsl_file, 'r') as f:
        dsl_data = json.load(f)
    with open(ori_file, 'r') as f:
        ori_data = json.load(f)

    def get_all_ids(node):
        ids = set()
        if isinstance(node, dict):
            if "do_objectID" in node:
                ids.add(node["do_objectID"])
            if "children" in node:
                for child in node["children"]:
                    ids.update(get_all_ids(child))
            if "layers" in node:
                for layer in node["layers"]:
                    ids.update(get_all_ids(layer))
        elif isinstance(node, list):
            for item in node:
                ids.update(get_all_ids(item))
        return ids

    dsl_ids = get_all_ids(dsl_data)
    ori_ids = get_all_ids(ori_data)

    missing_ids = ori_ids - dsl_ids

    missing_nodes = []

    def find_nodes_by_ids(node, ids):
        if isinstance(node, dict):
            if node.get("do_objectID") in ids and not node.get("isVisible") is False:
                missing_nodes.append(
                    {
                        "do_objectID": node.get("do_objectID"),
                        "_class": node.get("_class"),
                        "name": node.get("name"),
                    }
                )
            if "children" in node:
                for child in node["children"]:
                    find_nodes_by_ids(child, ids)
            if "layers" in node:
                for layer in node["layers"]:
                    find_nodes_by_ids(layer, ids)
        elif isinstance(node, list):
            for item in node:
                find_nodes_by_ids(item, ids)

    find_nodes_by_ids(ori_data, missing_ids)

    return missing_nodes


missing_nodes = find_missing_nodes('dsl.json', '_ori.json')

for node in missing_nodes:
    print(f"缺少节点：do_objectID: {node['do_objectID']}, _class: {node['_class']}, name: {node['name']}")

with open('missing_nodes.json', 'w') as f:
    json.dump(missing_nodes, f, ensure_ascii=False, indent=4)

print(f"\n总共缺少 {len(missing_nodes)} 个节点。")
