#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 配置文件
"""
import json
import os
# 确保datetime模块被导入
from datetime import datetime

config_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(config_dir)
config_path = os.path.join(config_dir, 'config.json')

default_db_name = 'research_project'
with open(config_path, 'r') as f:
    config = json.load(f)
# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',  # 数据库主机
    'user': 'root',  # 数据库用户名
    'password': '',  # 数据库密码（请修改为实际密码）
    'db': 'research_project',  # 数据库名
    'charset': 'utf8mb4'  # 字符集
}
DB_CONFIG.update({k: v for k, v in config['database'].items() if not (v is None or v == "")})

# 系统配置
SYSTEM_CONFIG = {
    'system_name': '科研项目管理系统',
    'version': '1.0.0',
    'author': '管理员',
    'copyright': f'© {datetime.now().year} 科研项目管理系统 版权所有',
    'default_reminder_days': 30,  # 默认提前提醒天数
    'max_project_duration': 10,  # 最大项目持续时间（年）
}
DEFAULT_ROOT_DIR = "C:\\Farmar\\code\\office-v3\\attachments"
FILE_SERVER_CONFIG = {
    "enabled": True,
    "host": "127.0.0.1",
    "port": 5001,
    "root_dir": DEFAULT_ROOT_DIR,
    "remote_server": True,
    "remote_host": "",
    "remote_port": 5001
}
FILE_SERVER_CONFIG.update({k: v for k, v in config['file_server'].items() if not (v is None or v == "")})
