#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒对话框
"""
from datetime import datetime

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLabel, QComboBox,
    QSpinBox, QTextEdit, QDialogButtonBox, QMessageBox, QDateEdit
)

from logic.project_logic import ProjectLogic
from logic.reminder_logic import ReminderLogic
from models.reminder import ReminderType, ReminderWay
from PyQt5.QtWidgets import QLabel

class BaseReminderDialog(QDialog):
    """提醒对话框基类，抽离公共逻辑"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.reminder_logic = ReminderLogic()
        self.project_logic = ProjectLogic()

        # 公共UI组件
        self.reminder_type_combo = None
        self.days_before_spin = None
        self.reminder_way_combo = None
        self.reminder_content_edit = None
        self.reminder_base_date_edit = None  # 提醒基准时间

        # 设置基础UI
        self.setFixedWidth(500)

    def _init_common_ui(self, main_layout):
        """初始化公共UI组件"""
        # 创建表单布局
        form_layout = QFormLayout()

        # 提醒类型
        self.reminder_type_combo = QComboBox()
        form_layout.addRow('提醒类型 *', self.reminder_type_combo)


        # 提醒基准时间（默认隐藏）
        self.reminder_base_date_edit = QDateEdit()
        self.reminder_base_date_edit.setCalendarPopup(True)
        self.reminder_base_date_edit.setDisplayFormat('yyyy-MM-dd')
        # 将日期选择框添加到布局，但默认隐藏
        self.base_date_label = QLabel('提醒基准时间（自定义情况下使用）')
        form_layout.addRow(self.base_date_label, self.reminder_base_date_edit)
        self.reminder_base_date_edit.hide()
        self.base_date_label.hide()

        # 连接信号槽，监听提醒类型变化
        self.reminder_type_combo.currentTextChanged.connect(self.on_reminder_type_changed)

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
        """加载提醒类型"""
        reminder_types = [type_enum.value for type_enum in ReminderType]
        self.reminder_type_combo.addItems(reminder_types)

    def load_reminder_ways(self):
        """加载提醒方式"""
        reminder_ways = [way_enum.value for way_enum in ReminderWay]
        self.reminder_way_combo.addItems(reminder_ways)

    def _get_selected_reminder_type_and_way(self):
        """获取选择的提醒类型和方式"""
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

        return reminder_type, reminder_way

    def on_reminder_type_changed(self, text):
        """处理提醒类型变化，显示或隐藏提醒基准时间"""
        
        if text == ReminderType.CUSTOM.value:
            base_date = datetime.strptime("2000-01-01", '%Y-%m-%d').date()
            if self.reminder_base_date_edit.date() == QDate(base_date.year, base_date.month, base_date.day):
                q_date = QDate.currentDate()
                self.reminder_base_date_edit.setDate(q_date)
            self.reminder_base_date_edit.show()
            self.base_date_label.show()  # 直接显示标签
        else:
            self.reminder_base_date_edit.hide()
            self.base_date_label.hide()  # 直接隐藏标签
        
        # 调整对话框大小以适应控件显示状态
        self.adjustSize()

    def accept(self):
        """验证并接受表单"""
        super().accept()


class EditReminderDialog(BaseReminderDialog):
    """编辑提醒对话框"""

    def __init__(self, parent=None, reminder_id=None):
        super().__init__(parent)
        self.setWindowTitle('编辑提醒')
        self.reminder_id = reminder_id
        self.reminder_data = None
        self.project_name_label = None
        self.init_ui()
        self.load_reminder_types()
        self.load_reminder_ways()
        if self.reminder_id:
            self.load_reminder_data()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建表单布局
        form_layout = QFormLayout()

        # 项目名称（不可编辑）
        self.project_name_label = QLabel()
        form_layout.addRow('项目名称', self.project_name_label)

        # 添加到主布局
        main_layout.addLayout(form_layout)

        # 初始化公共UI组件
        self._init_common_ui(main_layout)

    def load_reminder_data(self):
        """加载提醒数据"""
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
            # 设置提醒基准时间（如果有）
            if hasattr(self.reminder_data, 'due_date') and self.reminder_data.due_date:
                from datetime import datetime
                try:
                    # 尝试将日期字符串转换为QDate
                    if isinstance(self.reminder_data.due_date, str):
                        date_obj = datetime.strptime(self.reminder_data.due_date, '%Y-%m-%d').date()
                    else:
                        date_obj = self.reminder_data.due_date
                    from PyQt5.QtCore import QDate
                    q_date = QDate(date_obj.year, date_obj.month, date_obj.day)
                    self.reminder_base_date_edit.setDate(q_date)
                except:
                    pass
            # 触发类型变化事件，确保正确显示或隐藏基准时间
            self.on_reminder_type_changed(self.reminder_type_combo.currentText())
        else:
            QMessageBox.warning(self, '错误', '无法加载提醒数据')
            self.reject()

    def get_reminder_data(self):
        """获取提醒数据"""
        from models.reminder import ReminderUpdate
        from datetime import datetime

        reminder_type, reminder_way = self._get_selected_reminder_type_and_way()

        # 创建更新对象
        reminder_update = ReminderUpdate(
            id=self.reminder_id,
            project_id=self.reminder_data.project_id,
            project_name=self.reminder_data.project_name,
            reminder_type=reminder_type,
            days_before=self.days_before_spin.value(),
            reminder_way=reminder_way,
            content=self.reminder_content_edit.toPlainText()
        )

        # 如果是自定义类型，设置due_date
        if reminder_type == ReminderType.CUSTOM:
            q_date = self.reminder_base_date_edit.date()
            date_str = q_date.toString('yyyy-MM-dd')
            reminder_update.due_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        return reminder_update


class BatchReminderDialog(BaseReminderDialog):
    """批量添加提醒对话框"""

    def __init__(self, parent=None, project_ids=None):
        super().__init__(parent)
        self.setWindowTitle('批量添加提醒')
        self.project_ids = project_ids if project_ids else []
        self.init_ui()
        self.load_reminder_types()
        self.load_reminder_ways()

        # 批量添加提醒时，默认提前天数为30天
        self.days_before_spin.setValue(30)

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 显示已选择的项目数量
        project_count_label = QLabel(f'已选择 {len(self.project_ids)} 个项目')
        main_layout.addWidget(project_count_label)

        # 初始化公共UI组件
        self._init_common_ui(main_layout)

    def get_reminder_data(self):
        """获取提醒数据"""
        from datetime import datetime

        reminder_type, reminder_way = self._get_selected_reminder_type_and_way()

        # 设置一个默认的due_date（当前日期）
        # 实际上，这个值会在ReminderLogic.create_reminder中被覆盖
        # 但我们需要提供一个有效值以通过验证
        due_date = datetime.now().strftime('%Y-%m-%d')

        # 如果是自定义类型，使用选择的基准时间
        if reminder_type == ReminderType.CUSTOM:
            q_date = self.reminder_base_date_edit.date()
            due_date = q_date.toString('yyyy-MM-dd')

        # 返回字典，但使用正确的枚举值，并包含due_date
        return {
            'project_ids': self.project_ids,
            'reminder_type': reminder_type,
            'days_before': self.days_before_spin.value(),
            'reminder_way': reminder_way,
            'content': self.reminder_content_edit.toPlainText(),
            'due_date': due_date  # 添加due_date字段
        }
