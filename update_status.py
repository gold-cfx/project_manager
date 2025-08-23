#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新项目状态值，使其与 ProjectStatus 枚举一致
"""

import pymysql
from config.settings import DB_CONFIG


def update_project_status():
    """更新项目状态值"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        # 更新状态值
        # 将 '在研' 更新为 '进行中'
        cursor.execute("UPDATE projects SET status = '进行中' WHERE status = '在研'")
        rows_updated1 = cursor.rowcount
        
        # 将 '延期' 更新为 '已暂停'
        cursor.execute("UPDATE projects SET status = '已暂停' WHERE status = '延期'")
        rows_updated2 = cursor.rowcount
        
        # 将 '结题' 更新为 '已完成'
        cursor.execute("UPDATE projects SET status = '已完成' WHERE status = '结题'")
        rows_updated3 = cursor.rowcount
        
        # 提交事务
        conn.commit()
        
        print(f"更新完成：'在研' -> '进行中'：{rows_updated1}行")
        print(f"更新完成：'延期' -> '已暂停'：{rows_updated2}行")
        print(f"更新完成：'结题' -> '已完成'：{rows_updated3}行")
        
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"更新失败：{e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    update_project_status()