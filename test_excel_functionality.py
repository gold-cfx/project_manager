#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Excel导入导出功能
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_handler import ExcelTemplateGenerator, ExcelImporter, ExcelExporter
from datetime import datetime

def test_template_generation():
    """测试模板生成功能"""
    print("测试Excel模板生成...")
    template_path = "项目录入模板.xlsx"
    
    success = ExcelTemplateGenerator.generate_project_template(template_path)
    if success:
        print(f"✓ 模板生成成功: {template_path}")
        return True
    else:
        print("✗ 模板生成失败")
        return False

def test_export_function():
    """测试导出功能"""
    print("\n测试Excel导出功能...")
    
    # 模拟项目数据
    test_projects = [
        {
            'id': 1,
            'project_name': '测试项目1',
            'leader': '张三',
            'department': '科研科',
            'phone': '13800138000',
            'source': '国家自然科学基金',
            'type': '纵向课题',
            'level': '国家级',
            'funding_amount': 100.50,
            'funding_unit': '国家自然科学基金委员会',
            'approval_year': '2024',
            'project_code': 'NSFC2024001',
            'status': '进行中',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'notes': '这是一个测试项目'
        },
        {
            'id': 2,
            'project_name': '测试项目2',
            'leader': '李四',
            'department': '技术开发部',
            'phone': '13900139000',
            'source': '科技部项目',
            'type': '横向课题',
            'level': '省部级',
            'funding_amount': 50.75,
            'funding_unit': '科技部',
            'approval_year': '2024',
            'project_code': 'MOST2024002',
            'status': '已完成',
            'start_date': '2024-02-01',
            'end_date': '2024-11-30',
            'notes': '这是另一个测试项目'
        }
    ]
    
    export_path = "测试导出.xlsx"
    success = ExcelExporter.export_projects_to_excel(test_projects, export_path)
    if success:
        print(f"✓ 导出成功: {export_path}")
        return True
    else:
        print("✗ 导出失败")
        return False

def test_import_function():
    """测试导入功能"""
    print("\n测试Excel导入功能...")
    
    # 首先确保模板存在
    template_path = "项目录入模板.xlsx"
    if not os.path.exists(template_path):
        print("模板文件不存在，先生成模板...")
        ExcelTemplateGenerator.generate_project_template(template_path)
    
    try:
        projects = ExcelImporter.import_projects_from_excel(template_path)
        print(f"✓ 模板读取成功，共{len(projects)}条记录")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Excel功能测试开始")
    print("=" * 50)
    
    results = []
    
    # 测试模板生成
    results.append(test_template_generation())
    
    # 测试导出功能
    results.append(test_export_function())
    
    # 测试导入功能
    results.append(test_import_function())
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"模板生成: {'✓' if results[0] else '✗'}")
    print(f"数据导出: {'✓' if results[1] else '✗'}")
    print(f"数据导入: {'✓' if results[2] else '✗'}")
    
    if all(results):
        print("\n🎉 所有测试通过！Excel功能正常工作")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()