#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 主程序入口
"""
import os
import sys

# 设置中文字体支持
import matplotlib
from PyQt5.QtWidgets import QApplication

from data.db_connection import init_database
from file_server.start_server import start_file_server
from logic.auto_reminder import auto_reminder
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

matplotlib.use('Qt5Agg')
plt_font = {'family': 'SimHei', 'size': 10}
matplotlib.rc('font', **plt_font)

# 确保中文正常显示
os.environ['QT_FONT_DPI'] = '96'


def main():
    # 初始化数据库
    init_database()

    # 启动文件服务器
    try:
        start_file_server()
    except Exception as e:
        print(f"文件服务器启动失败: {str(e)}")

    # 创建应用程序
    app = QApplication(sys.argv)

    # 加载样式表
    with open('ui/styles.qss', 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())

    # 显示登录对话框
    login_dialog = LoginDialog()
    if login_dialog.exec_() == LoginDialog.Accepted:
        current_user = login_dialog.get_current_user()
        
        # 创建主窗口
        main_window = MainWindow(current_user)
        main_window.show()

        # 检查并显示自动提醒
        auto_reminder.check_and_show_reminders()

        # 运行应用程序
        sys.exit(app.exec_())
    else:
        # 用户取消登录，退出程序
        sys.exit(0)


if __name__ == '__main__':
    main()
