#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目登记界面
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.data_editor import ProjectEditor


class ProjectRegistration(ProjectEditor):
    def __init__(self):
        # 调用父类构造函数，不传入项目ID表示新建项目
        super().__init__(project_id=None)
        # 修改标题为项目登记
        self.set_title('项目登记')
        # 设置状态标签初始文本
        self.base_editor.status_label.setText('请填写项目信息')
        self.base_editor.status_label.setStyleSheet('color: black')

    def set_title(self, title):
        # 查找并修改标题标签
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            widget = item.widget()
            if isinstance(widget, QLabel) and widget.font().pointSize() == 16:
                widget.setText(title)
                break

    def save_project(self):
        # 重写保存方法，添加保存成功后的重置表单逻辑
        if self.validate_form():
            project_data = self.collect_form_data()
            success = self.project_logic.save_project(project_data)
            if success:
                QMessageBox.information(self, '保存成功', '项目信息已成功保存')
                self.reset_form()
            else:
                QMessageBox.warning(self, '保存失败', '项目信息保存失败，请重试')

    def reset_form(self):
        # 重置表单
        super().reset_form()
        # 额外重置状态标签
        self.base_editor.status_label.setText('请填写项目信息')
        self.base_editor.status_label.setStyleSheet('color: black')
