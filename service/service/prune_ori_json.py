#!/usr/bin/env python3
"""Prune Sketch-style JSON files down to selected node attributes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import os


ALLOWED_KEYS = ("isVisible", "_class", "do_objectID", "name", "exportOptions", "exportFormats")


def prune_node(node: Any) -> Any:
    """Recursively retain only specified attributes for each node."""
    if isinstance(node, dict):
        pruned = {key: node[key] for key in ALLOWED_KEYS if key in node}

        if "layers" in node:
            layers = node["layers"]
            if isinstance(layers, list):
                pruned["layers"] = [prune_node(child) for child in layers]
            else:
                pruned["layers"] = layers

        return pruned

    if isinstance(node, list):
        return [prune_node(item) for item in node]

    return node

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

def main() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 文件路径
    input_file = os.path.join(current_dir, 'ori.json')
    output_file = os.path.join(current_dir, '_ori.json')
    input_nodes = load_json_file(input_file)

    pruned = prune_node(input_nodes)

    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pruned, f, ensure_ascii=False, indent=4)
        print(f"剪枝完成: {output_file}")
    except Exception as e:
        print(f"写入文件失败: {e}")

    print(f"Pruned JSON written to {output_file}")


if __name__ == "__main__":
    main()

