#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据字典工具类
提供从数据字典获取枚举值的方法
"""
from typing import List, Dict

from logic.data_dict_logic import DataDictLogic


class DictUtils:
    """数据字典工具类"""

    _instance = None
    _logic = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DictUtils, cls).__new__(cls)
            cls._logic = DataDictLogic()
        return cls._instance

    def get_project_status(self) -> List[Dict[str, str]]:
        """获取项目状态列表"""
        items = self._logic.get_dict_items("project_status")
        return [{"value": item.dict_value}
                for item in items if item.is_active]

    def get_project_levels(self) -> List[Dict[str, str]]:
        """获取项目级别列表"""

        items = self._logic.get_dict_items("project_level")
        return [{"value": item.dict_value}
                for item in items if item.is_active]

    def get_project_sources(self) -> List[Dict[str, str]]:
        """获取项目来源列表"""
        items = self._logic.get_dict_items("project_source")
        return [{"value": item.dict_value}
                for item in items if item.is_active]

    def get_project_types(self) -> List[Dict[str, str]]:
        """获取项目类型列表"""
        items = self._logic.get_dict_items("project_type")
        return [{"value": item.dict_value}
                for item in items if item.is_active]

    def get_result_types(self) -> List[Dict[str, str]]:
        """获取成果类型列表"""
        items = self._logic.get_dict_items("result_type")
        return [{"value": item.dict_value}
                for item in items if item.is_active]

    def validate_dict_value(self, dict_type: str, dict_value: str) -> bool:
        """验证字典值是否有效"""
        try:
            items = self._logic.get_dict_items(dict_type)
            return any(item.dict_value == dict_value and item.is_active
                       for item in items)
        except:
            return True  # 如果数据字典不可用，允许所有值

    @classmethod
    def get_type_values(cls, type_dict_list, key="value"):
        return [type_dict[key] for type_dict in type_dict_list]


# 全局单例实例
dict_utils = DictUtils()
