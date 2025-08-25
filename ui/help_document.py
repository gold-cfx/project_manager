#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 帮助文档界面
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from data.help_doc_dao import HelpDocDAO
from models.help_doc import HelpDocUpdate


class HelpDocument(QWidget):
    def __init__(self):
        super().__init__()
        self.help_doc_dao = HelpDocDAO()
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
        """从数据库加载帮助文档内容"""
        try:
            help_doc = self.help_doc_dao.get_latest()
            if help_doc:
                self.editor.setText(help_doc.content)
                self.current_doc_id = help_doc.id
            else:
                QMessageBox.warning(self, "警告", "没有找到帮助文档数据")
                self.editor.setText("帮助文档\n使用说明\n\n数据存储说明\n\n使用注意事项\n")
                # 尝试初始化默认文档
                self.current_doc_id = self.help_doc_dao.initialize_default_doc()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载帮助文档失败：{str(e)}")

    def save_help_content(self):
        """保存帮助文档内容到数据库"""
        try:
            content = self.editor.toPlainText()
            
            # 创建更新模型
            help_doc_update = HelpDocUpdate(
                content=content,
                version="1.0"  # 这里可以根据需要更新版本号
            )
            
            if hasattr(self, 'current_doc_id') and self.current_doc_id > 0:
                # 更新现有文档
                if self.help_doc_dao.update(self.current_doc_id, help_doc_update):
                    QMessageBox.information(self, "成功", "帮助文档保存成功！")
                else:
                    QMessageBox.warning(self, "警告", "帮助文档更新失败")
            else:
                # 创建新文档
                from models.help_doc import HelpDocCreate
                help_doc_create = HelpDocCreate(
                    title="系统帮助文档",
                    content=content,
                    version="1.0"
                )
                new_id = self.help_doc_dao.insert(help_doc_create)
                if new_id > 0:
                    self.current_doc_id = new_id
                    QMessageBox.information(self, "成功", "帮助文档创建成功！")
                else:
                    QMessageBox.warning(self, "警告", "帮助文档创建失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存帮助文档失败：{str(e)}")

    def showEvent(self, event):
        """显示时重新加载内容"""
        self.load_help_content()
        super().showEvent(event)