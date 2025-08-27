#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果附件模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# 项目成果附件基础模型
class ProjectResultAttachmentBase(BaseModel):
    project_result_id: int
    file_name: str
    file_path: str
    file_server_host: str = ''
    file_server_port: str = ''
    file_storage_directory: str = ''


# 创建项目成果附件模型
class ProjectResultAttachmentCreate(ProjectResultAttachmentBase):
    pass


# 更新项目成果附件模型
class ProjectResultAttachmentUpdate(BaseModel):
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_server_host: Optional[str] = None
    file_server_port: Optional[str] = None
    file_storage_directory: Optional[str] = None


# 项目成果附件模型
class ProjectResultAttachment(ProjectResultAttachmentBase):
    id: int
    upload_time: datetime

    class Config:
        from_attributes = True
