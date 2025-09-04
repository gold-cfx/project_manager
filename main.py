#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
科研项目管理系统 - 主程序入口
"""
import ctypes
import os
import sys

import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from config.settings import ICON_PATH, QSS_PATH
from file_server.start_server import start_file_server
from logic.auto_reminder import auto_reminder
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from utils.logger import get_logger

logger = get_logger(__name__)

# 解决任务栏图标不显示问题
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ccp")

matplotlib.use('Qt5Agg')
plt_font = {'family': 'SimHei', 'size': 10}
matplotlib.rc('font', **plt_font)

# 确保中文正常显示
os.environ['QT_FONT_DPI'] = '96'


def main():
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 启用高DPI图标

    # 设置应用程序图标（任务栏图标）
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    # 加载样式表
    with open(QSS_PATH, 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())

    # 显示登录对话框
    login_dialog = LoginDialog()
    if login_dialog.exec_() == LoginDialog.Accepted:
        current_user = login_dialog.get_current_user()

        # 检查是否为隐藏管理员
        is_hidden_admin = current_user.username == 'cfx'

        # 如果不是隐藏管理员，执行数据初始化和启动服务
        if not is_hidden_admin:
            # 启动文件服务器
            try:
                start_file_server()
                logger.info("文件服务器启动成功")
            except Exception as e:
                logger.error(f"文件服务器启动失败: {str(e)}")
            # 设置主窗口引用并初始化定时提醒
            main_window = MainWindow(current_user)
            main_window.show()
            auto_reminder.set_main_window(main_window)
            auto_reminder.initialize_timer()
        else:
            # 隐藏管理员跳过所有初始化和提醒
            logger.info("隐藏管理员登录，跳过数据初始化和提醒扫描")
            main_window = MainWindow(current_user)
            main_window.show()

        # 运行应用程序
        sys.exit(app.exec_())
    else:
        # 用户取消登录，退出程序
        sys.exit(0)


if __name__ == '__main__':
    main()
