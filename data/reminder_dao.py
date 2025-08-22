#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒数据访问对象"""
from data.db_connection import with_db_connection
from pymysql.cursors import DictCursor, Cursor


class ReminderDAO:
    """提醒数据访问对象"""

    def __init__(self):
        pass

    def insert(self, reminder_data):
        """插入新提醒"""

        def operation(cursor):
            sql = """
                INSERT INTO reminders (
                    project_id, project_name, reminder_type, days_before,
                    reminder_way, content, due_date, create_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                reminder_data['project_id'],
                reminder_data['project_name'],
                reminder_data['reminder_type'],
                reminder_data['days_before'],
                reminder_data['reminder_way'],
                reminder_data.get('content', ''),
                reminder_data['due_date'],
                reminder_data['create_time']
            )
            cursor.execute(sql, params)
            return cursor.lastrowid

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else -1

    def get_by_id(self, reminder_id):
        """根据ID获取提醒"""

        def operation(cursor):
            sql = "SELECT * FROM reminders WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        return result if result is not None else None

    def get_all(self):
        """获取所有提醒"""

        def operation(cursor):
            sql = "SELECT * FROM reminders ORDER BY due_date ASC"
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []

    def get_unread(self):
        """获取未读提醒"""

        def operation(cursor):
            sql = "SELECT * FROM reminders WHERE status = '未读' ORDER BY due_date ASC"
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []

    def update(self, reminder_data):
        """更新提醒"""

        def operation(cursor):
            sql = """
                UPDATE reminders SET
                    project_id = %s, project_name = %s, reminder_type = %s,
                    days_before = %s, reminder_way = %s, content = %s,
                    due_date = %s, status = %s
                WHERE id = %s
            """
            params = (
                reminder_data['project_id'],
                reminder_data['project_name'],
                reminder_data['reminder_type'],
                reminder_data['days_before'],
                reminder_data['reminder_way'],
                reminder_data.get('content', ''),
                reminder_data['due_date'],
                reminder_data['status'],
                reminder_data['id']
            )
            cursor.execute(sql, params)
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def delete(self, reminder_id):
        """删除提醒"""

        def operation(cursor):
            sql = "DELETE FROM reminders WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def mark_as_read(self, reminder_id):
        """标记提醒为已读"""

        def operation(cursor):
            sql = "UPDATE reminders SET status = '已读' WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def get_due_reminders(self):
        """获取到期提醒"""

        def operation(cursor):
            sql = "SELECT * FROM reminders WHERE due_date <= CURDATE() AND status = '未读'"
            cursor.execute(sql)
            return cursor.fetchall()

        result = with_db_connection(operation)
        return result if result is not None else []
