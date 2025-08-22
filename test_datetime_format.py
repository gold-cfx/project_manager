#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日期时间和Decimal格式化装饰器
"""
from data.db_connection import with_db_connection
from datetime import datetime, date
from decimal import Decimal
import pymysql


def test_datetime_formatting():
    """测试日期时间和Decimal格式化"""
    print("开始测试日期时间和Decimal格式化...")

    # 测试1: 直接返回日期时间和Decimal对象
    def test_direct_objects():
        def operation(cursor):
            return {
                'date': date(2023, 12, 31),
                'datetime': datetime(2023, 12, 31, 23, 59, 59),
                'decimal': Decimal('450000.00'),
                'list': [date(2023, 1, 1), datetime(2023, 1, 1, 12, 0, 0), Decimal('123456.78')],
                'dict': {
                    'sub_date': date(2023, 2, 1), 
                    'sub_datetime': datetime(2023, 2, 1, 12, 0, 0),
                    'sub_decimal': Decimal('98765.43')
                }
            }
        return with_db_connection(operation)

    result1 = test_direct_objects()
    print("测试1 - 直接返回对象:")
    print(f"格式化后的date: {result1['date']} (类型: {type(result1['date'])})")
    print(f"格式化后的datetime: {result1['datetime']} (类型: {type(result1['datetime'])})")
    print(f"格式化后的decimal: {result1['decimal']} (类型: {type(result1['decimal'])})")
    print(f"列表中的date: {result1['list'][0]} (类型: {type(result1['list'][0])})")
    print(f"列表中的datetime: {result1['list'][1]} (类型: {type(result1['list'][1])})")
    print(f"列表中的decimal: {result1['list'][2]} (类型: {type(result1['list'][2])})")
    print(f"字典中的date: {result1['dict']['sub_date']} (类型: {type(result1['dict']['sub_date'])})")
    print(f"字典中的datetime: {result1['dict']['sub_datetime']} (类型: {type(result1['dict']['sub_datetime'])})")
    print(f"字典中的decimal: {result1['dict']['sub_decimal']} (类型: {type(result1['dict']['sub_decimal'])})")
    print()

    # 测试2: 从数据库查询返回日期时间和Decimal
    def test_db_objects():
        def operation(cursor):
            # 创建临时表
            cursor.execute("CREATE TABLE IF NOT EXISTS test_data_types (id INT, date_col DATE, datetime_col DATETIME, decimal_col DECIMAL(10,2))")
            cursor.execute("INSERT INTO test_data_types VALUES (1, '2023-12-31', '2023-12-31 23:59:59', 450000.00)")
            cursor.execute("SELECT * FROM test_data_types WHERE id = 1")
            result = cursor.fetchone()
            # 清理临时表
            cursor.execute("DROP TABLE IF EXISTS test_data_types")
            return result
        return with_db_connection(operation)

    result2 = test_db_objects()
    print("测试2 - 从数据库查询返回:")
    print(f"数据库返回的date: {result2['date_col']} (类型: {type(result2['date_col'])})")
    print(f"数据库返回的datetime: {result2['datetime_col']} (类型: {type(result2['datetime_col'])})")
    print(f"数据库返回的decimal: {result2['decimal_col']} (类型: {type(result2['decimal_col'])})")

    print("\n格式化测试完成!")


if __name__ == '__main__':
    test_datetime_formatting()