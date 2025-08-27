#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 图表工具
"""
import matplotlib

matplotlib.use('Qt5Agg')  # 使用Qt5作为后端
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os


class ChartUtils:
    """图表工具类"""

    @staticmethod
    def generate_bar_chart(data, x_label, y_label, title, figsize=(10, 6), color='skyblue'):
        """生成柱状图"""
        plt.figure(figsize=figsize)
        plt.bar(data.keys(), data.values(), color=color)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt

    @staticmethod
    def generate_pie_chart(data, title, figsize=(10, 6), autopct='%1.1f%%'):
        """生成饼图"""
        plt.figure(figsize=figsize)
        plt.pie(data.values(), labels=data.keys(), autopct=autopct, shadow=True, startangle=90)
        plt.axis('equal')  # 确保饼图是圆的
        plt.title(title)
        return plt

    @staticmethod
    def generate_line_chart(data, x_label, y_label, title, figsize=(10, 6), color='blue'):
        """生成折线图"""
        plt.figure(figsize=figsize)
        plt.plot(list(data.keys()), list(data.values()), marker='o', color=color)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        return plt

    @staticmethod
    def export_chart(plt, file_path, dpi=300):
        """导出图表为图片"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            plt.savefig(file_path, dpi=dpi)
            plt.close()
            return True
        except Exception as e:
            print(f"导出图表失败: {e}")
            return False

    @staticmethod
    def create_chart_canvas(plt):
        """创建Qt图表画布"""
        canvas = FigureCanvas(plt.gcf())
        return canvas


# 生成柱状图
def generate_bar_chart(data, x_label, y_label, title, figsize=(10, 6), color='skyblue'):
    return ChartUtils.generate_bar_chart(data, x_label, y_label, title, figsize, color)


# 生成饼图
def generate_pie_chart(data, title, figsize=(10, 6), autopct='%1.1f%%'):
    return ChartUtils.generate_pie_chart(data, title, figsize, autopct)


# 生成折线图
def generate_line_chart(data, x_label, y_label, title, figsize=(10, 6), color='blue'):
    return ChartUtils.generate_line_chart(data, x_label, y_label, title, figsize, color)
