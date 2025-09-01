#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 查询业务逻辑
"""
from pymysql.cursors import Cursor, DictCursor

from data.db_connection import with_db_connection


class QueryLogic:
    def __init__(self):
        pass

    @with_db_connection()
    def query_projects(self, conditions, cursor: DictCursor):
        """根据条件查询项目"""
        # 构建SQL查询语句
        sql = """
            SELECT
                id, project_name, leader, department, phone, project_source, project_type,
                start_date, end_date, funding_unit, level, funding_amount, approval_year,
                project_number, status
            FROM projects
            WHERE 1=1
        """
        params = []

        # 添加查询条件
        if conditions.get('project_name'):
            sql += " AND project_name LIKE %s"
            params.append(f"%{conditions['project_name']}%")

        if conditions.get('leader'):
            sql += " AND leader LIKE %s"
            params.append(f"%{conditions['leader']}%")

        # 处理科室条件
        if conditions.get('department'):
            sql += " AND department = %s"
            params.append(conditions['department'])

        # 处理项目来源条件
        if conditions.get('project_source'):
            sql += " AND project_source = %s"
            params.append(conditions['project_source'])

        # 处理项目类型条件
        if conditions.get('project_type'):
            sql += " AND project_type = %s"
            params.append(conditions['project_type'])

        # 处理开始日期条件
        if conditions.get('start_date_ge'):
            sql += " AND start_date >= %s"
            params.append(conditions['start_date_ge'])
        if conditions.get('start_date_le'):
            sql += " AND start_date <= %s"
            params.append(conditions['start_date_le'])

        # 处理结束日期条件
        if conditions.get('end_date_ge'):
            sql += " AND end_date >= %s"
            params.append(conditions['end_date_ge'])
        if conditions.get('end_date_le'):
            sql += " AND end_date <= %s"
            params.append(conditions['end_date_le'])

        if conditions.get('funding_unit'):
            sql += " AND funding_unit = %s"
            params.append(conditions['funding_unit'])

        if conditions.get('level'):
            sql += " AND level = %s"
            params.append(conditions['level'])

        if conditions.get('status'):
            sql += " AND status = %s"
            params.append(conditions['status'])

        # 处理立项年度条件
        if conditions.get('approval_year_ge'):
            sql += " AND approval_year >= %s"
            params.append(conditions['approval_year_ge'])
        if conditions.get('approval_year_le'):
            sql += " AND approval_year <= %s"
            params.append(conditions['approval_year_le'])

        # 添加排序
        sql += " ORDER BY start_date DESC"

        cursor.execute(sql, params)
        result = cursor.fetchall()
        return result if result is not None else []

    @with_db_connection(cursor_type=Cursor)
    def get_all_funding_units(self, cursor: Cursor):
        """获取所有资助单位"""

        sql = "SELECT DISTINCT funding_unit FROM projects ORDER BY funding_unit"
        cursor.execute(sql)
        result = [item[0] for item in cursor.fetchall()]
        return result if result is not None else []

    @with_db_connection(cursor_type=Cursor)
    def get_all_departments(self, cursor: Cursor):
        """获取所有科室"""

        sql = "SELECT DISTINCT department FROM projects ORDER BY department"
        cursor.execute(sql)
        result = [item[0] for item in cursor.fetchall()]

        return result if result is not None else []

    @with_db_connection(cursor_type=Cursor)
    def get_all_project_sources(self, cursor: Cursor):
        """获取所有项目来源"""

        sql = "SELECT DISTINCT project_source FROM projects ORDER BY project_source"
        cursor.execute(sql)
        result = [item[0] for item in cursor.fetchall()]
        return result if result is not None else []

    @with_db_connection(cursor_type=Cursor)
    def get_all_project_types(self, cursor: Cursor):
        """获取所有项目类型"""
        sql = "SELECT DISTINCT project_type FROM projects ORDER BY project_type"
        cursor.execute(sql)
        result = [item[0] for item in cursor.fetchall()]
        return result if result is not None else []

    @with_db_connection(cursor_type=Cursor)
    def get_chart_data(self, conditions, chart_type, chart_format, cursor: Cursor):
        """获取图表数据"""
        # 根据图表类型构建SQL查询
        if chart_type == '按级别统计项目数量':
            sql = """
                SELECT level, COUNT(*) as count
                FROM projects
                WHERE 1=1
            """
            group_by = " GROUP BY level ORDER BY level"

        elif chart_type == '按资助单位统计项目数量':
            sql = """
                SELECT funding_unit, COUNT(*) as count
                FROM projects
                WHERE 1=1
            """
            group_by = " GROUP BY funding_unit ORDER BY funding_unit"

        elif chart_type == '按年份统计项目数量':
            sql = """
                SELECT YEAR(start_date) as year, COUNT(*) as count
                FROM projects
                WHERE 1=1
            """
            group_by = " GROUP BY YEAR(start_date) ORDER BY YEAR(start_date)"

        elif chart_type == '按级别统计资助金额':
            sql = """
                SELECT level, SUM(funding_amount) as amount
                FROM projects
                WHERE 1=1
            """
            group_by = " GROUP BY level ORDER BY level"

        else:
            return {}

        # 添加查询条件
        params = []

        if conditions.get('project_name'):
            sql += " AND project_name LIKE %s"
            params.append(f"%{conditions['project_name']}%")

        if conditions.get('leader'):
            sql += " AND leader LIKE %s"
            params.append(f"%{conditions['leader']}%")

        # 处理开始日期条件
        if conditions.get('start_date_ge'):
            sql += " AND start_date >= %s"
            params.append(conditions['start_date_ge'])
        if conditions.get('start_date_le'):
            sql += " AND start_date <= %s"
            params.append(conditions['start_date_le'])

        # 处理结束日期条件
        if conditions.get('end_date_ge'):
            sql += " AND end_date >= %s"
            params.append(conditions['end_date_ge'])
        if conditions.get('end_date_le'):
            sql += " AND end_date <= %s"
            params.append(conditions['end_date_le'])

        if conditions.get('funding_unit'):
            sql += " AND funding_unit = %s"
            params.append(conditions['funding_unit'])

        if conditions.get('level'):
            sql += " AND level = %s"
            params.append(conditions['level'])

        if conditions.get('status'):
            sql += " AND status = %s"
            params.append(conditions['status'])

        # 添加分组和排序
        sql += group_by

        cursor.execute(sql, params)
        results = cursor.fetchall()

        # 格式化结果
        chart_data = {}
        for result in results:
            if chart_type in ['按级别统计项目数量', '按资助单位统计项目数量', '按年份统计项目数量']:
                key = result['level'] if 'level' in result else (
                    result['funding_unit'] if 'funding_unit' in result else str(result['year']))
                chart_data[key] = result['count']
            elif chart_type == '按级别统计资助金额':
                chart_data[result['level']] = result['amount']

        return chart_data if chart_data is not None else {}
