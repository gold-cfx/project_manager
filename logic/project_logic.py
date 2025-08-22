#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目业务逻辑"""
from data.db_connection import with_db_connection
from utils.validator import Validator, validate_project_data
from pymysql.cursors import DictCursor, Cursor
from logic.reminder_logic import ReminderLogic


class ProjectLogic:
    def __init__(self):
        pass

    def save_project(self, project_data):
        """保存项目信息"""
        # 验证项目数据
        if not validate_project_data(project_data):
            return False

        def operation(cursor):
            # 插入项目基本信息
            project_sql = """
                INSERT INTO projects (
                    project_name, leader, department, phone, project_source, project_type,
                    level, funding_amount, funding_unit, approval_year,
                    project_number, start_date, end_date, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            project_params = (
                project_data['project_name'],
                project_data['leader'],
                project_data['department'],
                project_data['phone'],
                project_data['project_source'],
                project_data['project_type'],
                project_data['level'],
                project_data['funding_amount'],
                project_data['funding_unit'],
                project_data['approval_year'],
                project_data['project_number'],
                project_data['start_date'],
                project_data['end_date'],
                '在研'  # 默认状态
            )
            cursor.execute(project_sql, project_params)
            project_id = cursor.lastrowid

            # 插入项目result信息
            if 'result' in project_data and project_data['result']:
                result_sql = """
                    INSERT INTO project_result (
                        project_id, type, name, date
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                """
                for result in project_data['result']:
                    result_params = (
                        project_id,
                        result['type'],
                        result['name'],
                        result['date']
                    )
                    cursor.execute(result_sql, result_params)

            return True

        # 移除 commit=False 参数，让 with_db_connection 函数自动提交事务
        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def is_project_name_exists(self, project_name):
        """检查项目名称是否已存在"""

        def operation(cursor):
            sql = "SELECT COUNT(*) FROM projects WHERE project_name = %s"
            cursor.execute(sql, (project_name,))
            count = cursor.fetchone()[0]
            return count > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def get_all_projects(self):
        """获取所有项目信息"""

        def operation(cursor):
            sql = """
                SELECT
                    id, project_name, leader, department, phone, project_source, project_type,
                    start_date, end_date, funding_unit, level, funding_amount, approval_year,
                    project_number, status
                FROM projects
                ORDER BY start_date DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []

    def get_project_by_id(self, project_id):
        """根据ID获取项目信息"""

        def operation(cursor):
            # 获取项目基本信息
            project_sql = "SELECT * FROM projects WHERE id = %s"
            cursor.execute(project_sql, (project_id,))
            project = cursor.fetchone()

            if not project:
                return None

            # 获取项目result信息
            result_sql = "SELECT * FROM project_result WHERE project_id = %s"
            cursor.execute(result_sql, (project_id,))
            result = cursor.fetchall()
            project['result'] = result

            return project

        result = with_db_connection(operation)
        return result if result is not None else None

    def update_project(self, project_data):
        """更新项目信息"""
        # 验证项目数据
        if not validate_project_data(project_data) or 'id' not in project_data:
            return False

        def operation(cursor):
            # 开始事务
            conn = cursor.connection
            conn.begin()

            # 更新项目基本信息
            project_sql = """
                UPDATE projects SET
                    project_name = %s, leader = %s, department = %s, phone = %s,
                    project_source = %s, project_type = %s, level = %s, funding_amount = %s,
                    funding_unit = %s, approval_year = %s, project_number = %s,
                    start_date = %s, end_date = %s, status = %s
                WHERE id = %s
            """
            project_params = (
                project_data['project_name'],
                project_data['leader'],
                project_data['department'],
                project_data['phone'],
                project_data['project_source'],
                project_data['project_type'],
                project_data['level'],
                project_data['funding_amount'],
                project_data['funding_unit'],
                project_data['approval_year'],
                project_data['project_number'],
                project_data['start_date'],
                project_data['end_date'],
                project_data['status'],
                project_data['id']
            )
            cursor.execute(project_sql, project_params)

            # 删除旧的项目result
            delete_result_sql = "DELETE FROM project_result WHERE project_id = %s"
            cursor.execute(delete_result_sql, (project_data['id'],))

            # 插入新的项目result
            if 'result' in project_data and project_data['result']:
                result_sql = """
                    INSERT INTO project_result (
                        project_id, type, name, date
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                """
                for result in project_data['result']:
                    result_params = (
                        project_data['id'],
                        result['type'],
                        result['name'],
                        result['date']
                    )
                    cursor.execute(result_sql, result_params)

            # 提交事务
            conn.commit()
            return True

        result = with_db_connection(operation, cursor_type=Cursor, commit=False)
        return result if result is not None else False

    def delete_project(self, project_id):
        """删除项目信息（同时删除相关成果和提醒）"""

        def operation(cursor):
            # 开始事务
            conn = cursor.connection
            conn.begin()

            # 删除项目result
            delete_result_sql = "DELETE FROM project_result WHERE project_id = %s"
            cursor.execute(delete_result_sql, (project_id,))

            # 删除项目提醒
            delete_reminder_sql = "DELETE FROM reminders WHERE project_id = %s"
            cursor.execute(delete_reminder_sql, (project_id,))

            # 删除项目
            delete_project_sql = "DELETE FROM projects WHERE id = %s"
            cursor.execute(delete_project_sql, (project_id,))

            # 提交事务
            conn.commit()
            return True

        result = with_db_connection(operation, cursor_type=Cursor, commit=False)
        return result if result is not None else False
