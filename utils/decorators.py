#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 装饰器工具
"""
import functools

from models.base import DateTimeFormatterMixin
from utils.logger import get_logger

logger = get_logger(__name__)


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
        return DateTimeFormatterMixin.format_value(result)

    return wrapper


def validate_model_data(model_class):
    """
    验证数据是否符合模型要求
    
    Args:
        model_class: Pydantic模型类
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查所有参数，找到第一个可能是要验证的数据的参数
            for i, arg in enumerate(args):
                if i > 0:  # 跳过self参数
                    # 如果参数是字典或者已经是模型实例，则认为它是要验证的数据
                    if isinstance(arg, dict) or isinstance(arg, model_class):
                        data = arg
                        # 如果数据不是模型实例，尝试创建一个
                        if not isinstance(data, model_class):
                            try:
                                validated_data = model_class(**data)
                                # 替换原始参数
                                args = list(args)
                                args[i] = validated_data
                                args = tuple(args)
                            except Exception as e:
                                raise ValueError(f"数据验证失败: {e}")
                        break
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_operation(operation_name):
    """
    记录操作日志
    
    Args:
        operation_name: 操作名称
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"执行操作: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"操作完成: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"操作失败: {operation_name}, 错误: {e}")
                raise

        return wrapper

    return decorator
