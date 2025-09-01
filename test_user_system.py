#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试用户系统功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.db_connection import init_database
from logic.user_logic import UserLogic
from models.user import UserCreate, UserRole, UserStatus

def test_user_system():
    """测试用户系统"""
    print("开始测试用户系统...")
    
    # 初始化数据库
    print("1. 初始化数据库...")
    init_database()
    
    # 创建用户逻辑实例
    user_logic = UserLogic()
    
    # 测试管理员登录
    print("2. 测试管理员登录...")
    admin_user = user_logic.authenticate_user("admin", "12345678")
    if admin_user:
        print(f"✓ 管理员登录成功: {admin_user.username} ({admin_user.real_name})")
        print(f"  角色: {admin_user.role}")
        print(f"  状态: {admin_user.status}")
    else:
        print("✗ 管理员登录失败")
    
    # 测试创建新用户
    print("3. 测试创建新用户...")
    try:
        new_user = UserCreate(
            username="testuser",
            password="test123",
            real_name="测试用户",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email="test@example.com",
            phone="1234567890"
        )
        
        success = user_logic.create_user(new_user)
        if success:
            print("✓ 创建用户成功")
            
            # 测试新用户登录
            test_user = user_logic.authenticate_user("testuser", "test123")
            if test_user:
                print("✓ 新用户登录成功")
            else:
                print("✗ 新用户登录失败")
        else:
            print("✗ 创建用户失败")
    except Exception as e:
        print(f"✗ 创建用户出错: {e}")
    
    # 测试获取所有用户
    print("4. 测试获取所有用户...")
    try:
        all_users = user_logic.get_all_users()
        print(f"✓ 获取用户列表成功，共 {len(all_users)} 个用户")
        for user in all_users:
            print(f"  - {user.username}: {user.real_name} ({user.role})")
    except Exception as e:
        print(f"✗ 获取用户列表出错: {e}")
    
    print("\n用户系统测试完成!")

if __name__ == "__main__":
    test_user_system()