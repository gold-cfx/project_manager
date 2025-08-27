#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 图表弹窗
"""
import matplotlib

matplotlib.use('Qt5Agg')  # 使用Qt5作为后端
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QTabWidget, QWidget, QPushButton)

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


class ChartDialog(QDialog):
    """图表弹窗类"""

    def __init__(self, parent=None, projects_data=None):
        super().__init__(parent)
        self.setWindowTitle('图表显示')
        self.setModal(True)
        self.resize(800, 600)  # 设置弹窗大小
        self.projects_data = projects_data
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建图表数据类型选择区域
        chart_type_layout = QHBoxLayout()
        chart_type_layout.addWidget(QLabel('图表数据类型:'))
        self.chart_data_combo = QComboBox()
        self.chart_data_combo.addItems([
            '按级别统计项目数量', '按资助单位统计项目数量',
            '按年份统计项目数量', '按级别统计资助金额'
        ])
        self.chart_data_combo.currentIndexChanged.connect(self.generate_charts)
        chart_type_layout.addWidget(self.chart_data_combo)
        chart_type_layout.addStretch()

        main_layout.addLayout(chart_type_layout)

        # 创建图表展示区域
        self.chart_tab = QTabWidget()

        # 柱状图
        self.bar_chart_widget = QWidget()
        self.bar_chart_layout = QVBoxLayout(self.bar_chart_widget)
        self.bar_figure = Figure(figsize=(5, 4), dpi=100)
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_chart_layout.addWidget(self.bar_canvas)
        self.chart_tab.addTab(self.bar_chart_widget, '柱状图')

        # 饼图
        self.pie_chart_widget = QWidget()
        self.pie_chart_layout = QVBoxLayout(self.pie_chart_widget)
        self.pie_figure = Figure(figsize=(5, 4), dpi=100)
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_chart_layout.addWidget(self.pie_canvas)
        self.chart_tab.addTab(self.pie_chart_widget, '饼图')

        # 折线图
        self.line_chart_widget = QWidget()
        self.line_chart_layout = QVBoxLayout(self.line_chart_widget)
        self.line_figure = Figure(figsize=(5, 4), dpi=100)
        self.line_canvas = FigureCanvas(self.line_figure)
        self.line_chart_layout.addWidget(self.line_canvas)
        self.chart_tab.addTab(self.line_chart_widget, '折线图')

        main_layout.addWidget(self.chart_tab)

        # 添加关闭按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

        # 初始生成图表
        self.generate_charts()

    def generate_charts(self):
        """生成图表"""
        if not self.projects_data:
            return

        chart_type = self.chart_data_combo.currentText()

        # 清除现有图表
        self.bar_figure.clear()
        self.pie_figure.clear()
        self.line_figure.clear()

        # 根据选择的图表类型生成数据
        if chart_type == '按级别统计项目数量':
            self.generate_level_count_charts()
        elif chart_type == '按资助单位统计项目数量':
            self.generate_funding_unit_count_charts()
        elif chart_type == '按年份统计项目数量':
            self.generate_year_count_charts()
        elif chart_type == '按级别统计资助金额':
            self.generate_level_funding_charts()

        # 刷新画布
        self.bar_canvas.draw()
        self.pie_canvas.draw()
        self.line_canvas.draw()

    def generate_level_count_charts(self):
        """按级别统计项目数量"""
        # 准备数据
        from models.project import ProjectLevel
        level_counts = {level.value: 0 for level in ProjectLevel}
        for project in self.projects_data:
            level = project['level']
            if level in level_counts:
                level_counts[level] += 1
            else:
                level_counts['其他'] = level_counts.get('其他', 0) + 1

        # 绘制柱状图
        ax_bar = self.bar_figure.add_subplot(111)
        levels = list(level_counts.keys())
        counts = list(level_counts.values())
        ax_bar.bar(levels, counts)
        ax_bar.set_title('按级别统计项目数量')
        ax_bar.set_xlabel('项目级别')
        ax_bar.set_ylabel('项目数量')
        ax_bar.tick_params(axis='x', rotation=45)

        # 绘制饼图
        ax_pie = self.pie_figure.add_subplot(111)
        ax_pie.pie(counts, labels=levels, autopct='%1.1f%%')
        ax_pie.set_title('项目级别分布')

    def generate_funding_unit_count_charts(self):
        """按资助单位统计项目数量"""
        # 准备数据
        unit_counts = {}
        for project in self.projects_data:
            unit = project['funding_unit']
            if unit in unit_counts:
                unit_counts[unit] += 1
            else:
                unit_counts[unit] = 1

        # 限制显示的单位数量，避免图表过于拥挤
        if len(unit_counts) > 5:
            # 取前5个，其余合并为'其他'
            sorted_units = sorted(unit_counts.items(), key=lambda x: x[1], reverse=True)
            top_units = sorted_units[:5]
            other_count = sum(item[1] for item in sorted_units[5:])
            unit_counts = dict(top_units)
            unit_counts['其他'] = other_count

        # 绘制柱状图
        ax_bar = self.bar_figure.add_subplot(111)
        units = list(unit_counts.keys())
        counts = list(unit_counts.values())
        ax_bar.bar(units, counts)
        ax_bar.set_title('按资助单位统计项目数量')
        ax_bar.set_xlabel('资助单位')
        ax_bar.set_ylabel('项目数量')
        ax_bar.tick_params(axis='x', rotation=45)

        # 绘制饼图
        ax_pie = self.pie_figure.add_subplot(111)
        ax_pie.pie(counts, labels=units, autopct='%1.1f%%')
        ax_pie.set_title('资助单位分布')

    def generate_year_count_charts(self):
        """按年份统计项目数量"""
        # 准备数据
        year_counts = {}
        for project in self.projects_data:
            # 假设start_date格式为'YYYY-MM-DD'
            year = project['start_date'].split('-')[0]
            if year in year_counts:
                year_counts[year] += 1
            else:
                year_counts[year] = 1

        # 按年份排序
        sorted_years = sorted(year_counts.keys())
        year_counts = {year: year_counts[year] for year in sorted_years}

        # 绘制柱状图
        ax_bar = self.bar_figure.add_subplot(111)
        years = list(year_counts.keys())
        counts = list(year_counts.values())
        ax_bar.bar(years, counts)
        ax_bar.set_title('按年份统计项目数量')
        ax_bar.set_xlabel('年份')
        ax_bar.set_ylabel('项目数量')

        # 绘制折线图
        ax_line = self.line_figure.add_subplot(111)
        ax_line.plot(years, counts, marker='o')
        ax_line.set_title('项目数量年度趋势')
        ax_line.set_xlabel('年份')
        ax_line.set_ylabel('项目数量')
        ax_line.grid(True)

    def generate_level_funding_charts(self):
        """按级别统计资助金额"""
        # 准备数据
        from models.project import ProjectLevel
        level_funding = {level.value: 0 for level in ProjectLevel}
        for project in self.projects_data:
            level = project['level']
            try:
                # 假设funding_amount是字符串，需要转换为浮点数
                amount = float(project['funding_amount'])
                if level in level_funding:
                    level_funding[level] += amount
                else:
                    level_funding['其他'] = level_funding.get('其他', 0) + amount
            except (ValueError, TypeError):
                # 如果无法转换，跳过
                continue

        # 绘制柱状图
        ax_bar = self.bar_figure.add_subplot(111)
        levels = list(level_funding.keys())
        funding = list(level_funding.values())
        ax_bar.bar(levels, funding)
        ax_bar.set_title('按级别统计资助金额')
        ax_bar.set_xlabel('项目级别')
        ax_bar.set_ylabel('资助金额')
        ax_bar.tick_params(axis='x', rotation=45)

        # 绘制饼图
        ax_pie = self.pie_figure.add_subplot(111)
        ax_pie.pie(funding, labels=levels, autopct='%1.1f%%')
        ax_pie.set_title('资助金额级别分布')
