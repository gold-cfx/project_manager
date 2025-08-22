#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目数据访问对象"""
from data.db_connection import with_db_connection
from pymysql.cursors import DictCursor, Cursor


class ProjectDAO:
    """项目数据访问对象"""

    def __init__(self):
        pass

    def insert(self, project_data):
        """插入新项目"""

        def operation(cursor):
            sql = """
                INSERT INTO projects (
                    project_name, leader, phone, email, start_date, end_date,
                    funding_unit, level, funding_amount, currency, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                project_data['project_name'],
                project_data['leader'],
                project_data['phone'],
                project_data['email'],
                project_data['start_date'],
                project_data['end_date'],
                project_data['funding_unit'],
                project_data['level'],
                project_data['funding_amount'],
                project_data['currency'],
                project_data.get('status', '进行中')
            )
            cursor.execute(sql, params)
            return cursor.lastrowid

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else -1

    def get_by_id(self, project_id):
        """根据ID获取项目"""

        def operation(cursor):
            sql = "SELECT * FROM projects WHERE id = %s"
            cursor.execute(sql, (project_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        return result if result is not None else None

    def get_by_name(self, project_name):
        """根据名称获取项目"""

        def operation(cursor):
            sql = "SELECT * FROM projects WHERE project_name = %s"
            cursor.execute(sql, (project_name,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        return result if result is not None else None

    def update(self, project_data):
        """更新项目"""

        def operation(cursor):
            sql = """
                UPDATE projects SET
                    project_name = %s, leader = %s, phone = %s, email = %s,
                    start_date = %s, end_date = %s, funding_unit = %s,
                    level = %s, funding_amount = %s, currency = %s,
                    status = %s
                WHERE id = %s
            """
            params = (
                project_data['project_name'],
                project_data['leader'],
                project_data['phone'],
                project_data['email'],
                project_data['start_date'],
                project_data['end_date'],
                project_data['funding_unit'],
                project_data['level'],
                project_data['funding_amount'],
                project_data['currency'],
                project_data['status'],
                project_data['id']
            )
            cursor.execute(sql, params)
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def delete(self, project_id):
        """删除项目"""

        def operation(cursor):
            sql = "DELETE FROM projects WHERE id = %s"
            cursor.execute(sql, (project_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def list_all(self):
        """列出所有项目"""

        def operation(cursor):
            sql = "SELECT * FROM projects ORDER BY start_date DESC"
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []

    def search(self, conditions):
        """根据条件搜索项目"""

        def operation(cursor):
            sql = "SELECT * FROM projects WHERE 1=1"
            params = []

            if 'project_name' in conditions and conditions['project_name']:
                sql += " AND project_name LIKE %s"
                params.append(f"%{conditions['project_name']}%")

            if 'leader' in conditions and conditions['leader']:
                sql += " AND leader LIKE %s"
                params.append(f"%{conditions['leader']}%")

            if 'start_date' in conditions and conditions['start_date']:
                sql += " AND start_date >= %s"
                params.append(conditions['start_date'])

            if 'end_date' in conditions and conditions['end_date']:
                sql += " AND end_date <= %s"
                params.append(conditions['end_date'])

            if 'funding_unit' in conditions and conditions['funding_unit']:
                sql += " AND funding_unit = %s"
                params.append(conditions['funding_unit'])

            if 'level' in conditions and conditions['level']:
                sql += " AND level = %s"
                params.append(conditions['level'])

            if 'status' in conditions and conditions['status']:
                sql += " AND status = %s"
                params.append(conditions['status'])

            sql += " ORDER BY start_date DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []
