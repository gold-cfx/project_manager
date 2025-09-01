#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 帮助文档数据访问对象
"""
from typing import Optional

from pymysql.cursors import Cursor, DictCursor

from data.db_connection import with_db_connection
from models.help_doc import HelpDoc, HelpDocCreate, HelpDocUpdate


class HelpDocDAO:
    """帮助文档数据访问对象"""

    def __init__(self):
        self.table_name = "help_docs"
        self.model = HelpDoc

    @with_db_connection(cursor_type=Cursor)
    def insert(self, help_doc_data: HelpDocCreate, cursor: Cursor) -> int:
        """插入新帮助文档"""
        # 使用模型的字段名和占位符
        fields = HelpDocCreate.get_field_names()
        placeholders = HelpDocCreate.get_sql_placeholders()

        sql = f"""
            INSERT INTO {self.table_name} (
                {', '.join(fields)}
            ) VALUES (
                {placeholders}
            )
        """

        # 从模型获取参数值
        params = tuple(getattr(help_doc_data, field) for field in fields)
        cursor.execute(sql, params)
        return cursor.lastrowid if cursor.lastrowid is not None else -1

    @with_db_connection()
    def get_by_id(self, doc_id: int, cursor: DictCursor) -> Optional[HelpDoc]:
        """根据ID获取帮助文档"""
        sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (doc_id,))
        result = cursor.fetchone()
        if result is not None:
            return HelpDoc(**result)
        return None

    @with_db_connection()
    def get_latest(self, cursor: DictCursor) -> Optional[HelpDoc]:
        """获取最新的帮助文档"""
        sql = f"SELECT * FROM {self.table_name} ORDER BY updated_at DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is not None:
            return HelpDoc(**result)
        return None

    @with_db_connection(cursor_type=Cursor)
    def update(self, doc_id: int, help_doc_data: HelpDocUpdate, cursor: Cursor) -> bool:
        """更新帮助文档"""
        # 只更新非空字段
        update_data = help_doc_data.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            return False

        set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values())
        values.append(doc_id)  # 添加WHERE条件的参数

        sql = f"""
            UPDATE {self.table_name} SET
                {set_clause}
            WHERE id = %s
        """

        cursor.execute(sql, tuple(values))
        return cursor.rowcount >= 0

    @with_db_connection(cursor_type=Cursor)
    def delete(self, doc_id: int, cursor: Cursor) -> bool:
        """删除帮助文档"""
        sql = f"DELETE FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (doc_id,))
        return cursor.rowcount >= 0

    def initialize_default_doc(self) -> int:
        """初始化默认帮助文档"""
        # 检查是否已有帮助文档
        existing_doc = self.get_latest()
        if existing_doc:
            return existing_doc.id

        # 创建默认帮助文档
        default_doc = HelpDocCreate(
            title="系统帮助文档",
            content="帮助文档\n使用说明\n\n数据存储说明\n\n使用注意事项\n",
            version="1.0"
        )
        return self.insert(default_doc)
