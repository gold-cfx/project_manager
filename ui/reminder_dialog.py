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
        from models.reminder import ReminderType
        reminder_types = [type_enum.value for type_enum in ReminderType]
        self.reminder_type_combo.addItems(reminder_types)

    def load_reminder_ways(self):
        # 加载提醒方式
        from models.reminder import ReminderWay
        reminder_ways = [way_enum.value for way_enum in ReminderWay]
        self.reminder_way_combo.addItems(reminder_ways)

    def load_reminder_data(self):
        # 加载提醒数据
        self.reminder_data = self.reminder_logic.get_reminder_by_id(self.reminder_id)
        if self.reminder_data:
            # 确保使用属性访问方式而不是字典访问方式
            self.project_name_label.setText(self.reminder_data.project_name)
            # 设置提醒类型
            reminder_type_index = self.reminder_type_combo.findText(self.reminder_data.reminder_type)
            if reminder_type_index >= 0:
                self.reminder_type_combo.setCurrentIndex(reminder_type_index)
            # 设置提前天数
            self.days_before_spin.setValue(self.reminder_data.days_before)
            # 设置提醒方式
            reminder_way_index = self.reminder_way_combo.findText(self.reminder_data.reminder_way)
            if reminder_way_index >= 0:
                self.reminder_way_combo.setCurrentIndex(reminder_way_index)
            # 设置提醒内容
            self.reminder_content_edit.setText(self.reminder_data.content)
        else:
            QMessageBox.warning(self, '错误', '无法加载提醒数据')
            self.reject()

    def get_reminder_data(self):
        """获取提醒数据"""
        from models.reminder import ReminderUpdate, ReminderType, ReminderWay
        
        # 获取当前选择的提醒类型和提醒方式
        reminder_type_text = self.reminder_type_combo.currentText()
        reminder_way_text = self.reminder_way_combo.currentText()
        
        # 确保提醒类型和提醒方式与枚举值匹配
        reminder_type = ReminderType.CUSTOM  # 默认使用自定义类型
        for type_enum in ReminderType:
            if type_enum.value == reminder_type_text:
                reminder_type = type_enum
                break
        
        reminder_way = ReminderWay.SYSTEM  # 默认使用系统提醒
        for way_enum in ReminderWay:
            if way_enum.value == reminder_way_text:
                reminder_way = way_enum
                break
        
        return ReminderUpdate(
            id=self.reminder_id,
            project_id=self.reminder_data.project_id,
            project_name=self.reminder_data.project_name,
            reminder_type=reminder_type,
            days_before=self.days_before_spin.value(),
            reminder_way=reminder_way,
            content=self.reminder_content_edit.toPlainText()
        )

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
        from models.reminder import ReminderType
        reminder_types = [type_enum.value for type_enum in ReminderType]
        self.reminder_type_combo.addItems(reminder_types)

    def load_reminder_ways(self):
        # 加载提醒方式
        from models.reminder import ReminderWay
        reminder_ways = [way_enum.value for way_enum in ReminderWay]
        self.reminder_way_combo.addItems(reminder_ways)

    def get_reminder_data(self):
        """获取提醒数据"""
        from models.reminder import ReminderType, ReminderWay, ReminderCreate
        from datetime import datetime, timedelta
        
        # 获取当前选择的提醒类型和提醒方式
        reminder_type_text = self.reminder_type_combo.currentText()
        reminder_way_text = self.reminder_way_combo.currentText()
        
        # 确保提醒类型和提醒方式与枚举值匹配
        reminder_type = ReminderType.CUSTOM  # 默认使用自定义类型
        for type_enum in ReminderType:
            if type_enum.value == reminder_type_text:
                reminder_type = type_enum
                break
        
        reminder_way = ReminderWay.SYSTEM  # 默认使用系统提醒
        for way_enum in ReminderWay:
            if way_enum.value == reminder_way_text:
                reminder_way = way_enum
                break
        
        # 设置一个默认的due_date（当前日期）
        # 实际上，这个值会在ReminderLogic.create_reminder中被覆盖
        # 但我们需要提供一个有效值以通过验证
        due_date = datetime.now().strftime('%Y-%m-%d')
        
        # 返回字典，但使用正确的枚举值，并包含due_date
        return {
            'project_ids': self.project_ids,
            'reminder_type': reminder_type,
            'days_before': self.days_before_spin.value(),
            'reminder_way': reminder_way,
            'content': self.reminder_content_edit.toPlainText(),
            'due_date': due_date  # 添加due_date字段
        }

    def accept(self):
        """验证并接受表单"""
        super().accept()
