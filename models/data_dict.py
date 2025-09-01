#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据字典模型
用于统一管理枚举类型的数据
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DictType(str, Enum):
    """字典类型枚举"""
    PROJECT_STATUS = "project_status"  # 项目状态
    PROJECT_LEVEL = "project_level"    # 项目级别
    PROJECT_SOURCE = "project_source"  # 项目来源
    PROJECT_TYPE = "project_type"      # 项目类型
    RESULT_TYPE = "result_type"         # 成果类型


class DataDictBase(BaseModel):
    """数据字典基础模型"""
    dict_type: str = Field(..., description="字典类型", max_length=50)
    dict_key: str = Field(..., description="字典键", max_length=50)
    dict_value: str = Field(..., description="字典值", max_length=100)
    sort_order: int = Field(0, description="排序顺序")
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述", max_length=200)


class DataDictCreate(DataDictBase):
    """创建数据字典模型"""
    pass


class DataDictUpdate(BaseModel):
    """更新数据字典模型"""
    dict_value: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class DataDict(DataDictBase):
    """数据字典完整模型"""
    id: int = Field(..., description="字典ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    class Config:
        orm_mode = True