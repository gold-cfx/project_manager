# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 自动提醒功能
"""
import datetime
import json
import os
from typing import List

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QMessageBox

from config.settings import config_dir, BACKUP_CONFIG_DIR
from logic.reminder_logic import ReminderLogic
from models.reminder import Reminder
from utils.logger import get_logger

logger = get_logger(__name__)


class AutoReminder(QObject):
    """自动提醒类，负责在系统启动时检查并显示需要提醒的项目"""
    reminder_triggered = pyqtSignal(str, str, str)

    def __init__(self):
        """初始化自动提醒类"""
        super().__init__()
        self.reminder_logic = ReminderLogic()
        self.timer = None
        self.reminder_interval_hours = 1
        self.main_window = None

        # 加载定时任务配置
        self.load_timer_config()

    def initialize_timer(self):
        """初始化定时器（在QApplication创建后调用）"""
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_and_show_reminders)

            # 启动时立即检查一次
            self.check_and_show_reminders()

            # 启动定时器
            self.start_timer()

    def set_main_window(self, main_window):
        """设置主窗口引用，用于消息框的父窗口"""
        self.main_window = main_window

    def load_timer_config(self):
        """加载定时任务配置"""
        try:
            # 优先加载备份目录的配置
            backup_path = os.path.join(BACKUP_CONFIG_DIR, 'reminder_config.json')
            config_path = os.path.join(config_dir, 'reminder_config.json')

            if os.path.exists(backup_path):
                config_path = backup_path
            elif not os.path.exists(config_path):
                # 默认每小时检查一次
                self.reminder_interval_hours = 1
                self.save_timer_config()
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.reminder_interval_hours = config.get('reminder_interval_hours', 1)
        except Exception as e:
            logger.error(f"加载提醒配置时发生错误: {e}")
            self.reminder_interval_hours = 1

    def save_timer_config(self):
        """保存定时任务配置"""
        try:
            os.makedirs(config_dir, exist_ok=True)
            os.makedirs(BACKUP_CONFIG_DIR, exist_ok=True)

            config = {
                'reminder_interval_hours': self.reminder_interval_hours
            }

            # 保存到本地配置目录
            config_path = os.path.join(config_dir, 'reminder_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # 保存到备份目录
            backup_path = os.path.join(BACKUP_CONFIG_DIR, 'reminder_config.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存提醒配置时发生错误: {e}")

    def start_timer(self):
        """启动定时器"""
        interval_ms = self.reminder_interval_hours * 60 * 60 * 1000  # 转换为毫秒
        self.timer.start(interval_ms)
        logger.info(f"定时提醒已启动，每{self.reminder_interval_hours}小时检查一次")

    def stop_timer(self):
        """停止定时器"""
        self.timer.stop()

    def update_interval(self, hours):
        """更新检查间隔"""
        self.reminder_interval_hours = hours
        self.save_timer_config()
        self.stop_timer()
        self.start_timer()

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

        # 在显示提醒前，确保主窗口可见
        if self.main_window:
            # 如果主窗口被最小化到系统托盘，先显示主窗口
            if not self.main_window.isVisible():
                self.main_window.show_normal()
            # 确保主窗口在最前
            self.main_window.raise_()
            self.main_window.activateWindow()

        # 为每个提醒单独显示对话框
        for i, reminder in enumerate(reminders, 1):
            # 创建提醒消息
            message = f"提醒 {i}/{len(reminders)}\n\n"
            message += f"项目：{reminder.project_name}\n"
            message += f"类型：{reminder.reminder_type}\n"
            message += f"内容：{reminder.content}\n"

            # 创建自定义消息框，始终使用主窗口作为父窗口
            if self.main_window:
                msg_box = QMessageBox(self.main_window)
            else:
                # 如果没有主窗口引用，创建无父窗口的消息框（备用方案）
                msg_box = QMessageBox()
                msg_box.setWindowModality(Qt.ApplicationModal)

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
