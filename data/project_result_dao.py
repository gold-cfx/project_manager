#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果数据访问对象
"""
from typing import List, Optional

from data.db_connection import with_db_connection
from models.project_result import ProjectResult, ProjectResultCreate, ProjectResultUpdate


class ProjectResultDAO:
    """项目成果数据访问对象"""

    def __init__(self):
        self.table_name = "project_result"
        self.model = ProjectResult

    def insert(self, result_data: ProjectResultCreate) -> int:
        """插入新项目成果"""

        def operation(cursor):
            # 使用模型的字段名和占位符
            fields = ["project_id", "type", "name", "date"]
            placeholders = ", ".join(["%s"] * len(fields))

            sql = f"""
                INSERT INTO {self.table_name} (
                    {', '.join(fields)}
                ) VALUES (
                    {placeholders}
                )
            """

            # 从模型获取参数值
            params = (
                result_data.project_id,
                result_data.type,
                result_data.name,
                result_data.date
            )
            cursor.execute(sql, params)
            return cursor.lastrowid

        result = with_db_connection(operation)
        return result if result is not None else -1

    def get_by_id(self, result_id: int) -> Optional[ProjectResult]:
        """根据ID获取项目成果"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (result_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        if result is not None:
            return ProjectResult(**result)
        return None

    def get_by_project_id(self, project_id: int) -> List[ProjectResult]:
        """根据项目ID获取项目成果"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE project_id = %s ORDER BY date DESC"
            cursor.execute(sql, (project_id,))
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [ProjectResult(**item) for item in results]
        return []

    def update(self, result_id: int, result_data: ProjectResultUpdate) -> bool:
        """更新项目成果"""

        def operation(cursor):
            # 获取非空字段和值
            update_fields = []
            params = []

            # 检查每个字段是否有值
            if result_data.project_id is not None:
                update_fields.append("project_id = %s")
                params.append(result_data.project_id)
            if result_data.type is not None:
                update_fields.append("type = %s")
                params.append(result_data.type)
            if result_data.name is not None:
                update_fields.append("name = %s")
                params.append(result_data.name)
            if result_data.date is not None:
                update_fields.append("date = %s")
                params.append(result_data.date)

            # 如果没有字段需要更新，返回True
            if not update_fields:
                return True

            # 构建SQL语句
            sql = f"""
                UPDATE {self.table_name}
                SET {', '.join(update_fields)}
                WHERE id = %s
            """

            # 添加ID参数
            params.append(result_id)

            # 执行更新
            cursor.execute(sql, tuple(params))
            return cursor.rowcount >= 0

        result = with_db_connection(operation)
        return result if result is not None else False

    def delete(self, result_id: int) -> bool:
        """删除项目成果"""

        def operation(cursor):
            sql = f"DELETE FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (result_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation)
        return result if result is not None else False

    def delete_by_project_id(self, project_id: int) -> bool:
        """根据项目ID删除所有项目成果"""

        def operation(cursor):
            sql = f"DELETE FROM {self.table_name} WHERE project_id = %s"
            cursor.execute(sql, (project_id,))
            return cursor.rowcount >= 0  # 即使没有记录被删除也返回True

        result = with_db_connection(operation)
        return result if result is not None else False
