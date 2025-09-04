#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
目录工具类
提供目录权限检查和修改存储目录的功能
"""

import os
import sys

from PyQt5.QtWidgets import (QFileDialog, QMessageBox)

from config.settings import save_config_with_backup, load_config_with_backup
from utils.logger import get_logger

logger = get_logger(__name__)


class DirectoryManager:
    """目录管理工具类"""

    @staticmethod
    def check_and_prompt_directory_change(parent_widget=None, current_dir=None):
        """
        检查当前目录权限，如果无权限则提示用户修改
        
        Args:
            parent_widget: 父窗口组件
            current_dir: 当前目录路径
            
        Returns:
            str: 新的目录路径，如果用户取消则返回None
        """
        from file_server.config import file_server_config

        if current_dir is None:
            current_dir = file_server_config.root_dir

        # 检查当前目录权限
        has_permission, error_msg = file_server_config.check_directory_permission(current_dir)

        if has_permission:
            return current_dir

        # 无权限，提示用户
        msg = f"当前文件存储目录权限不足：\n\n{error_msg}\n\n请选择以下操作："

        reply = QMessageBox.critical(
            parent_widget,
            "目录权限问题",
            msg,
            QMessageBox.Open | QMessageBox.Cancel,
            QMessageBox.Open
        )

        if reply == QMessageBox.Open:
            new_dir = DirectoryManager.select_new_directory(parent_widget, current_dir)
            if new_dir:
                success = DirectoryManager.update_storage_directory(new_dir, parent_widget)
                if success:
                    return new_dir

        return None

    @staticmethod
    def select_new_directory(parent_widget=None, current_dir=None):
        """
        让用户选择新的存储目录
        
        Args:
            parent_widget: 父窗口组件
            current_dir: 当前目录路径
            
        Returns:
            str: 用户选择的新目录路径，如果取消则返回None
        """
        if current_dir is None:
            from file_server.config import file_server_config
            current_dir = file_server_config.root_dir

        # 确保当前目录存在
        if not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")

        new_dir = QFileDialog.getExistingDirectory(
            parent_widget,
            "选择新的文件存储目录",
            current_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if new_dir:
            # 检查新目录的权限
            from file_server.config import file_server_config
            has_permission, error_msg = file_server_config.check_directory_permission(new_dir)

            if not has_permission:
                QMessageBox.warning(
                    parent_widget,
                    "目录权限不足",
                    f"选择的目录 '{new_dir}' 没有写入权限，请选择其他目录。"
                )
                return DirectoryManager.select_new_directory(parent_widget, new_dir)

            return new_dir

        return None

    @staticmethod
    def update_storage_directory(new_dir, parent_widget=None):
        """
        更新文件存储目录配置
        
        Args:
            new_dir: 新的存储目录路径
            parent_widget: 父窗口组件
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 加载当前配置
            config = load_config_with_backup('config.json')

            # 更新文件服务器配置
            if 'file_server' not in config:
                config['file_server'] = {}

            config['file_server']['root_dir'] = new_dir

            # 保存配置
            save_config_with_backup('config.json', config)

            # 确保新目录存在
            os.makedirs(new_dir, exist_ok=True)

            QMessageBox.information(
                parent_widget,
                "目录更新成功",
                f"文件存储目录已更新为：\n{new_dir}\n\n请重新启动程序以使更改生效。"
            )

            logger.info(f"文件存储目录已更新为: {new_dir}")
            return True

        except Exception as e:
            logger.error(f"更新存储目录失败: {e}")
            QMessageBox.critical(
                parent_widget,
                "更新失败",
                f"更新存储目录失败：{str(e)}"
            )
            return False

    @staticmethod
    def get_user_documents_path():
        """获取用户的文档目录路径"""
        if sys.platform == "win32":
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:
            return os.path.join(os.path.expanduser("~"), "Documents")

    @staticmethod
    def get_safe_default_directory():
        """获取安全的默认存储目录"""
        user_docs = DirectoryManager.get_user_documents_path()
        safe_dir = os.path.join(user_docs, "ResearchProject", "attachments")
        return safe_dir


# 便捷函数
def check_and_fix_directory_permission(parent_widget=None):
    """
    检查并修复目录权限问题
    
    Args:
        parent_widget: 父窗口组件
        
    Returns:
        bool: 是否已解决权限问题
    """
    from file_server.config import file_server_config

    current_dir = file_server_config.root_dir
    new_dir = DirectoryManager.check_and_prompt_directory_change(parent_widget, current_dir)

    return new_dir is not None
