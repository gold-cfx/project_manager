#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 帮助文档数据模型
"""
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from .base import BaseDataModel


class HelpDocBase(BaseModel):
    """帮助文档基础模型"""
    title: str = Field(..., description="文档标题", max_length=100)
    content: str = Field(..., description="文档内容")
    version: str = Field("1.0", description="文档版本", max_length=20)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于数据库操作"""
        return self.dict()

    @classmethod
    def get_field_names(cls) -> list:
        """获取所有字段名称"""
        return list(cls.__fields__.keys())

    @classmethod
    def get_sql_fields(cls) -> str:
        """获取SQL字段列表"""
        return ", ".join(cls.get_field_names())

    @classmethod
    def get_sql_placeholders(cls) -> str:
        """获取SQL占位符"""
        return ", ".join(['%s'] * len(cls.get_field_names()))


class HelpDocCreate(HelpDocBase):
    """创建帮助文档模型"""
    pass


class HelpDocUpdate(HelpDocBase):
    """更新帮助文档模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None


class HelpDoc(HelpDocBase, BaseDataModel):
    """帮助文档完整模型"""
    id: int = Field(..., description="文档ID")

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj: Any) -> 'HelpDoc':
        """从ORM对象创建模型"""
        return super().from_orm(obj)

    def to_formatted_dict(self) -> Dict[str, Any]:
        """转换为格式化字典"""
        return self.format_model()
