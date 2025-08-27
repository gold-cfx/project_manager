#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 基础数据模型
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class DateTimeFormatterMixin:
    """日期时间格式化混合类"""

    @classmethod
    def format_value(cls, value: Any) -> Any:
        """格式化值"""
        if isinstance(value, (date, datetime)):
            if isinstance(value, date) and not isinstance(value, datetime):
                # 处理 date 类型
                return value.strftime('%Y-%m-%d')
            else:
                # 处理 datetime 类型
                return value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, Decimal):
            # 处理 Decimal 类型
            return str(float(value))
        elif isinstance(value, dict):
            # 处理字典
            return {k: cls.format_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # 处理列表
            return [cls.format_value(item) for item in value]
        elif isinstance(value, tuple):
            # 处理元组
            return tuple(cls.format_value(item) for item in value)
        else:
            # 其他类型保持不变
            return value

    def format_model(self) -> Dict[str, Any]:
        """格式化模型数据"""
        data = self.dict()
        return self.format_value(data)


class BaseDataModel(BaseModel, DateTimeFormatterMixin):
    """基础数据模型"""

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            date: lambda v: v.strftime('%Y-%m-%d'),
            Decimal: lambda v: str(float(v))
        }

    @classmethod
    def from_orm(cls, obj: Any) -> 'BaseDataModel':
        """从ORM对象创建模型"""
        return super().from_orm(obj)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.dict()

    def to_formatted_dict(self) -> Dict[str, Any]:
        """转换为格式化字典"""
        return self.format_model()
