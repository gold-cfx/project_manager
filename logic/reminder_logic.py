#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒业务逻辑
"""
from datetime import datetime, timedelta
from typing import List, Optional

from data.project_dao import ProjectDAO
from data.reminder_dao import ReminderDAO
from models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderStatus, ReminderType
from utils.decorators import validate_model_data, log_operation


class ReminderLogic:
    """提醒业务逻辑类"""

    def __init__(self):
        self.reminder_dao = ReminderDAO()
        self.project_dao = ProjectDAO()

    @validate_model_data(ReminderCreate)
    @log_operation("创建提醒")
    def create_reminder(self, reminder_data: ReminderCreate) -> int:
        """创建新提醒
        
        Args:
            reminder_data: 提醒数据，ReminderCreate模型实例
            
        Returns:
            int: 新创建的提醒ID，失败返回-1
        """
        # 获取项目结束日期
        project = self.project_dao.get_by_id(reminder_data.project_id)
        if not project:
            raise ValueError(f"项目ID {reminder_data.project_id} 不存在")

        # 计算提醒日期
        if reminder_data.reminder_type == ReminderType.PROJECT_END:
            end_date = project.end_date
        elif reminder_data.reminder_type == ReminderType.PROJECT_START:
            end_date = project.start_date
        elif reminder_data.reminder_type == ReminderType.CUSTOM:
            end_date = reminder_data.start_date
        days_before = reminder_data.days_before

        # 如果end_date是字符串，转换为日期对象
        if isinstance(end_date, str):
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date_obj = end_date

        reminder_date = end_date_obj - timedelta(days=days_before)

        # 设置提醒日期
        reminder_data_dict = reminder_data.dict()
        reminder_data_dict['start_date'] = reminder_date.strftime('%Y-%m-%d')
        reminder_data_dict['status'] = ReminderStatus.UNREAD

        # 创建提醒
        updated_reminder_data = ReminderCreate(**reminder_data_dict)
        return self.reminder_dao.insert(updated_reminder_data)

    @validate_model_data(ReminderUpdate)
    @log_operation("更新提醒")
    def update_reminder(self, reminder_id: int, reminder_data: ReminderUpdate) -> bool:
        """更新提醒信息
        
        Args:
            reminder_id: 提醒ID
            reminder_data: 提醒更新数据，ReminderUpdate模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 检查提醒是否存在
        existing_reminder = self.get_reminder_by_id(reminder_id)
        if not existing_reminder:
            raise ValueError(f"提醒ID {reminder_id} 不存在")

        # 如果更新了项目ID，检查项目是否存在
        project_id = reminder_data.project_id or existing_reminder.project_id
        project = self.project_dao.get_by_id(project_id)
        if not project:
            raise ValueError(f"项目ID {project_id} 不存在")

        # 计算提醒日期
        days_before = reminder_data.days_before or existing_reminder.days_before
        end_date = project.end_date

        # 如果end_date是字符串，转换为日期对象
        if isinstance(end_date, str):
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date_obj = end_date

        reminder_date = end_date_obj - timedelta(days=days_before)

        # 更新提醒日期
        reminder_data_dict = reminder_data.dict(exclude_unset=True, exclude_none=True)
        # 确保start_date字段存在，即使在原始数据中没有提供
        reminder_data_dict['start_date'] = reminder_date.strftime('%Y-%m-%d')
        reminder_data_dict['status'] = ReminderStatus.UNREAD

        # 更新提醒
        updated_reminder_data = ReminderUpdate(**reminder_data_dict)
        return self.reminder_dao.update(reminder_id, updated_reminder_data)

    @log_operation("删除提醒")
    def delete_reminder(self, reminder_id: int) -> bool:
        """删除提醒
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            PermissionError: 当前用户无删除权限
        """
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除提醒")

        return self.reminder_dao.delete(reminder_id)

    def get_reminder_by_id(self, reminder_id: int) -> Optional[Reminder]:
        """根据ID获取提醒
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            Optional[Reminder]: 提醒对象，不存在返回None
        """
        return self.reminder_dao.get_by_id(reminder_id)

    def get_all_reminders(self) -> List[Reminder]:
        """获取所有提醒
        
        Returns:
            List[Reminder]: 提醒列表
        """
        return self.reminder_dao.get_all()

    def get_unread_reminders(self) -> List[Reminder]:
        """获取未读提醒
        
        Returns:
            List[Reminder]: 未读提醒列表
        """
        return self.reminder_dao.get_unread()

    def mark_reminder_as_read(self, reminder_id: int) -> bool:
        """标记提醒为已读
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            bool: 标记是否成功
        """
        return self.reminder_dao.mark_as_read(reminder_id)

    def check_due_reminders(self) -> List[Reminder]:
        """检查开始日期提醒
        
        Returns:
            List[Reminder]: 开始日期提醒列表
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.reminder_dao.get_upcoming_reminders(today)

    def get_reminders_by_project(self, project_id: int) -> List[Reminder]:
        """获取项目的所有提醒
        
        Args:
            project_id: 项目ID
            
        Returns:
            List[Reminder]: 提醒列表
        """
        return self.reminder_dao.get_by_project_id(project_id)
