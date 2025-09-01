#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 用户业务逻辑
"""
from typing import List, Optional

from models.user import User, UserCreate, UserUpdate
from data.user_dao import UserDAO
from utils.decorators import log_operation, validate_model_data


class UserLogic:
    """用户业务逻辑类"""

    def __init__(self):
        self.user_dao = UserDAO()

    @validate_model_data(UserCreate)
    @log_operation("创建用户")
    def create_user(self, user_data: UserCreate) -> bool:
        """创建用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            bool: 创建是否成功
        """
        # 检查用户名是否已存在
        if UserDAO.is_username_exists(user_data.username):
            raise ValueError(f"用户名 '{user_data.username}' 已存在")
            
        user_id = UserDAO.create_user(user_data)
        return user_id is not None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户登录认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 认证成功返回用户信息，失败返回None
        """
        if not username or not password:
            raise ValueError("用户名和密码不能为空")
            
        return UserDAO.authenticate_user(username, password)

    @log_operation("更新用户")
    def update_user(self, user_id: int, user_data: UserUpdate) -> bool:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            
        Returns:
            bool: 更新是否成功
        """
        # 检查用户是否存在
        existing_user = UserDAO.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"用户ID {user_id} 不存在")
            
        return UserDAO.update_user(user_id, user_data)

    @log_operation("删除用户")
    def delete_user(self, user_id: int) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        # 不能删除最后一个管理员
        user = UserDAO.get_user_by_id(user_id)
        if user and user.role == "admin":
            admin_count = len([u for u in UserDAO.get_all_users() if u.role == "admin"])
            if admin_count <= 1:
                raise ValueError("不能删除最后一个管理员用户")
                
        return UserDAO.delete_user(user_id)

    def get_all_users(self) -> List[User]:
        """获取所有用户
        
        Returns:
            List[User]: 用户列表
        """
        return UserDAO.get_all_users()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据用户ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户信息
        """
        return UserDAO.get_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户信息
        """
        if not username:
            raise ValueError("用户名不能为空")
        return UserDAO.get_user_by_username(username)

    def is_admin(self, user_id: int) -> bool:
        """检查用户是否为管理员
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否为管理员
        """
        user = UserDAO.get_user_by_id(user_id)
        return user is not None and user.role == "admin"

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 修改是否成功
        """
        user = UserDAO.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
            
        # 验证旧密码
        auth_user = UserDAO.authenticate_user(user.username, old_password)
        if not auth_user:
            raise ValueError("旧密码错误")
            
        if len(new_password) < 6:
            raise ValueError("新密码长度不能少于6位")
            
        return UserDAO.update_user(user_id, UserUpdate(password=new_password))

    def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码（管理员使用）
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            
        Returns:
            bool: 重置是否成功
        """
        if len(new_password) < 6:
            raise ValueError("新密码长度不能少于6位")
            
        return UserDAO.update_user(user_id, UserUpdate(password=new_password))