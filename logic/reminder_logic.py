#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒业务逻辑"""
from datetime import datetime, timedelta

from data.db_connection import with_db_connection


class ReminderLogic:
    def __init__(self):
        pass

    def add_reminder(self, reminder_data):
        """添加提醒"""

        def operation(cursor):
            # 获取项目结束日期
            project_id = reminder_data['project_id']
            project_sql = "SELECT end_date FROM projects WHERE id = %s"
            cursor.execute(project_sql, (project_id,))
            project = cursor.fetchone()
            if not project:
                return False

            end_date = project['end_date']
            days_before = reminder_data['days_before']

            # 计算提醒日期
            if str(end_date) == str:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date_obj = end_date
            reminder_date = end_date_obj - timedelta(days=days_before)

            # 插入提醒信息
            reminder_sql = """
                INSERT INTO reminders (
                    project_id, project_name, reminder_type, days_before,
                    reminder_way, content, due_date, status, create_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            reminder_params = (
                project_id,
                reminder_data['project_name'],
                reminder_data['reminder_type'],
                days_before,
                reminder_data['reminder_way'],
                reminder_data['content'],
                reminder_date.strftime('%Y-%m-%d'),
                '未读'
            )
            cursor.execute(reminder_sql, reminder_params)

            return True

        result = with_db_connection(operation)
        return result if result is not None else False

    def get_all_reminders(self):
        """获取所有提醒"""

        def operation(cursor):
            sql = """
                SELECT
                    id, project_id, project_name, reminder_type, days_before,
                    reminder_way, content, due_date, status, create_time
                FROM reminders
                ORDER BY due_date ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []

    def get_reminder_by_id(self, reminder_id):
        """根据ID获取提醒"""

        def operation(cursor):
            sql = "SELECT * FROM reminders WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        return result if result is not None else None

    def update_reminder(self, reminder_data):
        """更新提醒"""

        def operation(cursor):
            # 获取项目结束日期
            project_id = reminder_data['project_id']
            project_sql = "SELECT end_date FROM projects WHERE id = %s"
            cursor.execute(project_sql, (project_id,))
            project = cursor.fetchone()
            if not project:
                return False

            end_date = project['end_date']
            days_before = reminder_data['days_before']

            # 计算提醒日期
            if str(end_date) == str:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date_obj = end_date
            reminder_date = end_date_obj - timedelta(days=days_before)
            # 更新提醒信息
            reminder_sql = """
                UPDATE reminders SET
                    project_name = %s, reminder_type = %s, days_before = %s,
                    reminder_way = %s, content = %s, due_date = %s, status = %s
                WHERE id = %s
            """
            reminder_params = (
                reminder_data['project_name'],
                reminder_data['reminder_type'],
                days_before,
                reminder_data['reminder_way'],
                reminder_data['content'],
                reminder_date.strftime('%Y-%m-%d'),
                "未读",
                reminder_data['id']
            )
            cursor.execute(reminder_sql, reminder_params)

            return True

        result = with_db_connection(operation)
        return result if result is not None else False

    def delete_reminder(self, reminder_id):
        """删除提醒"""

        def operation(cursor):
            sql = "DELETE FROM reminders WHERE id = %s"
            cursor.execute(sql, (reminder_id,))

            return True

        result = with_db_connection(operation)
        return result if result is not None else False

    def mark_reminder_as_read(self, reminder_id):
        """标记提醒为已读"""

        def operation(cursor):
            sql = "UPDATE reminders SET status = '已读' WHERE id = %s"
            cursor.execute(sql, (reminder_id,))

            return True

        result = with_db_connection(operation)
        return result if result is not None else False

    def check_due_reminders(self):
        """检查到期提醒"""

        def operation(cursor):
            today = datetime.now().strftime('%Y-%m-%d')

            sql = """
                SELECT * FROM reminders
                WHERE due_date <= %s AND status = '未读'
            """
            cursor.execute(sql, (today,))
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []
