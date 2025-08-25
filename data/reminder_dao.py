#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒数据访问对象
"""
from typing import List, Optional, Dict, Any, Union
from datetime import date

from data.db_connection import with_db_connection
from models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderStatus
from pymysql.cursors import DictCursor, Cursor


class ReminderDAO:
    """提醒数据访问对象"""

    def __init__(self):
        self.table_name = "reminders"
        self.model = Reminder

    def insert(self, reminder_data: ReminderCreate) -> int:
        """插入新提醒"""

        def operation(cursor):
            # 使用模型的字段名和占位符
            fields = ReminderCreate.get_field_names()
            placeholders = ReminderCreate.get_sql_placeholders()
            
            sql = f"""
                INSERT INTO {self.table_name} (
                    {', '.join(fields)}
                ) VALUES (
                    {placeholders}
                )
            """
            
            # 从模型获取参数值
            params = tuple(getattr(reminder_data, field) for field in fields)
            cursor.execute(sql, params)
            return cursor.lastrowid

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else -1

    def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        """根据ID获取提醒"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.fetchone()

        result = with_db_connection(operation)
        if result is not None:
            return Reminder(**result)
        return None

    def get_all(self) -> List[Reminder]:
        """获取所有提醒"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} ORDER BY start_date ASC"
            cursor.execute(sql)
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    def get_unread(self) -> List[Reminder]:
        """获取未读提醒"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE status = %s ORDER BY start_date ASC"
            cursor.execute(sql, (ReminderStatus.UNREAD.value,))
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    def update(self, reminder_id: int, reminder_data: ReminderUpdate) -> bool:
        """更新提醒"""

        def operation(cursor):
            # 只更新非空字段
            update_data = reminder_data.dict(exclude_unset=True, exclude_none=True)
            if not update_data:
                return False
                
            set_clause = ", ".join([f"{field} = %s" for field in update_data.keys()])
            values = list(update_data.values())
            values.append(reminder_id)  # 添加WHERE条件的参数
            
            sql = f"""
                UPDATE {self.table_name} SET
                    {set_clause}
                WHERE id = %s
            """
            
            cursor.execute(sql, tuple(values))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def delete(self, reminder_id: int) -> bool:
        """删除提醒"""

        def operation(cursor):
            sql = f"DELETE FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (reminder_id,))
            return cursor.rowcount > 0

        result = with_db_connection(operation, cursor_type=Cursor)
        return result if result is not None else False

    def get_by_project_id(self, project_id: int) -> List[Reminder]:
        """根据项目ID获取提醒"""

        def operation(cursor):
            sql = f"SELECT * FROM {self.table_name} WHERE project_id = %s ORDER BY start_date ASC"
            cursor.execute(sql, (project_id,))
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    def get_upcoming_reminders(self, days: int = 7) -> List[Reminder]:
        """获取即将开始日期的提醒"""

        def operation(cursor):
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE start_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                ORDER BY start_date ASC
            """
            cursor.execute(sql, (days,))
            return cursor.fetchall()

        results = with_db_connection(operation)
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    def mark_as_read(self, reminder_id: int) -> bool:
        """标记提醒为已读"""
        update_data = ReminderUpdate(status=ReminderStatus.READ)
        return self.update(reminder_id, update_data)

    def mark_as_processed(self, reminder_id: int) -> bool:
        """标记提醒为已处理"""
        update_data = ReminderUpdate(status=ReminderStatus.PROCESSED)
        return self.update(reminder_id, update_data)
