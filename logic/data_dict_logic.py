#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据字典业务逻辑
"""
from typing import List, Dict, Any

from data.data_dict_dao import DataDictDAO
from models.data_dict import DataDict, DataDictCreate, DataDictUpdate
from utils.decorators import log_operation
from utils.session import SessionManager


class DataDictLogic:
    """数据字典业务逻辑类"""

    def __init__(self):
        self.dao = DataDictDAO()

    @log_operation("添加数据字典项")
    def add_dict_item(self, dict_data: DataDictCreate) -> int:
        """添加数据字典项"""
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能添加数据字典项")

        # 检查是否已存在相同的key
        existing_items = self.dao.get_by_type(dict_data.dict_type)
        for item in existing_items:
            if item.dict_key == dict_data.dict_key:
                raise ValueError(f"字典类型 {dict_data.dict_type} 中已存在键 {dict_data.dict_key}")

        return self.dao.insert(dict_data)

    @log_operation("更新数据字典项")
    def update_dict_item(self, dict_id: int, dict_data: DataDictUpdate) -> bool:
        """更新数据字典项"""
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能更新数据字典项")

        return self.dao.update(dict_id, dict_data)

    @log_operation("删除数据字典项")
    def delete_dict_item(self, dict_id: int) -> bool:
        """删除数据字典项"""
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除数据字典项")

        return self.dao.delete(dict_id)

    def get_dict_items(self, dict_type: str) -> List[DataDict]:
        """获取指定类型的数据字典列表"""
        return self.dao.get_by_type(dict_type)

    def get_all_dict_items(self) -> List[DataDict]:
        """获取所有数据字典项"""
        return self.dao.get_all()

    def get_all_types(self) -> List[str]:
        """获取所有字典类型"""
        return self.dao.get_all_types()

    def get_dict_map(self, dict_type: str) -> Dict[str, str]:
        """获取指定类型的字典映射"""
        return self.dao.get_dict_map(dict_type)

    def initialize_default_data(self) -> None:
        """初始化默认数据字典数据"""
        self.dao.initialize_default_data()

    def get_project_status_options(self) -> List[Dict[str, Any]]:
        """获取项目状态选项"""
        items = self.dao.get_by_type("project_status")
        return [{"key": item.dict_key, "value": item.dict_value} for item in items]

    def get_project_level_options(self) -> List[Dict[str, Any]]:
        """获取项目级别选项"""
        items = self.dao.get_by_type("project_level")
        return [{"key": item.dict_key, "value": item.dict_value} for item in items]

    def get_project_source_options(self) -> List[Dict[str, Any]]:
        """获取项目来源选项"""
        items = self.dao.get_by_type("project_source")
        return [{"key": item.dict_key, "value": item.dict_value} for item in items]

    def get_project_type_options(self) -> List[Dict[str, Any]]:
        """获取项目类型选项"""
        items = self.dao.get_by_type("project_type")
        return [{"key": item.dict_key, "value": item.dict_value} for item in items]

    def get_result_type_options(self) -> List[Dict[str, Any]]:
        """获取成果类型选项"""
        items = self.dao.get_by_type("result_type")
        return [{"key": item.dict_key, "value": item.dict_value} for item in items]
