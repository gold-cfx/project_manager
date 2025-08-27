#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目数据访问对象
"""
from typing import List, Optional, Dict, Any

from pymysql.cursors import Cursor

from data.db_connection import with_db_connection
from models.project import Project, ProjectCreate, ProjectUpdate, ProjectStatus


class ProjectDAO:
    """项目数据访问对象"""

    def __init__(self):
        self.table_name = "projects"
        self.model = Project

    def insert(self, project_data: ProjectCreate) -> int:
        """插入新项目"""

        def operation(cursor):
            # 使用模型的字段名和占位符
            fields = ProjectCreate.get_field_names()
            placeholders = ProjectCreate.get_sql_placeholders()

            sql = f"""
                INSERT INTO {self.table_name} (
                    {', '.join(fields)}
                ) VALUES (
                    {placeholders}
                )
            """

            # 从模型获取参数值
            params = tuple(getattr(project_data, field) for field in fields)
            cursor.execute(sql, params)
            return cursor.lastrowid

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else -1

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """根据ID获取项目"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (project_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        if result is not None:
            return Project(**result)
        return None

    def get_by_name(self, project_name: str) -> Optional[Project]:
        """根据名称获取项目"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE project_name = %s"
            cursor.execute(sql, (project_name,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        if result is not None:
            return Project(**result)
        return None

    def update(self, project_id: int, project_data: ProjectUpdate) -> bool:
        """更新项目"""

        def operation(cursor):
            # 只更新非空字段
            update_data = project_data.dict(exclude_unset=True, exclude_none=True)
            if not update_data:
                return False

            set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
            values = list(update_data.values())
            values.append(project_id)  # 添加WHERE条件的参数

            sql = f"""
                UPDATE {self.table_name} SET
                    {set_clause}
                WHERE id = %s
            """

            cursor.execute(sql, tuple(values))
            return cursor.rowcount >= 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def delete(self, project_id: int) -> bool:
        """删除项目"""

        def operation(cursor):
            sql = f"DELETE FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (project_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def get_all(self) -> List[Project]:
        """获取所有项目"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} ORDER BY id DESC"
            cursor.execute(sql)
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Project(**item) for item in results]
        return []

    def search(self, criteria: Dict[str, Any]) -> List[Project]:
        """根据条件搜索项目"""

        def operation(cursor):
            # 构建查询条件
            conditions = []
            params = []

            for field, value in criteria.items():
                if value is not None:
                    if field == 'status' and isinstance(value, ProjectStatus):
                        value = value.value

                    if isinstance(value, str) and '%' in value:
                        conditions.append(f"{field} LIKE %s")
                    else:
                        conditions.append(f"{field} = %s")
                    params.append(value)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            sql = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY id DESC"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Project(**item) for item in results]
        return []

    def count_by_status(self) -> Dict[str, int]:
        """统计各状态项目数量"""

        def operation(cursor):
            sql = f"SELECT status, COUNT(*) as count FROM {self.table_name} GROUP BY status"
            cursor.execute(sql)
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return {item['status']: item['count'] for item in results}
        return {}
