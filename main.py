#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 主程序入口
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from data.db_connection import init_database

# 设置中文字体支持
import matplotlib

matplotlib.use('Qt5Agg')
plt_font = {'family': 'SimHei', 'size': 10}
matplotlib.rc('font', **plt_font)

# 确保中文正常显示
os.environ['QT_FONT_DPI'] = '96'


def main():
    # 初始化数据库
    init_database()

    # 创建应用程序
    app = QApplication(sys.argv)

    # 加载样式表
    with open('ui/styles.qss', 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
