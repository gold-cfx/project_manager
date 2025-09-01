#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果附件业务逻辑
"""

import os
from datetime import datetime
from typing import List, Optional

from data.project_result_attachment_dao import ProjectResultAttachmentDAO
from file_server.client import file_server_client
from models.project_result_attachment import (
    ProjectResultAttachment,
    ProjectResultAttachmentCreate,
    ProjectResultAttachmentUpdate
)


class ProjectResultAttachmentLogic:
    """项目成果附件业务逻辑类"""

    def __init__(self):
        self.dao = ProjectResultAttachmentDAO()

    def _generate_sub_dir(self, project_result_id: int) -> str:
        """生成附件存储子目录"""
        return f'result_{project_result_id}'

    def _generate_safe_filename(self, file_name: str) -> str:
        """生成安全的文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 保留文件名中的安全字符
        safe_filename = ''.join(c for c in file_name if c.isalnum() or c in '._- ')
        return f'{timestamp}_{safe_filename}'

    def create_attachment(self, project_result_id: int, file_path: str, file_name: Optional[str] = None) -> int:
        """创建项目成果附件
        
        Args:
            project_result_id: 项目成果ID
            file_path: 原始文件路径
            file_name: 文件名（可选，默认使用原始文件名）
        
        Returns:
            新创建的附件ID
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_name is None:
            file_name = os.path.basename(file_path)

        # 使用文件服务器客户端上传文件
        sub_dir = self._generate_sub_dir(project_result_id)
        result = file_server_client.upload_file(file_path, sub_dir)

        if not result.get('success', False):
            raise Exception(f"文件上传失败: {result.get('message', '未知错误')}")

        # 获取当前文件服务器配置
        from file_server.config import file_server_config
        host, port, _ = file_server_config.get_effective_config()
        file_storage_directory = file_server_config.root_dir

        # 创建附件记录（存储相对路径和文件服务器信息）
        attachment = ProjectResultAttachmentCreate(
            project_result_id=project_result_id,
            file_name=file_name,
            file_path=result['file_path'],
            file_server_host=host,
            file_server_port=str(port),
            file_storage_directory=file_storage_directory
        )
        return self.dao.insert(attachment)

    def get_attachment(self, attachment_id: int) -> Optional[ProjectResultAttachment]:
        """获取项目成果附件"""
        return self.dao.get_by_id(attachment_id)

    def get_attachments_by_result(self, project_result_id: int) -> List[ProjectResultAttachment]:
        """获取项目成果的所有附件"""
        return self.dao.get_by_project_result_id(project_result_id)

    def update_attachment(self, attachment_id: int, new_file_path: str, new_file_name: Optional[str] = None) -> bool:
        """更新项目成果附件
        
        Args:
            attachment_id: 附件ID
            new_file_path: 新文件路径
            new_file_name: 新文件名（可选）
        
        Returns:
            更新是否成功
        """
        if not os.path.exists(new_file_path):
            raise FileNotFoundError(f"文件不存在: {new_file_path}")

        # 获取原有附件信息
        old_attachment = self.dao.get_by_id(attachment_id)
        if not old_attachment:
            return False

        if new_file_name is None:
            new_file_name = os.path.basename(new_file_path)

        # 使用文件服务器客户端上传新文件
        sub_dir = self._generate_sub_dir(old_attachment['project_result_id'])
        result = file_server_client.upload_file(new_file_path, sub_dir)

        if not result.get('success', False):
            raise Exception(f"文件上传失败: {result.get('message', '未知错误')}")

        # 更新数据库记录
        update_data = ProjectResultAttachmentUpdate(
            file_name=new_file_name,
            file_path=result['file_path']
        )
        success = self.dao.update(attachment_id, update_data)

        if success:
            # 删除旧文件，使用附件记录中存储的文件服务器信息
            try:
                from file_server.client import FileServerClient
                # 创建一个临时客户端，使用旧附件记录中的文件服务器信息
                temp_client = FileServerClient(
                    host=old_attachment.get('file_server_host', ''),
                    port=old_attachment.get('file_server_port', ''),
                    root_dir=old_attachment.get('file_storage_directory', '')
                )
                temp_client.delete_file(old_attachment['file_path'])
            except Exception as e:
                print(f"删除旧附件失败: {str(e)}")
                pass  # 忽略删除旧文件时的错误

        return success

    def delete_attachment(self, attachment_id: int) -> bool:
        """删除项目成果附件
        
        Args:
            attachment_id: 附件ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            PermissionError: 当前用户无删除权限
        """
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除项目成果附件")
            
        attachment = self.dao.get_by_id(attachment_id)
        if not attachment:
            return False

        # 删除数据库记录
        success = self.dao.delete(attachment_id)

        if success:
            # 删除文件，使用附件记录中存储的文件服务器信息
            try:
                from file_server.client import FileServerClient
                # 创建一个临时客户端，使用附件记录中的文件服务器信息
                temp_client = FileServerClient(
                    host=attachment.get('file_server_host', ''),
                    port=attachment.get('file_server_port', ''),
                    root_dir=attachment.get('file_storage_directory', '')
                )
                temp_client.delete_file(attachment['file_path'])
            except Exception:
                pass  # 忽略文件删除错误

        return success

    def delete_result_attachments(self, project_result_id: int) -> bool:
        """删除项目成果的所有附件
        
        Args:
            project_result_id: 项目成果ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            PermissionError: 当前用户无删除权限
        """
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除项目成果附件")
            
        attachments = self.dao.get_by_project_result_id(project_result_id)

        # 删除数据库记录
        success = self.dao.delete_by_project_result_id(project_result_id)

        if success:
            # 删除文件，使用每个附件记录中存储的文件服务器信息
            from file_server.client import FileServerClient
            for attachment in attachments:
                try:
                    # 为每个附件创建一个临时客户端，使用其存储的文件服务器信息
                    temp_client = FileServerClient(
                        host=attachment.get('file_server_host', ''),
                        port=attachment.get('file_server_port', ''),
                        root_dir=attachment.get('file_storage_directory', '')
                    )
                    temp_client.delete_file(attachment['file_path'])
                except Exception as e:
                    print(f"删除附件失败: {str(e)}")
                    pass  # 忽略文件删除错误

        return success

    def download_attachment(self, attachment_id: int, save_dir: str = '') -> Optional[bool]:
        """下载项目成果附件
        
        Args:
            attachment_id: 附件ID
            save_dir: 保存目录（可选）
        
        Returns:
            下载的文件路径，如果失败则返回None
        """
        attachment = self.dao.get_by_id(attachment_id)
        if not attachment:
            return False

        try:
            from file_server.client import FileServerClient
            # 创建一个临时客户端，使用附件记录中的文件服务器信息
            temp_client = FileServerClient(
                host=attachment.get('file_server_host', ''),
                port=attachment.get('file_server_port', ''),
                root_dir=attachment.get('file_storage_directory', '')
            )

            # 先使用相同的临时客户端检查文件是否存在
            if not temp_client.check_file_exists(attachment['file_path']):
                print(f"附件文件在数据库配置的文件服务器上不存在: {attachment['file_path']}")

                # 使用当前系统配置的文件服务再试一次
                print(f"尝试使用当前系统配置的文件服务下载附件: {attachment['file_path']}")
                # 使用全局的file_server_client，它使用当前系统配置
                success, error = file_server_client.download_file(attachment['file_path'], save_dir)
                if success:
                    print(f"使用系统配置的文件服务下载附件成功")
                    return success
                else:
                    print(f"使用系统配置的文件服务下载附件失败: {error}")
                    return False

            # 文件存在，执行下载
            success, error = temp_client.download_file(attachment['file_path'], save_dir)
            return success
        except Exception as e:
            print(f"下载附件失败: {str(e)}")
            return False

    def check_attachment_exists(self, attachment_id: int) -> bool:
        """检查附件是否存在
        
        Args:
            attachment_id: 附件ID
        
        Returns:
            附件是否存在
        """
        attachment = self.dao.get_by_id(attachment_id)
        if not attachment:
            return False

        try:
            from file_server.client import FileServerClient
            # 创建一个临时客户端，使用附件记录中的文件服务器信息
            temp_client = FileServerClient(
                host=attachment.get('file_server_host', ''),
                port=attachment.get('file_server_port', ''),
                root_dir=attachment.get('file_storage_directory', '')
            )
            return temp_client.check_file_exists(attachment['file_path'])
        except Exception as e:
            print(f"检查附件存在失败: {str(e)}")
            return False
