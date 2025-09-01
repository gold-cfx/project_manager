#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 提醒数据访问对象
"""
from typing import List, Optional

from pymysql.cursors import Cursor, DictCursor

from data.db_connection import with_db_connection
from models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderStatus


class ReminderDAO:
    """提醒数据访问对象"""

    def __init__(self):
        self.table_name = "reminders"
        self.model = Reminder

    @with_db_connection(cursor_type=Cursor)
    def insert(self, reminder_data: ReminderCreate, cursor: Cursor) -> int:
        """插入新提醒"""
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
        return cursor.lastrowid if cursor.lastrowid is not None else -1

    @with_db_connection()
    def get_by_id(self, reminder_id: int, cursor: DictCursor) -> Optional[Reminder]:
        """根据ID获取提醒"""
        sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (reminder_id,))
        result = cursor.fetchone()
        if result is not None:
            return Reminder(**result)
        return None

    @with_db_connection()
    def get_all(self, cursor: DictCursor) -> List[Reminder]:
        """获取所有提醒"""
        sql = f"SELECT * FROM {self.table_name} ORDER BY start_date ASC"
        cursor.execute(sql)
        results = cursor.fetchall()
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    @with_db_connection()
    def get_unread(self, cursor: DictCursor) -> List[Reminder]:
        """获取未读提醒"""
        sql = f"SELECT * FROM {self.table_name} WHERE status = %s ORDER BY start_date ASC"
        cursor.execute(sql, (ReminderStatus.UNREAD.value,))
        results = cursor.fetchall()
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    @with_db_connection(cursor_type=Cursor)
    def update(self, reminder_id: int, reminder_data: ReminderUpdate, cursor: Cursor) -> bool:
        """更新提醒"""
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

    @with_db_connection(cursor_type=Cursor)
    def delete(self, reminder_id: int, cursor: Cursor) -> bool:
        """删除提醒"""
        sql = f"DELETE FROM {self.table_name} WHERE id = %s"
        cursor.execute(sql, (reminder_id,))
        return cursor.rowcount > 0

    @with_db_connection()
    def get_by_project_id(self, project_id: int, cursor: DictCursor) -> List[Reminder]:
        """根据项目ID获取提醒"""
        sql = f"SELECT * FROM {self.table_name} WHERE project_id = %s ORDER BY start_date ASC"
        cursor.execute(sql, (project_id,))
        results = cursor.fetchall()
        if results is not None:
            return [Reminder(**item) for item in results]
        return []

    @with_db_connection()
    def get_upcoming_reminders(self, cursor: DictCursor, days: int = 7) -> List[Reminder]:
        """获取即将开始日期的提醒"""
        sql = f"""
            SELECT * FROM {self.table_name} 
            WHERE start_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY start_date ASC
        """
        cursor.execute(sql, (days,))
        results = cursor.fetchall()
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
