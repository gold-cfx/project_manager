#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据验证工具
"""
import re
from datetime import datetime


class Validator:
    """数据验证工具类"""

    @staticmethod
    def is_valid_project_name(project_name):
        """验证项目名称"""
        if not project_name or len(project_name) > 255:
            return False, "项目名称不能为空且不能超过255个字符"
        return True, "验证通过"

    @staticmethod
    def is_valid_leader(leader):
        """验证负责人姓名"""
        if not leader or len(leader) > 50:
            return False, "负责人姓名不能为空且不能超过50个字符"
        return True, "验证通过"

    @staticmethod
    def is_valid_phone(phone):
        """验证联系电话"""
        pattern = r'^1[3-9]\d{9}$|^\d{3,4}-\d{7,8}$'
        if not re.match(pattern, phone):
            return False, "联系电话格式不正确，请使用手机号或固话格式"
        return True, "验证通过"

    @staticmethod
    def is_valid_email(email):
        """验证邮箱地址"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, email):
            return False, "邮箱地址格式不正确"
        return True, "验证通过"

    @staticmethod
    def is_valid_date(date_str):
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, "验证通过"
        except ValueError:
            return False, "日期格式不正确，请使用YYYY-MM-DD格式"

    @staticmethod
    def is_valid_date_range(start_date, end_date):
        """验证日期范围"""
        try:
            if type(start_date) == str:
                start = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start = start_date
            if type(end_date) == str:
                end = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end = end_date
            if end < start:
                return False, "结束日期不能早于起始日期"
            # 检查项目持续时间是否超过10年
            duration = (end - start).days / 365
            if duration > 10:
                return False, "项目持续时间不能超过10年"
            return True, "验证通过"
        except ValueError:
            return False, "日期格式不正确，请使用YYYY-MM-DD格式"

    @staticmethod
    def is_valid_funding_amount(amount):
        """验证资助金额"""
        try:
            value = float(amount)
            if value < 0:
                return False, "资助金额不能为负数"
            return True, "验证通过"
        except ValueError:
            return False, "资助金额必须为数字"

    @staticmethod
    def is_valid_level(level):
        """验证项目级别"""
        # 验证项目级别
        valid_levels = ['国家级', '省部级', '市级', '厅局级']
        if level not in valid_levels:
            return False, f"项目级别必须是以下之一: {', '.join(valid_levels)}"
        return True, "验证通过"

    @staticmethod
    def is_valid_reminder_type(reminder_type):
        """验证提醒类型"""
        valid_types = ['开始日期提醒', '里程碑提醒', '其他提醒']
        if reminder_type not in valid_types:
            return False, f"提醒类型必须是以下之一: {', '.join(valid_types)}"
        return True, "验证通过"

    @staticmethod
    def is_valid_days_before(days_before):
        """验证提前天数"""
        try:
            value = int(days_before)
            if value < 0:
                return False, "提前天数不能为负数"
            return True, "验证通过"
        except ValueError:
            return False, "提前天数必须为整数"

    @staticmethod
    def is_valid_reminder_way(reminder_way):
        """验证提醒方式"""
        valid_ways = ['系统内通知', '邮件通知', '短信通知']
        if reminder_way not in valid_ways:
            return False, f"提醒方式必须是以下之一: {', '.join(valid_ways)}"
        return True, "验证通过"

    @staticmethod
    def is_valid_funding_unit(funding_unit):
        """验证资助单位"""
        if funding_unit and len(funding_unit) <= 100:
            return True, "验证通过"
        else:
            return False, '资助单位不能为空且不能超过100个字符'

    @staticmethod
    def is_valid_department(department):
        """验证科室"""
        if department and len(department) <= 50:
            return True, "验证通过"
        else:
            return False, '科室不能为空且不能超过50个字符'

    @staticmethod
    def is_valid_approval_year(approval_year):
        """验证立项年度"""
        if not approval_year or not approval_year.isdigit() or len(approval_year) != 4:
            return False, '请输入有效的立项年度(格式:YYYY)'
        year = int(approval_year)
        if year < 1900 or year > datetime.now().year + 1:
            return False, f'立项年度必须在1900到{datetime.now().year + 1}之间'
        return True, "验证通过"

    @staticmethod
    def is_valid_project_number(project_number):
        """验证项目编号"""
        if project_number and len(project_number) <= 50:
            return True, "验证通过"
        else:
            return False, '项目编号不能为空且不能超过50个字符'


# 验证项目数据
def validate_project_data(project_data):
    """验证项目数据"""
    errors = []

    # 验证项目名称
    valid, msg = Validator.is_valid_project_name(project_data.get('project_name'))
    if not valid: errors.append(msg)

    # 验证负责人
    valid, msg = Validator.is_valid_leader(project_data.get('leader'))
    if not valid: errors.append(msg)

    # 验证科室
    valid, msg = Validator.is_valid_department(project_data.get('department'))
    if not valid: errors.append(msg)

    # 验证联系电话
    valid, msg = Validator.is_valid_phone(project_data.get('phone'))
    if not valid: errors.append(msg)

    # 验证项目来源
    project_source = project_data.get('project_source')
    if not project_source or project_source.strip() == '' or project_source == '请选择项目来源':
        errors.append("项目来源不能为空")

    # 验证项目类型
    project_type = project_data.get('project_type')
    valid_types = ['纵向课题', '横向课题', '研究者发起的临床研究项目', 'GCP项目']
    if not project_type or project_type.strip() == '':
        errors.append("项目类型不能为空")
    elif project_type not in valid_types:
        errors.append(f"项目类型必须是以下之一: {', '.join(valid_types)}")

    # 验证项目级别
    valid, msg = Validator.is_valid_level(project_data.get('level'))
    if not valid: errors.append(msg)

    # 验证资助金额
    valid, msg = Validator.is_valid_funding_amount(project_data.get('funding_amount'))
    if not valid: errors.append(msg)

    # 验证资助单位
    valid, msg = Validator.is_valid_funding_unit(project_data.get('funding_unit'))
    if not valid: errors.append(msg)

    # 验证立项年度
    valid, msg = Validator.is_valid_approval_year(project_data.get('approval_year'))
    if not valid: errors.append(msg)

    # 验证项目编号
    valid, msg = Validator.is_valid_project_number(project_data.get('project_number'))
    if not valid: errors.append(msg)

    # 验证起始日期
    valid, msg = Validator.is_valid_date(project_data.get('start_date'))
    if not valid: errors.append(msg)

    # 验证结束日期
    valid, msg = Validator.is_valid_date(project_data.get('end_date'))
    if not valid:
        errors.append(msg)
    else:
        # 验证日期范围
        valid, msg = Validator.is_valid_date_range(project_data.get('start_date'), project_data.get('end_date'))
        if not valid: errors.append(msg)

    # 验证立项年度
    valid, msg = Validator.is_valid_approval_year(project_data.get('approval_year'))
    if not valid: errors.append(msg)

    # 验证项目编号
    valid, msg = Validator.is_valid_project_number(project_data.get('project_number'))
    if not valid: errors.append(msg)

    # 验证日期范围
    start_date = project_data.get('start_date')
    end_date = project_data.get('end_date')
    if start_date and end_date:
        valid, msg = Validator.is_valid_date_range(start_date, end_date)
        if not valid: errors.append(msg)
    else:
        if not start_date: errors.append("项目开始时间不能为空")
        if not end_date: errors.append("项目结束时间不能为空")

    # 验证项目状态
    status = project_data.get('status')
    valid_statuses = ['在研', '延期', '结题']
    if not status or status.strip() == '':
        errors.append("项目状态不能为空")
    elif status not in valid_statuses:
        errors.append(f"项目状态必须是以下之一: {', '.join(valid_statuses)}")

    return len(errors) == 0, errors


# 验证提醒数据
def validate_reminder_data(reminder_data):
    """验证提醒数据"""
    errors = []

    # 验证项目ID
    if not reminder_data.get('project_id'):
        errors.append("项目ID不能为空")

    # 验证项目名称
    if not reminder_data.get('project_name'):
        errors.append("项目名称不能为空")

    # 验证提醒类型
    valid, msg = Validator.is_valid_reminder_type(reminder_data.get('reminder_type'))
    if not valid: errors.append(msg)

    # 验证提前天数
    valid, msg = Validator.is_valid_days_before(reminder_data.get('days_before'))
    if not valid: errors.append(msg)

    # 验证提醒方式
    valid, msg = Validator.is_valid_reminder_way(reminder_data.get('reminder_way'))
    if not valid: errors.append(msg)

    # 验证开始日期
    valid, msg = Validator.is_valid_date(reminder_data.get('start_date'))
    if not valid: errors.append(msg)

    # 验证创建时间
    valid, msg = Validator.is_valid_date(reminder_data.get('create_time'))
    if not valid: errors.append(msg)

    return len(errors) == 0, errors
