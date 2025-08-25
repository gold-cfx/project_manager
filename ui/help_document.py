#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 帮助文档界面
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTextEdit, QPushButton, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class HelpDocument(QWidget):
    def __init__(self, help_file_path):
        super().__init__()
        self.help_file_path = help_file_path
        self.init_ui()
        self.load_help_content()

    def init_ui(self):
        # 设置布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 添加标题
        title_label = QLabel("帮助文档")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 添加编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("帮助文档内容...")
        self.editor.setFontPointSize(12)
        main_layout.addWidget(self.editor)

        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_help_content)
        button_layout.addWidget(self.save_button)

        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.load_help_content)
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

    def load_help_content(self):
        """加载帮助文档内容"""
        try:
            if os.path.exists(self.help_file_path):
                with open(self.help_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.editor.setText(content)
            else:
                QMessageBox.warning(self, "警告", f"帮助文档文件不存在：{self.help_file_path}")
                self.editor.setText("# 帮助文档\n## 使用说明\n\n## 数据存储说明\n\n## 使用注意事项\n")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载帮助文档失败：{str(e)}")

    def save_help_content(self):
        """保存帮助文档内容"""
        try:
            content = self.editor.toPlainText()
            with open(self.help_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            QMessageBox.information(self, "成功", "帮助文档保存成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存帮助文档失败：{str(e)}")

    def showEvent(self, event):
        """显示时重新加载内容"""
        self.load_help_content()
        super().showEvent(event)