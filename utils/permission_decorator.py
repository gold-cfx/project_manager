#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限验证装饰器
提供管理员权限验证功能
"""
import functools
from typing import Callable, Any

from PyQt5.QtWidgets import QMessageBox

from utils.session import SessionManager


def admin_required(func: Callable) -> Callable:
    """
    管理员权限验证装饰器
    
    使用方法：
    @admin_required
    def delete_something(self, ...):
        # 只有管理员才能执行的操作
        pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # 获取当前用户
        current_user = SessionManager.get_current_user()

        if not current_user:
            QMessageBox.warning(
                args[0] if args else None,
                '未登录',
                '请先登录系统'
            )
            return None

        # 检查是否为管理员
        if not current_user.is_admin:
            QMessageBox.warning(
                args[0] if args else None,
                '权限不足',
                '只有管理员才能执行此操作'
            )
            return None

        # 是管理员，执行原函数
        return func(*args, **kwargs)

    return wrapper


def admin_required_with_confirm(message: str = "确定要执行此删除操作吗？"):
    """
    管理员权限验证装饰器（带确认对话框）
    
    使用方法：
    @admin_required_with_confirm("确定要删除这个项目吗？")
    def delete_project(self, project_id):
        pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 获取当前用户
            current_user = SessionManager.get_current_user()

            if not current_user:
                QMessageBox.warning(
                    args[0] if args else None,
                    '未登录',
                    '请先登录系统'
                )
                return None

            # 检查是否为管理员
            if not current_user.is_admin:
                QMessageBox.warning(
                    args[0] if args else None,
                    '权限不足',
                    '只有管理员才能执行此操作'
                )
                return None

            # 显示确认对话框
            reply = QMessageBox.question(
                args[0] if args else None,
                '确认操作',
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return None

            # 确认后继续执行
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin_permission():
    """
    检查当前用户是否具有管理员权限
    
    使用示例：
    if not require_admin_permission():
        raise PermissionError("只有管理员才能执行此操作")
    """
    current_user = SessionManager.get_current_user()
    if not current_user or not current_user.is_admin:
        return False
    return True
