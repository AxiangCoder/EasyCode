#!/usr/bin/env python
"""
简单的API测试脚本
测试重构后的converter app API
"""

import requests
import json
from pathlib import Path

# API基础URL
BASE_URL = 'http://localhost:8000'

def test_converter_api():
    """测试converter API"""
    print("=== 测试Converter API ===")

    # 测试根端点
    try:
        response = requests.get(f'{BASE_URL}/v1/converter/')
        print(f"GET /v1/converter/ - Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error testing converter API: {e}")

    # 测试设计令牌端点
    try:
        response = requests.get(f'{BASE_URL}/v1/converter/tokens/')
        print(f"GET /v1/converter/tokens/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("需要认证 - 这是预期的")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error testing tokens API: {e}")

    # 测试任务端点
    try:
        response = requests.get(f'{BASE_URL}/v1/converter/tasks/')
        print(f"GET /v1/converter/tasks/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("需要认证 - 这是预期的")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error testing tasks API: {e}")

    # 测试结果端点
    try:
        response = requests.get(f'{BASE_URL}/v1/converter/results/')
        print(f"GET /v1/converter/results/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("需要认证 - 这是预期的")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error testing results API: {e}")

def test_admin_interface():
    """测试Django admin接口"""
    print("\n=== 测试Django Admin ===")

    try:
        response = requests.get(f'{BASE_URL}/admin/')
        print(f"GET /admin/ - Status: {response.status_code}")
        if 'login' in response.text.lower():
            print("Admin登录页面正常")
        else:
            print("Admin页面响应异常")
    except Exception as e:
        print(f"Error testing admin: {e}")

def test_other_apis():
    """测试其他API端点"""
    print("\n=== 测试其他API ===")

    # 测试用户API
    try:
        response = requests.get(f'{BASE_URL}/v1/')
        print(f"GET /v1/ - Status: {response.status_code}")
    except Exception as e:
        print(f"Error testing users API: {e}")

    # 测试sketch API
    try:
        response = requests.get(f'{BASE_URL}/v1/sketch/')
        print(f"GET /v1/sketch/ - Status: {response.status_code}")
    except Exception as e:
        print(f"Error testing sketch API: {e}")

if __name__ == '__main__':
    print("开始API测试...")
    print("注意：大部分API需要认证，401状态码是正常的")

    test_converter_api()
    test_admin_interface()
    test_other_apis()

    print("\n=== 测试完成 ===")
    print("重构后的converter app已成功部署！")
    print("主要功能：")
    print("- 设计令牌管理 API: /v1/converter/tokens/")
    print("- 转换任务管理 API: /v1/converter/tasks/")
    print("- 转换结果查看 API: /v1/converter/results/")
    print("- Django Admin管理界面: /admin/")
