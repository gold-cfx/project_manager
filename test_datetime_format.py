#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日期时间和Decimal格式化装饰器
"""
from data.db_connection import with_db_connection
from datetime import datetime, date
from decimal import Decimal
import pymysql
from typing import Dict, Any, List

from models.base import BaseDataModel
from pydantic import Field


class TestDataModel(BaseDataModel):
    """测试数据模型"""
    date_field: date = Field(..., description="日期字段")
    datetime_field: datetime = Field(..., description="日期时间字段")
    decimal_field: Decimal = Field(..., description="Decimal字段")
    list_field: List[Any] = Field(..., description="列表字段")
    dict_field: Dict[str, Any] = Field(..., description="字典字段")


def test_datetime_formatting():
    """测试日期时间和Decimal格式化"""
    print("开始测试日期时间和Decimal格式化...")

    # 测试1: 使用Pydantic模型
    def test_pydantic_model():
        # 创建测试数据模型
        test_model = TestDataModel(
            date_field=date(2023, 12, 31),
            datetime_field=datetime(2023, 12, 31, 23, 59, 59),
            decimal_field=Decimal('450000.00'),
            list_field=[date(2023, 1, 1), datetime(2023, 1, 1, 12, 0, 0), Decimal('123456.78')],
            dict_field={
                'sub_date': date(2023, 2, 1), 
                'sub_datetime': datetime(2023, 2, 1, 12, 0, 0),
                'sub_decimal': Decimal('98765.43')
            }
        )
        
        # 获取原始字典
        raw_dict = test_model.dict()
        print("原始字典:")
        print(f"date_field: {raw_dict['date_field']} (类型: {type(raw_dict['date_field'])})") 
        print(f"datetime_field: {raw_dict['datetime_field']} (类型: {type(raw_dict['datetime_field'])})") 
        print(f"decimal_field: {raw_dict['decimal_field']} (类型: {type(raw_dict['decimal_field'])})") 
        
        # 获取格式化字典
        formatted_dict = test_model.to_formatted_dict()
        print("\n格式化字典:")
        print(f"date_field: {formatted_dict['date_field']} (类型: {type(formatted_dict['date_field'])})") 
        print(f"datetime_field: {formatted_dict['datetime_field']} (类型: {type(formatted_dict['datetime_field'])})") 
        print(f"decimal_field: {formatted_dict['decimal_field']} (类型: {type(formatted_dict['decimal_field'])})") 
        print(f"list_field[0]: {formatted_dict['list_field'][0]} (类型: {type(formatted_dict['list_field'][0])})") 
        print(f"dict_field['sub_date']: {formatted_dict['dict_field']['sub_date']} (类型: {type(formatted_dict['dict_field']['sub_date'])})") 
        
        return formatted_dict
    
    result1 = test_pydantic_model()
    print("\n测试1 - Pydantic模型格式化完成!")
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