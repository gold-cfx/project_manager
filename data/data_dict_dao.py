#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据字典数据访问对象
"""
from typing import List, Optional, Dict

from pymysql.cursors import Cursor, DictCursor

from data.db_connection import with_db_connection
from models.data_dict import DataDict, DataDictCreate, DataDictUpdate


class DataDictDAO:
    """数据字典数据访问对象"""

    def __init__(self):
        self.table_name = "data_dicts"
        self.model = DataDict

    @with_db_connection(cursor_type=Cursor)
    def insert(self, dict_data: DataDictCreate, cursor: Cursor) -> int:
        """插入新数据字典项"""
        sql = f"""
            INSERT INTO {self.table_name} 
            (dict_type, dict_key, dict_value, sort_order, is_active, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            dict_data.dict_type,
            dict_data.dict_key,
            dict_data.dict_value,
            dict_data.sort_order,
            dict_data.is_active,
            dict_data.description
        ))
        return cursor.lastrowid if cursor.lastrowid is not None else -1

    @with_db_connection()
    def get_by_id(self, dict_id: int, cursor: DictCursor) -> Optional[DataDict]:
        """根据ID获取数据字典项"""
        sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (dict_id,))
        result = cursor.fetchone()
        if result:
            return DataDict(**result)
        return None

    @with_db_connection()
    def get_by_type_and_key(self, dict_type: str, dict_key: str, cursor: DictCursor) -> List[DataDict]:
        """根据类型获取数据字典列表"""
        sql = f"""
            SELECT * FROM {self.table_name} 
            WHERE dict_type = %s AND is_active = 1 AND dict_key = %s 
            ORDER BY sort_order ASC, dict_key ASC
        """
        cursor.execute(sql, (dict_type, dict_key))
        results = cursor.fetchall()
        return [DataDict(**row) for row in results]

    @with_db_connection()
    def get_by_type(self, dict_type: str, cursor: DictCursor) -> List[DataDict]:
        """根据类型获取数据字典列表"""
        sql = f"""
            SELECT * FROM {self.table_name} 
            WHERE dict_type = %s AND is_active = 1 
            ORDER BY sort_order ASC, dict_key ASC
        """
        cursor.execute(sql, (dict_type,))
        results = cursor.fetchall()
        return [DataDict(**row) for row in results]

    @with_db_connection()
    def get_all_types(self, cursor: DictCursor) -> List[str]:
        """获取所有字典类型"""
        sql = f"SELECT DISTINCT dict_type FROM {self.table_name} ORDER BY dict_type"
        cursor.execute(sql)
        results = cursor.fetchall()
        return [row['dict_type'] for row in results]

    @with_db_connection()
    def get_all(self, cursor: DictCursor) -> List[DataDict]:
        """获取所有数据字典项"""
        sql = f"SELECT * FROM {self.table_name} ORDER BY dict_type ASC, sort_order ASC"
        cursor.execute(sql)
        results = cursor.fetchall()
        return [DataDict(**row) for row in results]

    @with_db_connection(cursor_type=Cursor)
    def update(self, dict_id: int, dict_data: DataDictUpdate, cursor: Cursor) -> bool:
        """更新数据字典项"""
        update_data = dict_data.dict(exclude_unset=True)
        if not update_data:
            return False

        set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values())
        values.append(dict_id)

        sql = f"""
            UPDATE {self.table_name} 
            SET {set_clause}
            WHERE id = %s
        """
        cursor.execute(sql, tuple(values))
        return cursor.rowcount > 0

    @with_db_connection(cursor_type=Cursor)
    def delete(self, dict_id: int, cursor: Cursor) -> bool:
        """删除数据字典项"""
        sql = f"DELETE FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (dict_id,))
        return cursor.rowcount > 0

    @with_db_connection()
    def get_dict_map(self, dict_type: str, cursor: DictCursor) -> Dict[str, str]:
        """获取指定类型的字典映射"""
        sql = f"""
            SELECT dict_key, dict_value FROM {self.table_name} 
            WHERE dict_type = %s AND is_active = 1
        """
        cursor.execute(sql, (dict_type,))
        results = cursor.fetchall()
        return {row['dict_key']: row['dict_value'] for row in results}

    def initialize_default_data(self) -> None:
        """初始化默认数据字典数据"""
        default_data = [
            # 项目状态
            {"dict_type": "project_status", "dict_key": "IN_PROGRESS", "dict_value": "进行中", "sort_order": 1},
            {"dict_type": "project_status", "dict_key": "COMPLETED", "dict_value": "已完成", "sort_order": 2},
            {"dict_type": "project_status", "dict_key": "SUSPENDED", "dict_value": "已暂停", "sort_order": 3},
            {"dict_type": "project_status", "dict_key": "CANCELLED", "dict_value": "已取消", "sort_order": 4},

            # 项目级别
            {"dict_type": "project_level", "dict_key": "NATIONAL", "dict_value": "国家级", "sort_order": 1},
            {"dict_type": "project_level", "dict_key": "PROVINCIAL", "dict_value": "省部级", "sort_order": 2},
            {"dict_type": "project_level", "dict_key": "MUNICIPAL", "dict_value": "市级", "sort_order": 3},
            {"dict_type": "project_level", "dict_key": "ENTERPRISE", "dict_value": "企业", "sort_order": 4},
            {"dict_type": "project_level", "dict_key": "OTHER", "dict_value": "其他", "sort_order": 5},

            # 项目来源
            {"dict_type": "project_source", "dict_key": "NATIONAL_NATURAL", "dict_value": "国家自然科学基金",
             "sort_order": 1},
            {"dict_type": "project_source", "dict_key": "NATIONAL_SOCIAL", "dict_value": "国家社会科学基金",
             "sort_order": 2},
            {"dict_type": "project_source", "dict_key": "MINISTRY_EDUCATION", "dict_value": "教育部项目",
             "sort_order": 3},
            {"dict_type": "project_source", "dict_key": "PROVINCE_NATURAL", "dict_value": "省自然科学基金",
             "sort_order": 4},
            {"dict_type": "project_source", "dict_key": "ENTERPRISE_COOPERATION", "dict_value": "企业合作",
             "sort_order": 5},
            {"dict_type": "project_source", "dict_key": "HOSPITAL_INTERNAL", "dict_value": "院内项目", "sort_order": 6},

            # 项目类型
            {"dict_type": "project_type", "dict_key": "NATURAL_SCIENCE", "dict_value": "自然科学类", "sort_order": 1},
            {"dict_type": "project_type", "dict_key": "SOCIAL_SCIENCE", "dict_value": "社会科学类", "sort_order": 2},
            {"dict_type": "project_type", "dict_key": "TECHNOLOGY_DEVELOPMENT", "dict_value": "技术开发类",
             "sort_order": 3},
            {"dict_type": "project_type", "dict_key": "CLINICAL_RESEARCH", "dict_value": "临床研究类", "sort_order": 4},

            # 成果类型
            {"dict_type": "result_type", "dict_key": "PAPER", "dict_value": "论文", "sort_order": 1},
            {"dict_type": "result_type", "dict_key": "PATENT", "dict_value": "专利", "sort_order": 2},
            {"dict_type": "result_type", "dict_key": "SOFTWARE", "dict_value": "软件著作权", "sort_order": 3},
            {"dict_type": "result_type", "dict_key": "AWARD", "dict_value": "获奖", "sort_order": 4},
            {"dict_type": "result_type", "dict_key": "REPORT", "dict_value": "研究报告", "sort_order": 5},
        ]

        for item in default_data:
            if not self.get_by_type_and_key(item["dict_type"], item["dict_key"]):
                dict_data = DataDictCreate(**item)
                self.insert(dict_data)
