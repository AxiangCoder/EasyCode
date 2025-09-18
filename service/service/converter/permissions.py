from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View
from typing import Any


class IsOwnerOrReadOnly(BasePermission):
    """只允许创建者修改"""
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.creator == request.user


class CanConvertDesign(BasePermission):
    """检查用户是否有转换权限"""
    def has_permission(self, request: Request, view: View) -> bool:
        # 检查用户是否是活跃用户
        return request.user and request.user.is_active


class CanManageDesignTokens(BasePermission):
    """检查用户是否有管理设计令牌的权限"""
    def has_permission(self, request: Request, view: View) -> bool:
        # 只有活跃用户才能管理设计令牌
        return request.user and request.user.is_active

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # 只允许创建者或管理员修改
        return obj.creator == request.user or request.user.is_superuser


class CanViewConversionResults(BasePermission):
    """检查用户是否有查看转换结果的权限"""
    def has_permission(self, request: Request, view: View) -> bool:
        return request.user and request.user.is_active

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        # 用户只能查看自己创建的任务结果
        return obj.task.creator == request.user or request.user.is_superuser


class IsAdminOrOwner(BasePermission):
    """管理员或所有者权限"""
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.user.is_superuser:
            return True
        return obj.creator == request.user
