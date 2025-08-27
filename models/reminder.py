#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 提醒数据模型
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import Field, validator

from models.base import BaseDataModel


class ReminderType(str, Enum):
    """提醒类型枚举"""
    PROJECT_START = "项目开始"
    PROJECT_END = "项目结束"
    CUSTOM = "自定义"


class ReminderWay(str, Enum):
    """提醒方式枚举"""
    SYSTEM = "系统提醒"
    EMAIL = "邮件(暂不支持)"
    ALL = "全部"


class ReminderStatus(str, Enum):
    """提醒状态枚举"""
    UNREAD = "未读"
    READ = "已读"
    PROCESSED = "已处理"


class ReminderBase(BaseDataModel):
    """提醒基础模型"""
    project_id: int = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称", max_length=100)
    reminder_type: ReminderType = Field(..., description="提醒类型")
    days_before: int = Field(0, description="提前天数", ge=0)
    reminder_way: ReminderWay = Field(ReminderWay.SYSTEM, description="提醒方式")
    content: str = Field("", description="提醒内容", max_length=500)
    start_date: date = Field(..., description="开始日期")
    status: ReminderStatus = Field(ReminderStatus.UNREAD, description="提醒状态")

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


class ReminderCreate(ReminderBase):
    """创建提醒模型"""
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")

    @validator('start_date')
    def validate_start_date(cls, v):
        """验证开始日期"""
        if v < date.today():
            raise ValueError('提醒开始日期不能早于今天')
        return v


class ReminderUpdate(BaseDataModel):
    """更新提醒模型"""
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    reminder_type: Optional[ReminderType] = None
    days_before: Optional[int] = None
    reminder_way: Optional[ReminderWay] = None
    content: Optional[str] = None
    start_date: Optional[date] = None
    status: Optional[ReminderStatus] = None

    @validator('start_date')
    def validate_start_date(cls, v):
        """验证开始日期"""
        if v and v < date.today():
            raise ValueError('提醒开始日期不能早于今天')
        return v


class Reminder(ReminderBase):
    """提醒完整模型"""
    id: int = Field(..., description="提醒ID")
    create_time: datetime = Field(..., description="创建时间")

    class Config:
        orm_mode = True
