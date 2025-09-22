#!/usr/bin/env python
"""
错误处理测试脚本
用于验证自定义异常处理器和错误响应格式
"""

import os
import sys
import django
from django.test import TestCase
from django.test.client import Client
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
django.setup()

from converter.exceptions import TaskNotFoundError, ConversionError


class ErrorHandlingTest(APITestCase):
    """错误处理测试"""

    def setUp(self):
        """测试设置"""
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_custom_exception_response_format(self):
        """测试自定义异常响应格式"""
        # 尝试访问不存在的任务
        url = reverse('conversiontask-detail', kwargs={'pk': '999999'})
        response = self.client.get(url)

        # 验证响应格式
        self.assertEqual(response.status_code, 404)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)
        self.assertIn('timestamp', response.data)
        self.assertIn('path', response.data)

        # 验证错误结构
        error = response.data['error']
        self.assertIn('code', error)
        self.assertIn('message', error)
        self.assertIn('details', error)

    def test_validation_error_format(self):
        """测试验证错误响应格式"""
        # 发送无效数据
        url = reverse('conversiontask-list')
        invalid_data = {
            'name': '',  # 空名称
            'input_file': '',  # 空文件
        }

        response = self.client.post(url, invalid_data)

        # 验证响应格式
        self.assertEqual(response.status_code, 400)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_success_response_format(self):
        """测试成功响应格式"""
        # 获取任务列表
        url = reverse('conversiontask-list')
        response = self.client.get(url)

        # 验证响应格式
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])

    def test_exception_structure(self):
        """测试异常结构"""
        # 创建自定义异常
        exc = TaskNotFoundError("123")
        self.assertEqual(exc.code, "TASK_NOT_FOUND")
        self.assertEqual(exc.message, "转换任务不存在: 123")
        self.assertEqual(exc.details['task_id'], "123")

        exc2 = ConversionError("转换失败", step="test", task_id="456")
        self.assertEqual(exc2.code, "CONVERSION_ERROR")
        self.assertEqual(exc2.details['step'], "test")
        self.assertEqual(exc2.details['task_id'], "456")


def run_tests():
    """运行测试"""
    print("开始运行错误处理测试...")

    # 创建测试实例
    test_instance = ErrorHandlingTest()
    test_instance.setUp()

    # 运行测试
    try:
        test_instance.test_custom_exception_response_format()
        print("✅ 自定义异常响应格式测试通过")

        test_instance.test_validation_error_format()
        print("✅ 验证错误响应格式测试通过")

        test_instance.test_success_response_format()
        print("✅ 成功响应格式测试通过")

        test_instance.test_exception_structure()
        print("✅ 异常结构测试通过")

        print("\n🎉 所有错误处理测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
