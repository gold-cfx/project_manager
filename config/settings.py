#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 配置文件
"""
import json
import os
import socket
# 确保datetime模块被导入
from datetime import datetime

from utils.logger import get_logger
from utils.resource_path import get_config_path, get_icon_path

logger = get_logger(__name__)

pod_ip = socket.gethostbyname(socket.gethostname())

# 配置目录定义
config_dir = get_config_path()
config_path = os.path.join(config_dir, 'config.json')

# 备份配置目录
BACKUP_CONFIG_DIR = "C:\\research_project\\config"
os.makedirs(BACKUP_CONFIG_DIR, exist_ok=True)


def get_config_file_path(filename):
    """
    获取配置文件路径，优先使用备份目录中的配置
    
    Args:
        filename: 配置文件名
        
    Returns:
        str: 配置文件完整路径
    """
    backup_path = os.path.join(BACKUP_CONFIG_DIR, filename)
    local_path = os.path.join(config_dir, filename)

    # 如果备份目录存在该文件，优先使用备份目录
    if os.path.exists(backup_path):
        return backup_path
    else:
        return local_path


def load_config_with_backup(filename):
    """
    加载配置文件，支持备份目录优先级
    
    Args:
        filename: 配置文件名
        
    Returns:
        dict: 配置数据
    """
    config_file = get_config_file_path(filename)

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        logger.error(f"加载配置文件 {config_file} 时发生错误: {e}")
        return {}


def save_config_with_backup(filename, config_data):
    """
    保存配置文件到本地和备份目录，支持部分更新
    
    Args:
        filename: 配置文件名
        config_data: 配置数据（可以是部分配置）
    """
    # 先加载现有配置
    existing_config = load_config_with_backup(filename)
    
    # 合并配置数据（避免覆盖未修改的部分）
    def deep_merge(dict1, dict2):
        """深度合并两个字典"""
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                deep_merge(dict1[key], value)
            else:
                dict1[key] = value
    
    deep_merge(existing_config, config_data)
    
    # 保存到本地配置目录
    local_path = os.path.join(config_dir, filename)
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存本地配置文件 {local_path} 时发生错误: {e}")

    # 保存到备份配置目录
    backup_path = os.path.join(BACKUP_CONFIG_DIR, filename)
    try:
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存备份配置文件 {backup_path} 时发生错误: {e}")


# 加载配置，支持备份目录优先级
config = load_config_with_backup('config.json')

default_db_name = 'research_project'

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',  # 数据库主机
    'port': 3306,  # 数据库端口
    'user': 'root',  # 数据库用户名
    'password': '',  # 数据库密码（请修改为实际密码）
    'db_name': 'office',  # 数据库名
    'charset': 'utf8mb4'  # 字符集
}
if 'database' in config:
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


# 使用安全的默认目录
def get_safe_default_directory():
    """获取用户有权限的安全默认存储目录"""
    try:
        # 尝试使用用户文档目录
        import os
        user_docs = os.path.join(os.path.expanduser("~"), "Documents")
        safe_dir = os.path.join(user_docs, "ResearchProject", "attachments")

        # 检查权限
        try:
            os.makedirs(safe_dir, exist_ok=True)
            test_file = os.path.join(safe_dir, '.permission_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return safe_dir
        except (PermissionError, OSError):
            # 如果文档目录也不行，使用当前工作目录
            current_dir = os.path.join(os.getcwd(), "research_project", "attachments")
            return current_dir

    except Exception:
        # 最后fallback到C盘根目录
        return "C:\\research_project\\attachments"


def get_default_log_directory():
    """获取默认日志目录"""
    try:
        log_dir = "C:\\research_project\\log"
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')


# 使用安全的默认目录
DEFAULT_ROOT_DIR = get_safe_default_directory()
DEFAULT_LOG_DIR = get_default_log_directory()

FILE_SERVER_CONFIG = {
    "enabled": True,
    "host": "127.0.0.1",
    "port": 5001,
    "root_dir": DEFAULT_ROOT_DIR,
    "remote_server": True,
    "remote_host": "",
    "remote_port": 5001
}
if 'file_server' in config:
    FILE_SERVER_CONFIG.update({k: v for k, v in config['file_server'].items() if not (v is None or v == "")})

LOG_CONFIG = {
    "log_dir": DEFAULT_LOG_DIR,
    "log_level": "INFO",
    "max_days": 7
}
if 'log_config' in config:
    LOG_CONFIG.update({k: v for k, v in config['log_config'].items() if not (v is None or v == "")})

ICON_PATH = os.path.join(get_icon_path(), "icon.ico")
QSS_PATH = os.path.join(get_icon_path(), "styles.qss")
