#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目数据模型
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator


class ProjectBase(BaseModel):
    """项目基础模型"""
    project_name: str = Field(..., description="项目名称", max_length=100)
    leader: str = Field(..., description="项目负责人", max_length=50)
    department: str = Field("", description="部门", max_length=50)
    phone: str = Field(..., description="联系电话", max_length=20)
    project_source: str = Field("", description="项目来源", max_length=100)
    project_type: str = Field("", description="项目类型", max_length=50)
    level: str = Field(..., description="项目级别", max_length=50)
    funding_amount: Decimal = Field(..., description="资助金额", ge=0)
    funding_unit: str = Field(..., description="资助单位", max_length=100)
    approval_year: str = Field("", description="批准年份", max_length=4)
    project_number: str = Field("", description="项目编号", max_length=50)
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    status: str = Field("进行中", description="项目状态", max_length=50)

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        """验证结束日期必须晚于开始日期"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于数据库操作"""
        return self.dict()

    @classmethod
    def get_field_names(cls) -> List[str]:
        """获取所有字段名称"""
        return list(cls.__fields__.keys())

    @classmethod
    def get_field_description(cls, field_name: str) -> str:
        """获取字段描述"""
        if field_name in cls.__fields__:
            return cls.__fields__[field_name].field_info.description
        return ""

    @classmethod
    def get_field_type(cls, field_name: str) -> type:
        """获取字段类型"""
        if field_name in cls.__fields__:
            return cls.__fields__[field_name].outer_type_
        return None

    @classmethod
    def get_sql_fields(cls) -> str:
        """获取SQL字段列表"""
        return ", ".join(cls.get_field_names())

    @classmethod
    def get_sql_placeholders(cls) -> str:
        """获取SQL占位符"""
        return ", ".join(['%s'] * len(cls.get_field_names()))


class ProjectCreate(ProjectBase):
    """创建项目模型"""
    pass


class ProjectUpdate(ProjectBase):
    """更新项目模型"""
    project_name: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    funding_unit: Optional[str] = None
    level: Optional[str] = None
    funding_amount: Optional[Decimal] = None
    status: Optional[str] = None


class Project(ProjectBase):
    """项目完整模型"""
    id: int = Field(..., description="项目ID")
    create_time: datetime = Field(None, description="创建时间")
    update_time: datetime = Field(None, description="更新时间")

    class Config:
        orm_mode = True
