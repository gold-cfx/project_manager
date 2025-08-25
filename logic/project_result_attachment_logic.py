#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果附件业务逻辑
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional

from config.settings import UPLOAD_DIR
from data.project_result_attachment_dao import ProjectResultAttachmentDAO
from models.project_result_attachment import (
    ProjectResultAttachment,
    ProjectResultAttachmentCreate,
    ProjectResultAttachmentUpdate
)

class ProjectResultAttachmentLogic:
    """项目成果附件业务逻辑类"""

    def __init__(self):
        self.dao = ProjectResultAttachmentDAO()
        self.attachment_dir = UPLOAD_DIR
        os.makedirs(self.attachment_dir, exist_ok=True)

    def _generate_file_path(self, project_result_id: int, file_name: str) -> str:
        """生成附件存储路径"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = ''.join(c for c in file_name if c.isalnum() or c in '._- ')
        return os.path.join(
            self.attachment_dir,
            f'result_{project_result_id}',
            f'{timestamp}_{safe_filename}'
        )

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

        # 生成存储路径并确保目录存在
        new_file_path = self._generate_file_path(project_result_id, file_name)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

        # 复制文件到存储位置
        shutil.copy2(file_path, new_file_path)

        # 创建附件记录
        attachment = ProjectResultAttachmentCreate(
            project_result_id=project_result_id,
            file_name=file_name,
            file_path=new_file_path
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

        # 生成新的存储路径
        new_storage_path = self._generate_file_path(
            old_attachment['project_result_id'],
            new_file_name
        )
        os.makedirs(os.path.dirname(new_storage_path), exist_ok=True)

        # 复制新文件到存储位置
        shutil.copy2(new_file_path, new_storage_path)

        # 更新数据库记录
        update_data = ProjectResultAttachmentUpdate(
            file_name=new_file_name,
            file_path=new_storage_path
        )
        success = self.dao.update(attachment_id, update_data)

        if success:
            # 删除旧文件
            try:
                if os.path.exists(old_attachment['file_path']):
                    os.remove(old_attachment['file_path'])
            except OSError:
                pass  # 忽略删除旧文件时的错误

        return success

    def delete_attachment(self, attachment_id: int) -> bool:
        """删除项目成果附件"""
        attachment = self.dao.get_by_id(attachment_id)
        if not attachment:
            return False

        # 删除数据库记录
        success = self.dao.delete(attachment_id)

        if success:
            # 删除文件
            try:
                if os.path.exists(attachment['file_path']):
                    os.remove(attachment['file_path'])
                    # 如果目录为空，删除目录
                    dir_path = os.path.dirname(attachment['file_path'])
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
            except OSError:
                pass  # 忽略文件删除错误

        return success

    def delete_result_attachments(self, project_result_id: int) -> bool:
        """删除项目成果的所有附件"""
        attachments = self.dao.get_by_project_result_id(project_result_id)
        
        # 删除数据库记录
        success = self.dao.delete_by_project_result_id(project_result_id)

        if success:
            # 删除文件和目录
            for attachment in attachments:
                try:
                    if os.path.exists(attachment['file_path']):
                        os.remove(attachment['file_path'])
                except OSError:
                    pass  # 忽略文件删除错误

            # 尝试删除空目录
            try:
                dir_path = os.path.join(self.attachment_dir, f'result_{project_result_id}')
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except OSError:
                pass  # 忽略目录删除错误

        return success