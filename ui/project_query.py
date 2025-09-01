#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目查询界面
"""
import csv
import os

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QMessageBox, QSplitter, QFileDialog, QHeaderView, QDialog
)
from matplotlib import pyplot as plt

from logic.project_logic import ProjectLogic
from logic.query_logic import QueryLogic
from ui.chart_dialog import ChartDialog
from ui.data_editor import ProjectEditorDialog

# 动态导入其他对话框，避免循环依赖


# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


class ProjectQuery(QWidget):
    def __init__(self):
        super().__init__()
        self.query_logic = QueryLogic()
        self.project_logic = ProjectLogic()  # 用于项目删除操作
        self.selected_rows = set()  # 用于存储选中的项目ID
        self.init_ui()
        self.load_project_status()
        self.load_funding_units()
        self.load_project_levels()
        self.load_departments()
        self.load_project_sources()
        self.load_project_types()
        self.select_all = False

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel('项目查询')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建查询条件组
        query_group = QGroupBox('查询条件')

        # 创建第一个FormLayout
        query_layout1 = QFormLayout()
        # 创建第二个FormLayout
        query_layout2 = QFormLayout()
        # 设置两个formlayout的宽度一致
        # query_layout1.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        # query_layout2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        # query_layout1.setHorizontalSpacing(10)
        # query_layout2.setHorizontalSpacing(10)
        # query_layout1.setSizeConstraint(QLayout.SetMinAndMaxSize)
        # query_layout2.setSizeConstraint(QLayout.SetMinAndMaxSize)

        # 项目名称
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText('请输入项目名称关键词')
        query_layout1.addRow('项目名称', self.project_name_edit)

        # 负责人
        self.leader_edit = QLineEdit()
        self.leader_edit.setPlaceholderText('请输入负责人关键词')
        query_layout2.addRow('项目负责人', self.leader_edit)

        # 课题资助单位
        self.funding_unit_combo = QComboBox()
        self.funding_unit_combo.addItem('全部')
        query_layout1.addRow('课题资助单位', self.funding_unit_combo)

        # 课题级别
        self.level_combo = QComboBox()
        self.level_combo.addItem('全部')
        query_layout2.addRow('课题级别', self.level_combo)

        # 科室
        self.department_combo = QComboBox()
        self.department_combo.addItem('全部')
        query_layout1.addRow('科室', self.department_combo)

        # 项目来源
        self.project_source_combo = QComboBox()
        self.project_source_combo.addItem('全部')
        query_layout2.addRow('项目来源', self.project_source_combo)

        # 开始时间范围 (项目在该时间范围内开始)
        start_range_layout = QHBoxLayout()

        self.start_date_from = QDateEdit()
        self.start_date_from.setCalendarPopup(True)
        self.start_date_from.setDisplayFormat('yyyy-MM-dd')
        self.start_date_from.setDate(QDate.currentDate().addYears(-10))

        self.start_date_to = QDateEdit()
        self.start_date_to.setCalendarPopup(True)
        self.start_date_to.setDisplayFormat('yyyy-MM-dd')
        self.start_date_to.setDate(QDate.currentDate().addYears(10))

        # 开始时间快速选择
        self.start_quick_combo = QComboBox()
        self.start_quick_combo.addItems(
            ['自定义', '近7天', '近30天', '近90天', '近6个月', '近1年', '未来7天', '未来30天', '未来90天', '未来6个月'])
        self.start_quick_combo.currentIndexChanged.connect(lambda index: self.on_date_quick_changed(index, 'start'))

        start_range_layout.addWidget(self.start_date_from)
        start_range_layout.addWidget(QLabel('~'))
        start_range_layout.addWidget(self.start_date_to)
        start_range_layout.addWidget(self.start_quick_combo)

        query_layout1.addRow('开始时间范围', start_range_layout)

        # 结束时间范围 (项目在该时间范围内结束)
        end_range_layout = QHBoxLayout()

        self.end_date_from = QDateEdit()
        self.end_date_from.setCalendarPopup(True)
        self.end_date_from.setDisplayFormat('yyyy-MM-dd')
        self.end_date_from.setDate(QDate.currentDate().addYears(-10))

        self.end_date_to = QDateEdit()
        self.end_date_to.setCalendarPopup(True)
        self.end_date_to.setDisplayFormat('yyyy-MM-dd')
        self.end_date_to.setDate(QDate.currentDate().addYears(10))

        # 结束时间快速选择
        self.end_quick_combo = QComboBox()
        self.end_quick_combo.addItems(
            ['自定义', '近7天', '近30天', '近90天', '近6个月', '近1年', '未来7天', '未来30天', '未来90天', '未来6个月'])
        self.end_quick_combo.currentIndexChanged.connect(lambda index: self.on_date_quick_changed(index, 'end'))

        end_range_layout.addWidget(self.end_date_from)
        end_range_layout.addWidget(QLabel('~'))
        end_range_layout.addWidget(self.end_date_to)
        end_range_layout.addWidget(self.end_quick_combo)

        query_layout2.addRow('结束时间范围', end_range_layout)

        # 立项年度范围
        approval_year_layout = QHBoxLayout()
        self.approval_year_from = QDateEdit()
        self.approval_year_from.setCalendarPopup(True)
        self.approval_year_from.setDisplayFormat('yyyy')
        self.approval_year_from.setDate(QDate.currentDate().addYears(-10))

        self.approval_year_to = QDateEdit()
        self.approval_year_to.setCalendarPopup(True)
        self.approval_year_to.setDisplayFormat('yyyy')
        self.approval_year_to.setDate(QDate.currentDate().addYears(10))

        # 立项年度快速选择
        self.approval_year_quick_combo = QComboBox()
        self.approval_year_quick_combo.addItems([
            '自定义', '近5年', '近10年', '近15年', '2020年至今'
        ])
        self.approval_year_quick_combo.currentIndexChanged.connect(
            lambda index: self.on_approval_year_quick_changed(index)
        )

        approval_year_layout.addWidget(self.approval_year_from)
        approval_year_layout.addWidget(QLabel('~'))
        approval_year_layout.addWidget(self.approval_year_to)
        approval_year_layout.addWidget(self.approval_year_quick_combo)
        query_layout1.addRow('立项年度范围', approval_year_layout)

        # 项目类型
        self.project_type_combo = QComboBox()
        self.project_type_combo.addItem('全部')
        query_layout2.addRow('项目类型', self.project_type_combo)
        # 项目状态
        self.status_combo = QComboBox()
        self.status_combo.addItem('全部')
        query_layout1.addRow('项目状态', self.status_combo)

        # 将两个FormLayout放入水平布局
        h_layout = QHBoxLayout()
        h_layout.addLayout(query_layout1)
        h_layout.addLayout(query_layout2)
        query_group.setLayout(h_layout)

        main_layout.addWidget(query_group)

        # 创建查询按钮区域
        btn_layout = QHBoxLayout()

        query_btn = QPushButton('查询')
        query_btn.clicked.connect(self.query_projects)
        btn_layout.addWidget(query_btn)

        reset_btn = QPushButton('重置')
        reset_btn.clicked.connect(self.reset_query)
        btn_layout.addWidget(reset_btn)

        main_layout.addLayout(btn_layout)

        # 创建结果展示区域
        self.result_splitter = QSplitter(Qt.Vertical)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(10)
        self.result_table.setHorizontalHeaderLabels([
            '选择', '项目名称', '负责人', '起始日期', '结束日期', '资助单位', '级别', '资助经费', '状态', '币种'
        ])
        # 设置表头样式
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # 添加双击事件处理
        self.result_table.doubleClicked.connect(self.on_project_double_clicked)
        # 添加表头点击事件处理
        header.sectionClicked.connect(self.on_header_clicked)
        # 添加单元格点击事件处理
        self.result_table.itemClicked.connect(self.on_item_clicked)
        self.result_splitter.addWidget(self.result_table)

        # 创建功能按钮区域
        action_btn_layout = QHBoxLayout()

        reminder_btn = QPushButton('添加提醒')
        reminder_btn.clicked.connect(self.add_reminder)
        action_btn_layout.addWidget(reminder_btn)

        delete_btn = QPushButton('一键删除')
        delete_btn.clicked.connect(self.batch_delete)
        action_btn_layout.addWidget(delete_btn)

        export_btn = QPushButton('导出CSV')
        export_btn.clicked.connect(self.export_results)
        action_btn_layout.addWidget(export_btn)

        export_excel_btn = QPushButton('导出Excel')
        export_excel_btn.clicked.connect(self.export_to_excel)
        action_btn_layout.addWidget(export_excel_btn)

        # 添加图表按钮
        chart_btn = QPushButton('根据查询结果显示统计图表')
        chart_btn.clicked.connect(self.show_chart_dialog)
        action_btn_layout.addWidget(chart_btn)
        action_btn_layout.addStretch()

        main_layout.addWidget(self.result_splitter)
        main_layout.addLayout(action_btn_layout)

    def load_project_status(self):
        # 加载项目状态
        from models.project import ProjectStatus
        self.status_combo.addItems([status.value for status in ProjectStatus])

    def load_funding_units(self):
        # 加载资助单位
        funding_units = self.query_logic.get_all_funding_units()
        self.funding_unit_combo.addItems(funding_units)

    def load_project_levels(self):
        # 加载项目级别
        from models.project import ProjectLevel
        self.level_combo.addItems([status.value for status in ProjectLevel])

    def load_departments(self):
        # 加载科室
        departments = self.query_logic.get_all_departments()
        self.department_combo.addItems(departments)

    def load_project_sources(self):
        # 加载项目来源
        sources = self.query_logic.get_all_project_sources()
        self.project_source_combo.addItems(sources)

    def load_project_types(self):
        # 加载项目类型
        types = self.query_logic.get_all_project_types()
        self.project_type_combo.addItems(types)

    def collect_query_conditions(self):
        # 收集查询条件
        conditions = {
            'project_name': self.project_name_edit.text(),
            'leader': self.leader_edit.text(),
            'department': self.department_combo.currentText() if self.department_combo.currentText() != '全部' else '',
            'project_source': self.project_source_combo.currentText() if self.project_source_combo.currentText() != '全部' else '',
            'project_type': self.project_type_combo.currentText() if self.project_type_combo.currentText() != '全部' else '',
            'funding_unit': self.funding_unit_combo.currentText() if self.funding_unit_combo.currentText() != '全部' else '',
            'level': self.level_combo.currentText() if self.level_combo.currentText() != '全部' else '',
            'status': self.status_combo.currentText() if self.status_combo.currentText() != '全部' else ''
        }

        # 处理开始日期范围 (项目在该时间范围内开始)
        start_from = ''
        start_to = ''
        if self.start_date_from.date().isValid():
            start_from = self.start_date_from.date().toString('yyyy-MM-dd')
        if self.start_date_to.date().isValid():
            start_to = self.start_date_to.date().toString('yyyy-MM-dd')
        if start_from:
            conditions['start_date_ge'] = start_from
        if start_to:
            conditions['start_date_le'] = start_to

        # 处理结束日期范围 (项目在该时间范围内结束)
        end_from = ''
        end_to = ''
        if self.end_date_from.date().isValid():
            end_from = self.end_date_from.date().toString('yyyy-MM-dd')
        if self.end_date_to.date().isValid():
            end_to = self.end_date_to.date().toString('yyyy-MM-dd')
        if end_from:
            conditions['end_date_ge'] = end_from
        if end_to:
            conditions['end_date_le'] = end_to

        # 处理立项年度范围
        approval_year_from = ''
        approval_year_to = ''
        if self.approval_year_from.date().isValid():
            approval_year_from = self.approval_year_from.date().toString('yyyy')
        if self.approval_year_to.date().isValid():
            approval_year_to = self.approval_year_to.date().toString('yyyy')
        if approval_year_from:
            conditions['approval_year_ge'] = approval_year_from
        if approval_year_to:
            conditions['approval_year_le'] = approval_year_to

        return conditions

    def query_projects(self):
        # 查询项目
        conditions = self.collect_query_conditions()
        projects = self.query_logic.query_projects(conditions)
        self.display_query_results(projects)

    def display_query_results(self, projects):
        # 显示查询结果
        self.result_table.setRowCount(0)
        self.projects_data = projects  # 保存项目数据
        self.selected_rows.clear()  # 清空选中行集合

        # 设置表头（确保已添加复选框列）
        if self.result_table.columnCount() != 14:
            self.result_table.setColumnCount(14)
            self.result_table.setHorizontalHeaderLabels([
                '选择', '项目名称', '负责人', '科室', '项目来源',
                '项目类型', '项目级别', '资助经费（万元）', '资助单位',
                '立项年度', '项目编号', '项目开始时间', '项目结束时间',
                '项目状态'
            ])

        # 设置表头复选框
        header_item = QTableWidgetItem()
        header_item.setCheckState(Qt.Unchecked)
        header_item.setText('全选')
        self.result_table.setHorizontalHeaderItem(0, header_item)

        # 填充数据
        for row, project in enumerate(projects):
            self.result_table.insertRow(row)

            # 添加复选框
            check_item = QTableWidgetItem()
            check_item.setCheckState(Qt.Unchecked)
            check_item.setData(Qt.UserRole, project.get('id'))
            self.result_table.setItem(row, 0, check_item)

            # 设置其他列数据
            self.result_table.setItem(row, 1, QTableWidgetItem(project.get('project_name', '')))
            self.result_table.setItem(row, 2, QTableWidgetItem(project.get('leader', '')))
            self.result_table.setItem(row, 3, QTableWidgetItem(project.get('department', '')))
            self.result_table.setItem(row, 4, QTableWidgetItem(project.get('project_source', '')))
            self.result_table.setItem(row, 5, QTableWidgetItem(project.get('project_type', '')))
            self.result_table.setItem(row, 6, QTableWidgetItem(project.get('level', '')))
            self.result_table.setItem(row, 7, QTableWidgetItem(str(project.get('funding_amount', ''))))
            self.result_table.setItem(row, 8, QTableWidgetItem(project.get('funding_unit', '')))
            self.result_table.setItem(row, 9, QTableWidgetItem(project.get('approval_year', '')))
            self.result_table.setItem(row, 10, QTableWidgetItem(project.get('project_number', '')))
            self.result_table.setItem(row, 11, QTableWidgetItem(project.get('start_date', '')))
            self.result_table.setItem(row, 12, QTableWidgetItem(project.get('end_date', '')))
            self.result_table.setItem(row, 13, QTableWidgetItem(project.get('status', '')))

        # 设置列宽
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(13, QHeaderView.ResizeToContents)
        for i in range(1, 13):
            self.result_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # 保存查询结果供图表使用
        self.projects_data = projects
        self.selected_rows = set()  # 跟踪选中的行
        self.select_all = False

        # 连接单元格点击事件以更新选中状态
        self.result_table.itemClicked.connect(self.on_item_clicked)

    def show_chart_dialog(self):
        """显示图表弹窗"""
        if not hasattr(self, 'projects_data') or not self.projects_data:
            QMessageBox.information(self, '提示', '请先查询项目数据')
            return

        # 创建并显示图表弹窗
        chart_dialog = ChartDialog(self, self.projects_data)
        chart_dialog.exec_()

    def on_date_quick_changed(self, index, date_type):
        current_date = QDate.currentDate()

        if date_type == 'start':
            from_edit = self.start_date_from
            to_edit = self.start_date_to
        else:
            from_edit = self.end_date_from
            to_edit = self.end_date_to

        if index == 0:  # 自定义
            # 清除日期设置，允许用户手动选择
            from_edit.setDate(current_date.addYears(-10))
            to_edit.setDate(current_date.addYears(10))
        elif index == 1:  # 近7天
            from_edit.setDate(current_date.addDays(-7))
            to_edit.setDate(current_date)
        elif index == 2:  # 近30天
            from_edit.setDate(current_date.addDays(-30))
            to_edit.setDate(current_date)
        elif index == 3:  # 近90天
            from_edit.setDate(current_date.addDays(-90))
            to_edit.setDate(current_date)
        elif index == 4:  # 近6个月
            from_edit.setDate(current_date.addMonths(-6))
            to_edit.setDate(current_date)
        elif index == 5:  # 近1年
            from_edit.setDate(current_date.addYears(-1))
            to_edit.setDate(current_date)
        elif index == 6:  # 未来7天
            from_edit.setDate(current_date)
            to_edit.setDate(current_date.addDays(7))
        elif index == 7:  # 未来30天
            from_edit.setDate(current_date)
            to_edit.setDate(current_date.addDays(30))
        elif index == 8:  # 未来90天
            from_edit.setDate(current_date)
            to_edit.setDate(current_date.addDays(90))
        elif index == 9:  # 未来6个月
            from_edit.setDate(current_date)
            to_edit.setDate(current_date.addMonths(6))

    def on_approval_year_quick_changed(self, index):
        current_date = QDate.currentDate()
        from_edit = self.approval_year_from
        to_edit = self.approval_year_to

        if index == 0:  # 自定义
            # 清除日期设置，允许用户手动选择
            from_edit.setDate(current_date.addYears(-10))
            to_edit.setDate(current_date.addYears(10))
        elif index == 1:  # 近5年
            from_edit.setDate(current_date.addYears(-5))
            to_edit.setDate(current_date)
        elif index == 2:  # 近10年
            from_edit.setDate(current_date.addYears(-10))
            to_edit.setDate(current_date)
        elif index == 3:  # 近15年
            from_edit.setDate(current_date.addYears(-15))
            to_edit.setDate(current_date)
        elif index == 4:  # 2020年至今
            from_edit.setDate(QDate(2020, 1, 1))
            to_edit.setDate(current_date)

    def reset_query(self):
        """重置查询条件"""
        # 清空输入框
        self.project_name_edit.clear()
        self.leader_edit.clear()

        # 重置日期
        self.start_date_from.setDate(QDate.currentDate().addYears(-10))
        self.start_date_to.setDate(QDate.currentDate().addYears(10))
        self.end_date_from.setDate(QDate.currentDate().addYears(-10))
        self.end_date_to.setDate(QDate.currentDate().addYears(10))
        self.approval_year_from.setDate(QDate.currentDate().addYears(-10))
        self.approval_year_to.setDate(QDate.currentDate().addYears(10))

        # 重置下拉框
        self.funding_unit_combo.setCurrentIndex(0)
        self.level_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.department_combo.setCurrentIndex(0)
        self.project_source_combo.setCurrentIndex(0)
        self.project_type_combo.setCurrentIndex(0)

        # 清空结果表格
        self.result_table.setRowCount(0)

        # 清除图表数据
        if hasattr(self, 'projects_data'):
            delattr(self, 'projects_data')

    def on_header_clicked(self, logical_index):
        """表头点击事件处理"""
        if logical_index == 0:  # 复选框列
            # 获取表头复选框状态
            header_item = self.result_table.horizontalHeaderItem(0)
            self.select_all = not self.select_all
            if self.select_all:
                check_state = Qt.Checked
                header_item.setText("取消")
            else:
                check_state = Qt.Unchecked
                header_item.setText("全选")

            # 更新所有行的复选框状态
            for row in range(self.result_table.rowCount()):
                item = self.result_table.item(row, 0)
                item.setCheckState(check_state)

                # 更新选中行集合
                project_id = item.data(Qt.UserRole)
                if check_state == Qt.Checked:
                    self.selected_rows.add(project_id)
                else:
                    self.selected_rows.discard(project_id)

    def on_item_clicked(self, item):
        """单元格点击事件处理"""
        if item.column() == 0:  # 复选框列
            # 更新选中行集合
            project_id = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                self.selected_rows.add(project_id)
            else:
                self.selected_rows.discard(project_id)

            # 更新表头复选框状态
            all_checked = True
            all_unchecked = True
            for row in range(self.result_table.rowCount()):
                if not all_checked and not all_unchecked:
                    break
                row_item = self.result_table.item(row, 0)
                if row_item.checkState() != Qt.Checked:
                    all_checked = False
                if row_item.checkState() != Qt.Unchecked:
                    all_unchecked = False

            header_item = self.result_table.horizontalHeaderItem(0)
            if all_checked:
                header_item.setCheckState(Qt.Checked)
            elif all_unchecked:
                header_item.setCheckState(Qt.Unchecked)
            else:
                header_item.setCheckState(Qt.PartiallyChecked)

    def on_project_double_clicked(self, index):
        """双击项目行事件处理"""
        # 获取选中行
        row = index.row()
        # 从保存的项目数据中获取项目ID
        if hasattr(self, 'projects_data') and 0 <= row < len(self.projects_data):
            project = self.projects_data[row]
            project_id = project.get('id')

            if project_id:
                try:
                    # 使用ProjectEditorDialog对话框
                    editor = ProjectEditorDialog(project_id=project_id, parent=self)
                    editor.setWindowTitle(f'编辑项目: {project.get("project_name", "未命名项目")}')

                    # 显示对话框
                    result = editor.exec_()

                except Exception as e:
                    print(f'创建项目编辑对话框时出错: {str(e)}')
                    QMessageBox.critical(self, '错误', f'创建项目编辑对话框时出错: {str(e)}')
            else:
                QMessageBox.warning(self, '错误', '无法获取项目ID')
        else:
            QMessageBox.warning(self, '错误', '无法获取项目数据')

    def add_reminder(self):
        """添加提醒功能"""
        if not self.selected_rows:
            QMessageBox.warning(self, '提示', '请先选择项目')
            return

        # 打开提醒编辑对话框
        try:
            # 动态导入提醒对话框
            from ui.reminder_dialog import BatchReminderDialog
            batch_dialog = BatchReminderDialog(project_ids=self.selected_rows)
            if batch_dialog.exec_() == QDialog.Accepted:
                reminder_data = batch_dialog.get_reminder_data()
                # 调用提醒逻辑批量添加提醒
                from logic.reminder_logic import ReminderLogic
                reminder_logic = ReminderLogic()
                success_count = 0
                fail_count = 0
                for project_id in reminder_data['project_ids']:
                    project = self.project_logic.get_project_by_id(project_id)
                    if project:
                        reminder_create_data = {
                            'project_id': project_id,
                            'project_name': project.project_name,
                            'reminder_type': reminder_data['reminder_type'],
                            'days_before': reminder_data['days_before'],
                            'reminder_way': reminder_data['reminder_way'],
                            'content': reminder_data['content'],
                            'start_date': reminder_data['start_date']  # 添加start_date字段
                        }
                        if reminder_logic.create_reminder(reminder_create_data):
                            success_count += 1
                        else:
                            fail_count += 1
                QMessageBox.information(self, '批量添加结果', f'成功添加{success_count}个提醒，失败{fail_count}个')
        except Exception as e:
            print(f'打开提醒对话框时出错: {str(e)}')
            QMessageBox.critical(self, '错误', f'打开提醒对话框时出错: {str(e)}')

    def batch_delete(self):
        """批量删除功能"""
        if not self.selected_rows:
            QMessageBox.warning(self, '提示', '请先选择项目')
            return

        reply = QMessageBox.question(self, '确认', f'确定要删除选中的{len(self.selected_rows)}个项目吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                success_count = 0
                for project_id in self.selected_rows:
                    if self.project_logic.delete_project(project_id):
                        success_count += 1
                QMessageBox.information(self, '成功',
                                        f'成功删除{success_count}个项目，失败{len(self.selected_rows) - success_count}个项目')
                # 重新查询以更新结果
                self.query_projects()
            except Exception as e:
                print(f'批量删除项目时出错: {str(e)}')
                QMessageBox.critical(self, '错误', f'批量删除项目时出错: {str(e)}')

    def export_results(self):
        """导出查询结果到CSV文件"""
        if not hasattr(self, 'projects_data') or not self.projects_data:
            QMessageBox.information(self, '提示', '没有查询结果可导出')
            return
        if not self.selected_rows:
            QMessageBox.warning(self, '提示', '请先选择项目')
            return

        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出结果', os.path.expanduser('~'), 'CSV文件 (*.csv)'
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
                writer = csv.writer(csv_file)
                # 写入表头
                headers = [
                    '项目名称', '负责人', '科室', '联系电话', '项目来源',
                    '项目类型', '项目级别', '资助经费（万元）', '资助单位',
                    '立项年度', '项目编号', '项目开始时间', '项目结束时间', '项目状态'
                ]
                writer.writerow(headers)

                # 写入数据
                for project in self.projects_data:
                    if project["id"] not in self.selected_rows:
                        continue
                    row_data = [
                        project.get('project_name', ''),
                        project.get('leader', ''),
                        project.get('department', ''),
                        project.get('phone', ''),
                        project.get('source', ''),
                        project.get('type', ''),
                        project.get('level', ''),
                        project.get('funding_amount', ''),
                        project.get('funding_unit', ''),
                        project.get('approval_year', ''),
                        project.get('project_code', ''),
                        project.get('start_date', ''),
                        project.get('end_date', ''),
                        project.get('status', '')
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, '成功', f'结果已导出到: {file_path}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败: {str(e)}')

    def export_to_excel(self):
        """导出查询结果到Excel文件"""
        if not hasattr(self, 'projects_data') or not self.projects_data:
            QMessageBox.information(self, '提示', '没有查询结果可导出')
            return
        if not self.selected_rows:
            QMessageBox.warning(self, '提示', '请先选择项目')
            return

        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出到Excel', os.path.expanduser('~'), 'Excel文件 (*.xlsx)'
        )

        if not file_path:
            return

        try:
            from utils.excel_handler import ExcelExporter
            exporter = ExcelExporter()

            # 筛选选中的项目数据
            selected_projects = [p for p in self.projects_data if p["id"] in self.selected_rows]

            success = exporter.export_projects_to_excel(selected_projects, file_path)

            if success:
                QMessageBox.information(self, '成功', f'项目数据已导出到: {file_path}')
            else:
                QMessageBox.critical(self, '错误', '导出失败')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败: {str(e)}')
