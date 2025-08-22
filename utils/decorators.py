#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 装饰器工具
"""
from datetime import date, datetime
from decimal import Decimal
import functools


def format_datetime_in_result(func):
    """
    格式化数据库操作结果中的数据
    - datetime.date 格式化为 'xxxx-xx-xx'
    - datetime.datetime 格式化为 'xxxx-xx-xx ss:ss:ss'
    - Decimal 类型转换为 float 类型
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return format_result(result)
    return wrapper


def format_result(data):
    """递归处理结果中的数据格式"""
    if isinstance(data, (date, datetime, )):
        if isinstance(data, date) and not isinstance(data, datetime):
            # 处理 date 类型
            return data.strftime('%Y-%m-%d')
        else:
            # 处理 datetime 类型
            return data.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, Decimal):
        # 处理 Decimal 类型
        return str(float(data))
    elif isinstance(data, dict):
        # 处理字典
        return {k: format_result(v) for k, v in data.items()}
    elif isinstance(data, list):
        # 处理列表
        return [format_result(item) for item in data]
    elif isinstance(data, tuple):
        # 处理元组
        return tuple(format_result(item) for item in data)
    else:
        # 其他类型保持不变
        return data