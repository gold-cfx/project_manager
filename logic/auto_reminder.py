# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 自动提醒功能
"""
import datetime
from typing import List

from PyQt5.QtWidgets import QMessageBox, QPushButton

from logic.reminder_logic import ReminderLogic
from models.reminder import Reminder


class AutoReminder:
    """自动提醒类，负责在系统启动时检查并显示需要提醒的项目"""

    def __init__(self):
        """初始化自动提醒类"""
        self.reminder_logic = ReminderLogic()

    def check_and_show_reminders(self) -> None:
        """检查需要提醒的项目并显示提醒对话框
        
        系统启动后自动扫描提醒表，查询未读的所有提醒，
        如果当前时间在 start_date 到 start_date + days_before 之间，则弹窗提醒
        """
        # 获取所有未读提醒
        unread_reminders = self.reminder_logic.get_unread_reminders()

        # 获取当前时间
        current_time = datetime.datetime.now()

        # 检查哪些提醒需要显示
        reminders_to_show = self._filter_reminders_to_show(unread_reminders, current_time)

        # 显示需要提醒的项目
        self._show_reminders(reminders_to_show)

    def _filter_reminders_to_show(self, reminders: List[Reminder], current_time: datetime.datetime) -> List[Reminder]:
        """过滤出当前需要显示的提醒
        
        Args:
            reminders: 提醒列表
            current_time: 当前时间
            
        Returns:
            List[Reminder]: 需要显示的提醒列表
        """
        reminders_to_show = []

        for reminder in reminders:
            # 将start_date转换为datetime对象
            if isinstance(reminder.start_date, str):
                start_date = datetime.datetime.strptime(reminder.start_date, '%Y-%m-%d')
            else:
                # 处理date对象
                start_date = datetime.datetime.combine(reminder.start_date, datetime.time.min)

            # 计算提醒的时间范围：start_date 到 start_date + days_before 天
            end_date = start_date + datetime.timedelta(days=reminder.days_before)

            # 检查当前时间是否在提醒时间范围内
            if start_date <= current_time <= end_date:
                reminders_to_show.append(reminder)

        return reminders_to_show

    def _show_reminders(self, reminders: List[Reminder]) -> None:
        """显示提醒对话框，每个提醒单独显示，操作作用于单个提醒
        
        Args:
            reminders: 需要显示的提醒列表
        """
        if not reminders:
            return

        # 对提醒按日期排序
        reminders.sort(key=lambda r: r.start_date)

        # 为每个提醒单独显示对话框
        for i, reminder in enumerate(reminders, 1):
            # 创建提醒消息
            message = f"提醒 {i}/{len(reminders)}\n\n"
            message += f"项目：{reminder.project_name}\n"
            message += f"类型：{reminder.reminder_type}\n"
            message += f"内容：{reminder.content}\n"

            # 创建自定义消息框
            msg_box = QMessageBox()
            msg_box.setWindowTitle("项目提醒")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            
            # 添加"下次继续提醒"按钮
            remind_later_btn = msg_box.addButton("下次继续提醒", QMessageBox.ActionRole)
            
            # 添加"不再提醒"按钮
            remind_stop_btn = msg_box.addButton("不再提醒", QMessageBox.AcceptRole)
            
            # 设置默认按钮
            msg_box.setDefaultButton(remind_later_btn)
            
            # 显示消息框并获取用户选择
            msg_box.exec_()
            
            # 根据用户选择处理单个提醒
            if msg_box.clickedButton() == remind_stop_btn:
                # 用户选择"不再提醒"，标记当前提醒为已读
                self.reminder_logic.mark_reminder_as_read(reminder.id)


# 创建单例实例，方便在main中使用
auto_reminder = AutoReminder()
