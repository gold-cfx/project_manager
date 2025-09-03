# -*- coding: utf-8 -*-
"""
资源路径管理工具
用于处理PyInstaller打包后的资源路径问题
"""

import os
import sys


def get_resource_path(relative_path):
    """
    获取资源的绝对路径
    在开发环境和打包环境中都能正确工作
    
    Args:
        relative_path: 相对路径
        
    Returns:
        str: 资源的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时路径
        base_path = sys._MEIPASS
    else:
        # 开发环境中的当前目录
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)


def get_config_path():
    """获取配置文件目录路径"""
    return get_resource_path('config_file')


def get_help_path():
    """获取帮助文档目录路径"""
    return get_resource_path('help')


def get_icon_path():
    """获取图标目录路径"""
    return get_resource_path('icon')


def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        get_config_path(),
        get_help_path(),
        get_icon_path(),
    ]

    for dir_path in dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                pass  # 目录已存在或无法创建
