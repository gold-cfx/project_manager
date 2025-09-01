#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 用户数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"    # 激活
    INACTIVE = "inactive"  # 禁用


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., description="用户名", max_length=50)
    real_name: str = Field(..., description="真实姓名", max_length=50)
    role: UserRole = Field(UserRole.USER, description="用户角色")
    status: UserStatus = Field(UserStatus.ACTIVE, description="用户状态")
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    last_login: Optional[datetime] = Field(None, description="最后登录时间")


class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., description="密码", min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户模型"""
    real_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """用户完整模型"""
    id: int = Field(..., description="用户ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")