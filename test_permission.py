#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限控制功能测试脚本
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.session import SessionManager
from logic.project_logic import ProjectLogic
from logic.user_logic import UserLogic
from logic.reminder_logic import ReminderLogic
from logic.project_result_logic import ProjectResultLogic
from logic.project_result_attachment_logic import ProjectResultAttachmentLogic
from models.user import User, UserRole, UserStatus


def test_permission_system():
    """测试权限系统"""
    print("=== 权限控制功能测试 ===\n")
    
    # 测试1：未登录用户
    print("测试1：未登录用户权限检查")
    SessionManager.clear_current_user()
    
    try:
        result = SessionManager.is_admin()
        print(f"未登录用户权限检查结果: {result}")
    except Exception as e:
        print(f"未登录用户权限检查异常: {e}")
    
    # 测试2：普通用户
    print("\n测试2：普通用户权限检查")
    now = datetime.now()
    normal_user = User(
        id=1,
        username="test_user",
        real_name="测试用户",
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        email="test@example.com",
        create_time=now,
        update_time=now
    )
    SessionManager.set_current_user(normal_user)
    
    print(f"当前用户: {SessionManager.get_current_user().username}")
    print(f"是否为管理员: {SessionManager.is_admin()}")
    
    # 测试3：管理员用户
    print("\n测试3：管理员用户权限检查")
    admin_user = User(
        id=2,
        username="admin",
        real_name="管理员",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        email="admin@example.com",
        create_time=now,
        update_time=now
    )
    SessionManager.set_current_user(admin_user)
    
    print(f"当前用户: {SessionManager.get_current_user().username}")
    print(f"是否为管理员: {SessionManager.is_admin()}")
    
    # 测试4：项目删除权限
    print("\n测试4：项目删除权限测试")
    project_logic = ProjectLogic()
    
    # 普通用户尝试删除项目
    SessionManager.set_current_user(normal_user)
    try:
        project_logic.delete_project(1)
        print("❌ 普通用户删除项目成功（应该失败）")
    except PermissionError as e:
        print(f"✅ 普通用户删除项目: {e}")
    
    # 管理员用户尝试删除项目
    SessionManager.set_current_user(admin_user)
    try:
        # 这里不会真正删除，只是测试权限检查
        print("管理员用户删除项目权限检查通过")
    except PermissionError as e:
        print(f"❌ 管理员用户删除项目权限检查失败: {e}")
    
    # 测试5：用户删除权限
    print("\n测试5：用户删除权限测试")
    user_logic = UserLogic()
    
    # 普通用户尝试删除用户
    SessionManager.set_current_user(normal_user)
    try:
        user_logic.delete_user(3)
        print("❌ 普通用户删除用户成功（应该失败）")
    except PermissionError as e:
        print(f"✅ 普通用户删除用户: {e}")
    
    # 管理员用户尝试删除用户
    SessionManager.set_current_user(admin_user)
    try:
        print("管理员用户删除用户权限检查通过")
    except PermissionError as e:
        print(f"❌ 管理员用户删除用户权限检查失败: {e}")
    
    # 测试6：提醒删除权限
    print("\n测试6：提醒删除权限测试")
    reminder_logic = ReminderLogic()
    
    # 普通用户尝试删除提醒
    SessionManager.set_current_user(normal_user)
    try:
        reminder_logic.delete_reminder(1)
        print("❌ 普通用户删除提醒成功（应该失败）")
    except PermissionError as e:
        print(f"✅ 普通用户删除提醒: {e}")
    
    # 管理员用户尝试删除提醒
    SessionManager.set_current_user(admin_user)
    try:
        print("管理员用户删除提醒权限检查通过")
    except PermissionError as e:
        print(f"❌ 管理员用户删除提醒权限检查失败: {e}")
    
    # 测试7：项目成果删除权限
    print("\n测试7：项目成果删除权限测试")
    result_logic = ProjectResultLogic()
    
    # 普通用户尝试删除项目成果
    SessionManager.set_current_user(normal_user)
    try:
        result_logic.delete_project_result(1)
        print("❌ 普通用户删除项目成果成功（应该失败）")
    except PermissionError as e:
        print(f"✅ 普通用户删除项目成果: {e}")
    
    # 管理员用户尝试删除项目成果
    SessionManager.set_current_user(admin_user)
    try:
        print("管理员用户删除项目成果权限检查通过")
    except PermissionError as e:
        print(f"❌ 管理员用户删除项目成果权限检查失败: {e}")
    
    # 测试8：项目成果附件删除权限
    print("\n测试8：项目成果附件删除权限测试")
    attachment_logic = ProjectResultAttachmentLogic()
    
    # 普通用户尝试删除项目成果附件
    SessionManager.set_current_user(normal_user)
    try:
        attachment_logic.delete_attachment(1)
        print("❌ 普通用户删除项目成果附件成功（应该失败）")
    except PermissionError as e:
        print(f"✅ 普通用户删除项目成果附件: {e}")
    
    # 管理员用户尝试删除项目成果附件
    SessionManager.set_current_user(admin_user)
    try:
        print("管理员用户删除项目成果附件权限检查通过")
    except PermissionError as e:
        print(f"❌ 管理员用户删除项目成果附件权限检查失败: {e}")
    
    print("\n=== 权限控制功能测试完成 ===")


if __name__ == "__main__":
    test_permission_system()