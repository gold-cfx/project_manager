#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据字典管理界面
"""
from typing import List, Dict, Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QMessageBox, QComboBox, QDialog, QFormLayout,
                             QDialogButtonBox, QTextEdit, QSpinBox, QCheckBox,
                             QHeaderView)

from logic.data_dict_logic import DataDictLogic
from models.data_dict import DataDict, DataDictCreate, DataDictUpdate
from utils.session import SessionManager


class DataDictDialog(QDialog):
    """数据字典编辑对话框"""

    def __init__(self, parent=None, dict_item: DataDict = None):
        super().__init__(parent)
        self.dict_item = dict_item
        self.init_ui()

        if dict_item:
            self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("数据字典编辑")
        self.setModal(True)
        self.resize(500, 400)

        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 字典类型
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("如：project_status, project_level")
        layout.addRow("字典类型*:", self.type_edit)

        # 字典键
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("如：IN_PROGRESS, NATIONAL")
        layout.addRow("字典键*:", self.key_edit)

        # 字典值
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("如：进行中, 国家级")
        layout.addRow("字典值*:", self.value_edit)

        # 排序顺序
        self.sort_spin = QSpinBox()
        self.sort_spin.setRange(0, 999)
        layout.addRow("排序顺序:", self.sort_spin)

        # 是否启用
        self.active_check = QCheckBox("启用")
        self.active_check.setChecked(True)
        layout.addRow("状态:", self.active_check)

        # 描述
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        layout.addRow("描述:", self.desc_edit)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def load_data(self):
        """加载数据"""
        if self.dict_item:
            self.type_edit.setText(self.dict_item.dict_type)
            self.key_edit.setText(self.dict_item.dict_key)
            self.value_edit.setText(self.dict_item.dict_value)
            self.sort_spin.setValue(self.dict_item.sort_order)
            self.active_check.setChecked(self.dict_item.is_active)
            self.desc_edit.setPlainText(self.dict_item.description or "")

    def get_data(self) -> Dict[str, Any]:
        """获取表单数据"""
        return {
            "dict_type": self.type_edit.text().strip(),
            "dict_key": self.key_edit.text().strip(),
            "dict_value": self.value_edit.text().strip(),
            "sort_order": self.sort_spin.value(),
            "is_active": self.active_check.isChecked(),
            "description": self.desc_edit.toPlainText().strip()
        }


class DataDictManagement(QWidget):
    """数据字典管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logic = DataDictLogic()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("数据字典管理")
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 类型筛选
        self.type_filter = QComboBox()
        self.type_filter.addItem("全部类型", "")
        self.type_filter.addItem("项目状态", "project_status")
        self.type_filter.addItem("项目级别", "project_level")
        self.type_filter.addItem("项目来源", "project_source")
        self.type_filter.addItem("项目类型", "project_type")
        self.type_filter.addItem("成果类型", "result_type")
        self.type_filter.currentTextChanged.connect(self.filter_data)
        toolbar_layout.addWidget(QLabel("类型筛选:"))
        toolbar_layout.addWidget(self.type_filter)

        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索：键或值")
        self.search_edit.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(QLabel("搜索:"))
        toolbar_layout.addWidget(self.search_edit)

        toolbar_layout.addStretch()

        # 添加按钮
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.on_add)
        toolbar_layout.addWidget(self.add_button)

        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.load_data)
        toolbar_layout.addWidget(self.refresh_button)

        layout.addLayout(toolbar_layout)

        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "类型", "键", "值", "排序", "启用", "描述"
        ])

        # 设置表格样式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(1, 150)  # 类型
        self.table.setColumnWidth(2, 200)  # 键
        self.table.setColumnWidth(3, 200)  # 值
        self.table.setColumnWidth(4, 50)  # 排序
        self.table.setColumnWidth(5, 50)  # 启用

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # 操作按钮
        button_layout = QHBoxLayout()

        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self.on_edit)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.on_delete)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def load_data(self):
        """加载数据"""
        try:
            self.all_data = self.logic.get_all_dict_items()
            self.filter_data()
            self.update_type_filter()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据失败: {str(e)}")

    def update_type_filter(self):
        """更新类型筛选下拉框"""
        try:
            types = self.logic.get_all_types()
            self.type_filter.clear()
            self.type_filter.addItem("全部类型", "")
            for type_name in types:
                self.type_filter.addItem(type_name, type_name)
        except Exception as e:
            pass  # 忽略错误

    def filter_data(self):
        """筛选数据"""
        filter_type = self.type_filter.currentData()
        search_text = self.search_edit.text().lower()

        filtered_data = []
        for item in self.all_data:
            # 类型筛选
            if filter_type and item.dict_type != filter_type:
                continue

            # 搜索筛选
            if search_text and (
                    search_text not in item.dict_key.lower() and
                    search_text not in item.dict_value.lower()
            ):
                continue

            filtered_data.append(item)

        self.display_data(filtered_data)

    def display_data(self, data: List[DataDict]):
        """显示数据"""
        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.dict_type))
            self.table.setItem(row, 2, QTableWidgetItem(item.dict_key))
            self.table.setItem(row, 3, QTableWidgetItem(item.dict_value))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.sort_order)))
            self.table.setItem(row, 5, QTableWidgetItem("是" if item.is_active else "否"))
            self.table.setItem(row, 6, QTableWidgetItem(item.description or ""))

            # 设置每行的用户数据
            for col in range(7):
                if self.table.item(row, col):
                    self.table.item(row, col).setData(Qt.UserRole, item)

    def on_add(self):
        """添加数据字典项"""
        if not SessionManager.is_admin():
            QMessageBox.warning(self, "权限不足", "只有管理员才能添加数据字典项")
            return

        dialog = DataDictDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                dict_data = DataDictCreate(**data)
                self.logic.add_dict_item(dict_data)
                self.load_data()
                QMessageBox.information(self, "成功", "添加成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"添加失败: {str(e)}")

    def on_edit(self):
        """编辑数据字典项"""
        if not SessionManager.is_admin():
            QMessageBox.warning(self, "权限不足", "只有管理员才能编辑数据字典项")
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要编辑的数据")
            return

        item = self.table.item(current_row, 0).data(Qt.UserRole)
        dialog = DataDictDialog(self, item)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                dict_data = DataDictUpdate(**data)
                self.logic.update_dict_item(item.id, dict_data)
                self.load_data()
                QMessageBox.information(self, "成功", "更新成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"更新失败: {str(e)}")

    def on_delete(self):
        """删除数据字典项"""
        if not SessionManager.is_admin():
            QMessageBox.warning(self, "权限不足", "只有管理员才能删除数据字典项")
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要删除的数据")
            return

        item = self.table.item(current_row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {item.dict_type} - {item.dict_value} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.logic.delete_dict_item(item.id)
                self.load_data()
                QMessageBox.information(self, "成功", "删除成功")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")
