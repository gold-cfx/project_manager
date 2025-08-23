#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果数据模型
"""
import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator


class ProjectResultType(str, Enum):
    """项目成果类型枚举"""
    PAPER = "论文"
    PATENT = "专利"
    AWARD = "奖项"
    STANDARD = "标准"
    SOFTWARE = "软件"
    OTHER = "其他"


class ProjectResultBase(BaseModel):
    """项目成果基础模型"""
    project_id: int = Field(..., description="项目ID")
    type: ProjectResultType = Field(..., description="成果类型")
    name: str = Field(..., description="成果名称", max_length=255)
    date: datetime.date = Field(..., description="发表/获得日期")


class ProjectResultCreate(ProjectResultBase):
    """创建项目成果模型"""
    pass


class ProjectResultUpdate(ProjectResultBase):
    """更新项目成果模型"""
    project_id: Optional[int] = None
    type: Optional[ProjectResultType] = None
    name: Optional[str] = None
    date: Optional[datetime.date] = None


class ProjectResult(ProjectResultBase):
    """项目成果完整模型"""
    id: int = Field(..., description="成果ID")

    class Config:
        orm_mode = True