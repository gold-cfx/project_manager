# -*- coding: utf-8 -*-
"""
文件服务器包
"""

from .client import FileServerClient, file_server_client
# 从各个模块导入常用类和函数
from .config import FileServerConfig, file_server_config
from .server import FileServer, file_server
from .start_server import (
    FileServerManager,
    file_server_manager,
    start_file_server,
    stop_file_server,
    get_file_server_status
)

# 定义包的版本
__version__ = '1.0.0'

# 定义包的公开API
__all__ = [
    # 配置相关
    'FileServerConfig',
    'file_server_config',

    # 服务器相关
    'FileServer',
    'file_server',
    'FileServerManager',
    'file_server_manager',
    'start_file_server',
    'stop_file_server',
    'get_file_server_status',

    # 客户端相关
    'FileServerClient',
    'file_server_client'
]
