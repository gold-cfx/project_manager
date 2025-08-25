#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 主窗口
"""
import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QStatusBar, QToolBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from .project_registration import ProjectRegistration
from .project_query import ProjectQuery
from .reminder_management import ReminderManagement
from .system_settings import SystemSettings
from .help_document import HelpDocument


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('科研项目管理系统')
        self.setMinimumSize(1366, 768)

        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # 创建顶部工具栏
        self.create_toolbar()

        # 创建左侧菜单栏
        self.create_sidebar()

        # 创建主内容区域
        self.create_content_area()

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')

        # 初始显示项目登记界面
        self.show_project_registration()

    def create_toolbar(self):
        toolbar = QToolBar('顶部工具栏')
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # 添加标题标签
        title_label = QLabel('科研项目管理系统')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        toolbar.addWidget(title_label)

        # 添加分隔符
        toolbar.addSeparator()

        # 添加用户信息
        user_label = QLabel('当前用户: 管理员')
        toolbar.addWidget(user_label)

    def create_sidebar(self):
        # 创建侧边栏框架
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName('sidebar')
        sidebar_frame.setMinimumWidth(180)
        sidebar_frame.setMaximumWidth(220)
        sidebar_layout = QVBoxLayout(sidebar_frame)

        # 创建功能菜单列表
        self.menu_list = QListWidget()
        self.menu_list.setObjectName('menuList')
        self.menu_list.setSpacing(2)

        # 添加菜单项
        self.add_menu_item('项目登记', 'project_registration')
        self.add_menu_item('项目查询', 'project_query')
        self.add_menu_item('提醒管理', 'reminder_management')
        self.add_menu_item('系统设置', 'system_settings')
        self.add_menu_item('帮助文档', 'help_doc')

        # 连接菜单点击信号
        self.menu_list.itemClicked.connect(self.on_menu_clicked)

        # 添加到布局
        sidebar_layout.addWidget(QLabel('功能菜单'))
        sidebar_layout.addWidget(self.menu_list)
        sidebar_layout.addStretch()

        # 添加到主布局
        self.main_layout.addWidget(sidebar_frame)

    def add_menu_item(self, text, data):
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, data)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.menu_list.addItem(item)

    def create_content_area(self):
        # 创建内容区域框架
        self.content_frame = QFrame()
        self.content_frame.setObjectName('contentArea')
        self.content_layout = QVBoxLayout(self.content_frame)

        # 添加到主布局
        self.main_layout.addWidget(self.content_frame, 1)

    def clear_content_area(self):
        # 清空内容区域
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                self.content_layout.removeWidget(widget)

    def show_project_registration(self):
        # 显示项目登记界面
        self.clear_content_area()
        self.project_registration = ProjectRegistration()
        self.content_layout.addWidget(self.project_registration)
        self.project_registration.show()
        self.status_bar.showMessage('项目登记')

    def show_project_query(self):
        # 显示项目查询界面
        self.clear_content_area()
        self.project_query = ProjectQuery()
        self.content_layout.addWidget(self.project_query)
        self.project_query.show()
        self.status_bar.showMessage('项目查询')

    def show_reminder_management(self):
        # 显示提醒管理界面
        self.clear_content_area()
        self.reminder_management = ReminderManagement()
        self.content_layout.addWidget(self.reminder_management)
        self.reminder_management.show()
        self.status_bar.showMessage('提醒管理')

    def show_system_settings(self):
        # 显示系统设置界面
        self.clear_content_area()
        self.system_settings = SystemSettings()
        self.content_layout.addWidget(self.system_settings)
        self.system_settings.show()
        self.status_bar.showMessage('系统设置')

    def show_help_document(self):
        # 显示帮助文档界面
        self.clear_content_area()
        self.help_document = HelpDocument()
        self.content_layout.addWidget(self.help_document)
        self.help_document.show()
        self.status_bar.showMessage('帮助文档')

    def on_menu_clicked(self, item):
        # 处理菜单点击事件
        data = item.data(Qt.UserRole)
        if data == 'project_registration':
            self.show_project_registration()
        elif data == 'project_query':
            self.show_project_query()
        elif data == 'reminder_management':
            self.show_reminder_management()
        elif data == 'system_settings':
            self.show_system_settings()
        elif data == 'help_doc':
            self.show_help_document()
