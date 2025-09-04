#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目登记界面
"""
from PyQt5.QtWidgets import QLabel, QMessageBox, QPushButton, QFileDialog

from ui.data_editor import ProjectEditor
from utils.excel_handler import ExcelTemplateGenerator, ExcelImporter
from utils.logger import get_logger

logger = get_logger(__name__)


class ProjectRegistration(ProjectEditor):
    def __init__(self):
        # 调用父类构造函数，不传入项目ID表示新建项目
        super().__init__(project_id=None)
        # 修改标题为项目登记
        self.set_title('项目登记')
        # 设置状态标签初始文本
        self.base_editor.status_label.setText('请填写项目信息')
        self.base_editor.status_label.setStyleSheet('color: black')

        # 初始化项目逻辑
        from logic.project_logic import ProjectLogic
        self.project_logic = ProjectLogic()

        # 添加Excel功能按钮
        self.init_excel_buttons()

    def init_excel_buttons(self):
        """初始化Excel功能按钮"""
        # 创建Excel功能按钮布局
        # excel_layout = QHBoxLayout()

        # 下载模板按钮
        self.download_template_btn = QPushButton('下载Excel模板')
        self.download_template_btn.clicked.connect(self.download_template)
        # excel_layout.addWidget(self.download_template_btn)

        # 批量导入按钮
        self.import_excel_btn = QPushButton('批量导入Excel项目')
        self.import_excel_btn.clicked.connect(self.import_from_excel)
        # excel_layout.addWidget(self.import_excel_btn)

        # 将按钮添加到主布局
        main_layout = self.layout()
        if main_layout:
            # 找到按钮区域并插入Excel按钮
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if hasattr(item, 'layout') and item.layout():
                    sub_layout = item.layout()
                    all_widget = [sub_layout.itemAt(j).widget() for j in range(sub_layout.count()) if
                                  sub_layout.itemAt(j)]
                    if any(isinstance(w, QPushButton) for w in all_widget):
                        # 在现有按钮布局中插入Excel按钮
                        sub_layout.addWidget(self.download_template_btn)
                        sub_layout.addWidget(self.import_excel_btn)
                        # main_layout.insertLayout(i, excel_layout)
                        break

    def set_title(self, title):
        # 查找并修改标题标签
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            widget = item.widget()
            if isinstance(widget, QLabel) and widget.font().pointSize() == 16:
                widget.setText(title)
                break

    def download_template(self):
        """下载Excel模板"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                '保存Excel模板',
                '项目信息模板.xlsx',
                'Excel Files (*.xlsx)'
            )

            if file_path:
                if ExcelTemplateGenerator.generate_project_template(file_path):
                    QMessageBox.information(
                        self,
                        '成功',
                        f'Excel模板已下载到：\n{file_path}'
                    )
                else:
                    QMessageBox.warning(
                        self,
                        '失败',
                        '下载模板失败，请重试'
                    )
        except Exception as e:
            QMessageBox.warning(
                self,
                '错误',
                f'下载模板时出错：\n{str(e)}'
            )

    def import_from_excel(self):
        """从Excel批量导入项目"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                '选择Excel文件',
                '',
                'Excel Files (*.xlsx *.xls)'
            )

            if file_path:
                # 导入数据
                projects = ExcelImporter.import_projects_from_excel(file_path)

                if not projects:
                    QMessageBox.information(
                        self,
                        '提示',
                        'Excel文件中没有找到有效数据'
                    )
                    return

                # 显示导入预览
                reply = QMessageBox.question(
                    self,
                    '确认导入',
                    f'找到 {len(projects)} 个项目信息，\n'
                    f'是否确认导入？\n'
                    f'（已存在项目名称将被跳过）',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    self.import_projects_batch(projects)

        except Exception as e:
            QMessageBox.warning(
                self,
                '导入失败',
                f'导入Excel时出错：\n{str(e)}'
            )

    def import_projects_batch(self, projects: list):
        """批量导入项目"""
        try:
            from models.project import ProjectCreate

            success_count = 0
            skip_count = 0
            error_count = 0

            for project_data in projects:
                try:
                    # 检查项目名称是否已存在
                    if self.project_logic.is_project_name_exists(project_data['project_name']):
                        skip_count += 1
                        continue

                    # 创建项目
                    project_create = ProjectCreate(**project_data)
                    project_id = self.project_logic.create_project(project_create)

                    if project_id > 0:
                        success_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    logger.error(f"导入项目失败: {str(e)}")
                    continue

            # 显示导入结果
            message = f'导入完成！\n'
            message += f'成功：{success_count} 个\n'
            message += f'跳过：{skip_count} 个（已存在）\n'
            message += f'失败：{error_count} 个'

            QMessageBox.information(self, '导入结果', message)

            # 如果导入成功，刷新项目列表（如果有）
            if success_count > 0:
                # 通知主界面刷新项目列表
                pass

        except Exception as e:
            QMessageBox.warning(
                self,
                '批量导入失败',
                f'批量导入时出错：\n{str(e)}'
            )

    def save_project(self):
        # 重写保存方法，添加保存成功后的重置表单逻辑
        if self.validate_form():
            project_data = self.collect_form_data()
            from models.project import ProjectCreate
            project_create = ProjectCreate(**project_data)
            success = self.project_logic.create_project(project_create) > 0
            if success:
                QMessageBox.information(self, '保存成功', '项目信息已成功保存')
                self.reset_form()
            else:
                QMessageBox.warning(self, '保存失败', '项目信息保存失败，请重试')

    def reset_form(self):
        # 重置表单
        super().reset_form()
        # 额外重置状态标签
        self.base_editor.status_label.setText('请填写项目信息')
        self.base_editor.status_label.setStyleSheet('color: black')
