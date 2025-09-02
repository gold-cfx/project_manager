#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 主窗口
"""
import os

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QFrame, QStatusBar, QToolBar, QMessageBox, QAction,
    QSystemTrayIcon, QMenu, QApplication
)

from config.settings import ICON_PATH
from models.user import User
from .data_dict_management import DataDictManagement
from .help_document import HelpDocument
from .project_query import ProjectQuery
from .project_registration import ProjectRegistration
from .reminder_management import ReminderManagement
from .system_settings import SystemSettings


class MainWindow(QMainWindow):
    login_success = pyqtSignal(User)

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
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

        # 创建系统托盘图标
        self.create_system_tray()

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
        user_label = QLabel(
            f'当前用户: {self.current_user.real_name} ({"管理员" if self.current_user.role == "admin" else "用户"})')
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

        # 管理员专用菜单项
        if self.current_user.role == "admin":
            self.add_menu_item('字典管理', 'data_dict_management')

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
        self.system_settings = SystemSettings(self.current_user)
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

    def show_data_dict_management(self):
        # 显示数据字典管理界面（仅管理员）
        if self.current_user.role != "admin":
            QMessageBox.warning(self, '权限不足', '只有管理员才能访问字典管理功能')
            return

        self.clear_content_area()
        self.data_dict_management = DataDictManagement()
        self.content_layout.addWidget(self.data_dict_management)
        self.data_dict_management.show()
        self.status_bar.showMessage('字典管理')

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
        elif data == 'data_dict_management':
            self.show_data_dict_management()
        elif data == 'help_doc':
            self.show_help_document()

    def create_system_tray(self):
        """创建系统托盘图标"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 设置图标路径 - 使用统一的图标文件
        if os.path.exists(ICON_PATH):
            tray_icon = QIcon(ICON_PATH)
            print(f"user icon: {ICON_PATH}")
        else:
            tray_icon = self.style().standardIcon(self.style().SP_ComputerIcon)

        # 统一设置所有图标
        self.tray_icon.setIcon(tray_icon)
        self.setWindowIcon(tray_icon)  # 设置窗口图标（任务栏图标）

        # 创建托盘菜单
        tray_menu = QMenu()

        # 添加菜单项
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        # 设置菜单
        self.tray_icon.setContextMenu(tray_menu)

        # 双击图标显示主窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

        # 设置提示信息
        self.tray_icon.setToolTip("科研项目管理系统")

    def tray_icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()

    def show_normal(self):
        """显示主窗口"""
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """重写关闭事件，最小化到系统托盘"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # 隐藏窗口而不是退出
            self.hide()
            self.tray_icon.showMessage(
                "科研项目管理系统",
                "程序已最小化到系统托盘，双击图标可恢复显示",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()
