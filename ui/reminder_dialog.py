#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLabel, QComboBox,
    QSpinBox, QTextEdit, QDialogButtonBox, QMessageBox
)

from logic.project_logic import ProjectLogic
from logic.reminder_logic import ReminderLogic


class EditReminderDialog(QDialog):
    """编辑提醒对话框"""

    def __init__(self, parent=None, reminder_id=None):
        super().__init__(parent)
        self.setWindowTitle('编辑提醒')
        self.setModal(True)
        self.reminder_id = reminder_id
        self.reminder_logic = ReminderLogic()
        self.project_logic = ProjectLogic()
        self.reminder_data = None
        self.init_ui()
        self.load_reminder_types()
        self.load_reminder_ways()
        if self.reminder_id:
            self.load_reminder_data()

    def init_ui(self):
        # 设置弹窗宽度
        self.setFixedWidth(500)
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建表单布局
        form_layout = QFormLayout()

        # 项目名称（不可编辑）
        self.project_name_label = QLabel()
        form_layout.addRow('项目名称', self.project_name_label)

        # 提醒类型
        self.reminder_type_combo = QComboBox()
        form_layout.addRow('提醒类型 *', self.reminder_type_combo)

        # 提前提醒天数
        self.days_before_spin = QSpinBox()
        self.days_before_spin.setRange(1, 365)
        form_layout.addRow('提前提醒天数 *', self.days_before_spin)

        # 提醒方式
        self.reminder_way_combo = QComboBox()
        form_layout.addRow('提醒方式 *', self.reminder_way_combo)

        # 提醒内容
        self.reminder_content_edit = QTextEdit()
        self.reminder_content_edit.setPlaceholderText('请输入提醒内容')
        form_layout.addRow('提醒内容', self.reminder_content_edit)

        main_layout.addLayout(form_layout)

        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def load_reminder_types(self):
        # 加载提醒类型
        reminder_types = ['到期提醒', '里程碑提醒', '结题提醒', '其他提醒']
        self.reminder_type_combo.addItems(reminder_types)

    def load_reminder_ways(self):
        # 加载提醒方式
        reminder_ways = ['系统内通知', '邮件通知', '短信通知', '微信通知']
        self.reminder_way_combo.addItems(reminder_ways)

    def load_reminder_data(self):
        # 加载提醒数据
        self.reminder_data = self.reminder_logic.get_reminder_by_id(self.reminder_id)
        if self.reminder_data:
            self.project_name_label.setText(self.reminder_data['project_name'])
            # 设置提醒类型
            reminder_type_index = self.reminder_type_combo.findText(self.reminder_data['reminder_type'])
            if reminder_type_index >= 0:
                self.reminder_type_combo.setCurrentIndex(reminder_type_index)
            # 设置提前天数
            self.days_before_spin.setValue(self.reminder_data['days_before'])
            # 设置提醒方式
            reminder_way_index = self.reminder_way_combo.findText(self.reminder_data['reminder_way'])
            if reminder_way_index >= 0:
                self.reminder_way_combo.setCurrentIndex(reminder_way_index)
            # 设置提醒内容
            self.reminder_content_edit.setText(self.reminder_data['content'])
        else:
            QMessageBox.warning(self, '错误', '无法加载提醒数据')
            self.reject()

    def get_reminder_data(self):
        """获取提醒数据"""
        return {
            'id': self.reminder_id,
            'project_id': self.reminder_data['project_id'],
            'project_name': self.reminder_data['project_name'],
            'reminder_type': self.reminder_type_combo.currentText(),
            'days_before': self.days_before_spin.value(),
            'reminder_way': self.reminder_way_combo.currentText(),
            'content': self.reminder_content_edit.toPlainText()
        }

    def accept(self):
        """验证并接受表单"""
        super().accept()


class BatchReminderDialog(QDialog):
    """批量添加提醒对话框"""

    def __init__(self, parent=None, project_ids=None):
        super().__init__(parent)
        self.setWindowTitle('批量添加提醒')
        self.setModal(True)
        self.project_ids = project_ids if project_ids else []
        self.reminder_logic = ReminderLogic()
        self.project_logic = ProjectLogic()
        self.init_ui()
        self.load_reminder_types()
        self.load_reminder_ways()

    def init_ui(self):
        # 设置弹窗宽度
        self.setFixedWidth(500)
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 显示已选择的项目数量
        project_count_label = QLabel(f'已选择 {len(self.project_ids)} 个项目')
        main_layout.addWidget(project_count_label)

        # 创建表单布局
        form_layout = QFormLayout()

        # 提醒类型
        self.reminder_type_combo = QComboBox()
        form_layout.addRow('提醒类型 *', self.reminder_type_combo)

        # 提前提醒天数
        self.days_before_spin = QSpinBox()
        self.days_before_spin.setRange(1, 365)
        self.days_before_spin.setValue(30)
        form_layout.addRow('提前提醒天数 *', self.days_before_spin)

        # 提醒方式
        self.reminder_way_combo = QComboBox()
        form_layout.addRow('提醒方式 *', self.reminder_way_combo)

        # 提醒内容
        self.reminder_content_edit = QTextEdit()
        self.reminder_content_edit.setPlaceholderText('请输入提醒内容')
        form_layout.addRow('提醒内容', self.reminder_content_edit)

        main_layout.addLayout(form_layout)

        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def load_reminder_types(self):
        # 加载提醒类型
        reminder_types = ['到期提醒', '里程碑提醒', '结题提醒', '其他提醒']
        self.reminder_type_combo.addItems(reminder_types)

    def load_reminder_ways(self):
        # 加载提醒方式
        reminder_ways = ['系统内通知', '邮件通知', '短信通知', '微信通知']
        self.reminder_way_combo.addItems(reminder_ways)

    def get_reminder_data(self):
        """获取提醒数据"""
        return {
            'project_ids': self.project_ids,
            'reminder_type': self.reminder_type_combo.currentText(),
            'days_before': self.days_before_spin.value(),
            'reminder_way': self.reminder_way_combo.currentText(),
            'content': self.reminder_content_edit.toPlainText()
        }

    def accept(self):
        """验证并接受表单"""
        super().accept()
