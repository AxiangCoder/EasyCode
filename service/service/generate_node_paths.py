#!/usr/bin/env python3
"""
脚本用于从 missing_nodes.json 中的节点向上遍历到根节点，
并生成 Markdown 格式的路径文档。
"""

import json
import os
from typing import List, Dict, Any, Optional


def load_json_file(file_path: str) -> Any:
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"错误：解析 JSON 文件 {file_path} 失败: {e}")
        return None


def find_node_by_id(nodes: List[Dict], node_id: str) -> Optional[Dict]:
    """在节点列表中查找指定 ID 的节点"""
    for node in nodes:
        if node.get('do_objectID') == node_id:
            return node
        # 如果节点有子节点，递归查找
        if 'layers' in node:
            found = find_node_by_id(node['layers'], node_id)
            if found:
                return found
    return None


def get_parent_node(nodes: List[Dict], target_node_id: str, parent_path: List[str] = None) -> Optional[List[str]]:
    """递归查找目标节点的父节点路径"""
    if parent_path is None:
        parent_path = []
    
    for node in nodes:
        current_path = parent_path + [node['do_objectID']]
        
        # 如果找到目标节点，返回路径
        if node.get('do_objectID') == target_node_id:
            return current_path
        
        # 如果当前节点有子节点，递归查找
        if 'layers' in node:
            result = get_parent_node(node['layers'], target_node_id, current_path)
            if result:
                return result
    
    return None


def find_node_path_in_data(data: Dict, target_node_id: str, path: List[str] = None) -> Optional[List[str]]:
    """在整个数据结构中递归查找节点路径"""
    if path is None:
        path = []
    
    # 检查当前节点
    if data.get('do_objectID') == target_node_id:
        return path + [data['do_objectID']]
    
    # 检查子节点
    if 'layers' in data:
        for layer in data['layers']:
            result = find_node_path_in_data(layer, target_node_id, path + [data['do_objectID']])
            if result:
                return result
    
    return None


def traverse_to_root(ori_data: Dict, missing_node_id: str) -> List[str]:
    """从缺失节点向上遍历到根节点"""
    return find_node_path_in_data(ori_data, missing_node_id) or []


def generate_markdown_paths(missing_nodes: List[Dict], ori_data: Dict) -> str:
    """生成 Markdown 格式的路径文档"""
    markdown_content = []
    markdown_content.append("# 节点路径分析报告\n")
    markdown_content.append("本文档显示了从缺失节点到根节点的完整路径。\n")
    
    found_count = 0
    total_count = len(missing_nodes)
    
    for missing_node in missing_nodes:
        node_id = missing_node.get('do_objectID')
        node_name = missing_node.get('name', 'Unknown')
        node_class = missing_node.get('_class', 'Unknown')
        
        # 向上遍历到根节点
        path = traverse_to_root(ori_data, node_id)
        
        if path:
            found_count += 1
            # 路径已经是正确的顺序（从根节点到目标节点），不需要反转
            # 生成路径字符串
            path_string = " - ".join(path)
            markdown_content.append(f"```\n{path_string}\n```\n")
        else:
            markdown_content.append(f"```\n未找到节点 {node_id} ({node_name}) 的路径\n```\n")
    
    # 添加统计信息
    markdown_content.append(f"\n## 统计信息\n")
    markdown_content.append(f"- 总节点数: {total_count}\n")
    markdown_content.append(f"- 找到路径的节点数: {found_count}\n")
    markdown_content.append(f"- 未找到路径的节点数: {total_count - found_count}\n")
    
    return "\n".join(markdown_content)


def main():
    """主函数"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 文件路径
    missing_nodes_file = os.path.join(current_dir, 'missing_nodes.json')
    ori_file = os.path.join(current_dir, 'ori.json')
    output_file = os.path.join(current_dir, 'node_paths_analysis.md')
    
    print("正在加载数据...")
    
    # 加载缺失节点数据
    missing_nodes = load_json_file(missing_nodes_file)
    if missing_nodes is None:
        return
    
    # 加载原始数据
    ori_data = load_json_file(ori_file)
    if ori_data is None:
        return
    
    print(f"找到 {len(missing_nodes)} 个缺失节点")
    
    # 生成 Markdown 内容
    print("正在生成路径分析...")
    markdown_content = generate_markdown_paths(missing_nodes, ori_data)
    
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"路径分析报告已生成: {output_file}")
    except Exception as e:
        print(f"写入文件失败: {e}")


if __name__ == "__main__":
    main()
