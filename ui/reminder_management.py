#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒管理界面
"""
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QComboBox, QSpinBox, QPushButton, QTableWidget,
    QTableWidgetItem, QGroupBox, QMessageBox, QDialog, QTextEdit
)
from ui.reminder_dialog import EditReminderDialog
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from logic.reminder_logic import ReminderLogic
from logic.project_logic import ProjectLogic


class ReminderManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.reminder_logic = ReminderLogic()
        self.init_ui()
        self.load_reminders()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel('提醒管理')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建按钮区域
        btn_layout = QHBoxLayout()

        edit_btn = QPushButton('编辑提醒')
        edit_btn.clicked.connect(self.edit_reminder)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton('删除提醒')
        delete_btn.clicked.connect(self.delete_reminder)
        btn_layout.addWidget(delete_btn)

        mark_read_btn = QPushButton('标记为已读')
        mark_read_btn.clicked.connect(self.mark_reminder_as_read)
        btn_layout.addWidget(mark_read_btn)

        main_layout.addLayout(btn_layout)

        # 创建提醒列表
        self.reminder_table = QTableWidget()
        self.reminder_table.setColumnCount(8)
        self.reminder_table.setHorizontalHeaderLabels([
            'ID', '项目名称', '提醒类型', '到期日期', '提前天数', '提醒方式', '状态', '创建时间'
        ])
        # 隐藏ID列
        self.reminder_table.setColumnHidden(0, True)
        self.reminder_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.reminder_table)

    # 移除了load_projects方法，因为不再需要项目选择功能

    # 移除了load_reminder_types方法，因为不再需要提醒类型选择功能

    # 移除了load_reminder_ways方法，因为不再需要提醒方式选择功能

    def load_reminders(self):
        # 加载提醒列表
        reminders = self.reminder_logic.get_all_reminders()
        self.display_reminders(reminders)

    def display_reminders(self, reminders):
        # 显示提醒列表
        self.reminder_table.setRowCount(0)
        for row, reminder in enumerate(reminders):
            self.reminder_table.insertRow(row)
            # 存储提醒ID（不显示）
            self.reminder_table.setItem(row, 0, QTableWidgetItem(str(reminder['id'])))
            self.reminder_table.setItem(row, 1, QTableWidgetItem(reminder['project_name']))
            self.reminder_table.setItem(row, 2, QTableWidgetItem(reminder['reminder_type']))
            self.reminder_table.setItem(row, 3, QTableWidgetItem(reminder['due_date']))
            self.reminder_table.setItem(row, 4, QTableWidgetItem(str(reminder['days_before'])))
            self.reminder_table.setItem(row, 5, QTableWidgetItem(reminder['reminder_way']))
            self.reminder_table.setItem(row, 6, QTableWidgetItem(reminder['status']))
            self.reminder_table.setItem(row, 7, QTableWidgetItem(reminder['create_time']))

            # 设置未读提醒的样式
            if reminder['status'] == '未读':
                for column in range(1, self.reminder_table.columnCount()):
                    item = self.reminder_table.item(row, column)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

        # 自动调整列宽
        for column in range(self.reminder_table.columnCount()):
            self.reminder_table.resizeColumnToContents(column)

    def delete_reminder(self):
        # 删除提醒
        selected_row = self.reminder_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '操作错误', '请先选择要删除的提醒')
            return

        # 获取选中的提醒ID
        reminder_id = int(self.reminder_table.item(selected_row, 0).text())
        project_name = self.reminder_table.item(selected_row, 1).text()

        # 确认删除
        reply = QMessageBox.question(self, '确认', f'确定要删除项目 {project_name} 的提醒吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除提醒
            if self.reminder_logic.delete_reminder(reminder_id):
                QMessageBox.information(self, '成功', '提醒已成功删除')
                # 重新加载提醒列表
                self.load_reminders()
            else:
                QMessageBox.warning(self, '失败', '提醒删除失败')

    def mark_reminder_as_read(self):
        # 标记提醒为已读
        selected_row = self.reminder_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '操作错误', '请先选择要标记的提醒')
            return

        # 获取选中的提醒ID
        reminder_id = int(self.reminder_table.item(selected_row, 0).text())

        # 标记为已读
        if self.reminder_logic.mark_reminder_as_read(reminder_id):
            QMessageBox.information(self, '成功', '提醒已标记为已读')
            # 重新加载提醒列表
            self.load_reminders()
        else:
            QMessageBox.warning(self, '失败', '标记提醒为已读失败')

    def edit_reminder(self):
        # 编辑提醒
        selected_row = self.reminder_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '操作错误', '请先选择要编辑的提醒')
            return

        # 获取选中的提醒ID
        reminder_id = int(self.reminder_table.item(selected_row, 0).text())

        # 打开编辑提醒对话框
        edit_dialog = EditReminderDialog(self, reminder_id)
        if edit_dialog.exec_() == QDialog.Accepted:
            # 获取编辑后的提醒数据
            reminder_data = edit_dialog.get_reminder_data()
            # 更新提醒
            if self.reminder_logic.update_reminder(reminder_data):
                QMessageBox.information(self, '成功', '提醒已成功更新')
                # 重新加载提醒列表
                self.load_reminders()
            else:
                QMessageBox.warning(self, '失败', '提醒更新失败')
