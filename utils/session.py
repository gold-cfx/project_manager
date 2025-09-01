#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户会话管理模块
管理当前登录用户的信息和状态
"""
from typing import Optional

from models.user import User, UserRole


class SessionManager:
    """用户会话管理器"""

    _current_user: Optional[User] = None

    @classmethod
    def set_current_user(cls, user: User) -> None:
        """设置当前登录用户"""
        cls._current_user = user

    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """获取当前登录用户"""
        return cls._current_user

    @classmethod
    def clear_current_user(cls) -> None:
        """清除当前用户会话"""
        cls._current_user = None

    @classmethod
    def is_logged_in(cls) -> bool:
        """检查是否有用户登录"""
        return cls._current_user is not None

    @classmethod
    def is_admin(cls) -> bool:
        """检查当前用户是否为管理员"""
        if not cls._current_user:
            return False
        return cls._current_user.role == UserRole.ADMIN.value
