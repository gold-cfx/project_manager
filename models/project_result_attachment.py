#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果附件模型
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# 项目成果附件基础模型
class ProjectResultAttachmentBase(BaseModel):
    project_result_id: int
    file_name: str
    file_path: str

# 创建项目成果附件模型
class ProjectResultAttachmentCreate(ProjectResultAttachmentBase):
    pass

# 更新项目成果附件模型
class ProjectResultAttachmentUpdate(BaseModel):
    file_name: Optional[str] = None
    file_path: Optional[str] = None

# 项目成果附件模型
class ProjectResultAttachment(ProjectResultAttachmentBase):
    id: int
    upload_time: datetime

    class Config:
        from_attributes = True