#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 配置文件
"""
# 确保datetime模块被导入
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',  # 数据库主机
    'user': 'root',  # 数据库用户名
    'password': '',  # 数据库密码（请修改为实际密码）
    'db': 'research_project',  # 数据库名
    'charset': 'utf8mb4'  # 字符集
}

# 系统配置
SYSTEM_CONFIG = {
    'system_name': '科研项目管理系统',
    'version': '1.0.0',
    'author': '管理员',
    'copyright': f'© {datetime.now().year} 科研项目管理系统 版权所有',
    'default_reminder_days': 30,  # 默认提前提醒天数
    'max_project_duration': 10,  # 最大项目持续时间（年）
}
