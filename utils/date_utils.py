#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 日期工具
"""
from datetime import datetime, timedelta


class DateUtils:
    """日期工具类"""

    @staticmethod
    def format_date(date_str, input_format='%Y-%m-%d', output_format='%Y-%m-%d'):
        """格式化日期字符串"""
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return date_str

    @staticmethod
    def calculate_duration(start_date, end_date):
        """计算日期持续时间（天）"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            duration = (end - start).days
            return duration
        except ValueError:
            return 0

    @staticmethod
    def calculate_duration_years(start_date, end_date):
        """计算日期持续时间（年）"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            # 计算年份差
            years = end.year - start.year
            # 考虑月份和日期
            if (end.month < start.month) or (end.month == start.month and end.day < start.day):
                years -= 1
            return years
        except ValueError:
            return 0

    @staticmethod
    def get_start_date(end_date, days_before):
        """计算开始日期提醒日期"""
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            start_date = end - timedelta(days=days_before)
            return start_date.strftime('%Y-%m-%d')
        except ValueError:
            return ''

    @staticmethod
    def get_current_date(format_str='%Y-%m-%d'):
        """获取当前日期"""
        return datetime.now().strftime(format_str)

    @staticmethod
    def is_date_in_range(date_str, start_date, end_date):
        """检查日期是否在范围内"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return start <= date <= end
        except ValueError:
            return False


# 格式化日期
def format_date(date_str, input_format='%Y-%m-%d', output_format='%Y-%m-%d'):
    return DateUtils.format_date(date_str, input_format, output_format)


# 计算持续时间（天）
def calculate_duration(start_date, end_date):
    return DateUtils.calculate_duration(start_date, end_date)


# 获取开始日期
def get_start_date(end_date, days_before):
    return DateUtils.get_start_date(end_date, days_before)
