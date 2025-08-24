#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据编辑公共模块
"""
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QComboBox, QDoubleSpinBox, QPushButton, QMessageBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QDialog, QDialogButtonBox, QListWidget, QFileDialog, QListWidgetItem
)
import os
from logic.project_logic import ProjectLogic
from logic.project_result_logic import ProjectResultLogic
from logic.project_result_attachment_logic import ProjectResultAttachmentLogic
from utils.validator import Validator


class ResultDialog(QDialog):
    """成果添加/编辑弹窗"""

    def __init__(self, parent=None, result_data=None, project_result_id=None):
        super().__init__(parent)
        self.setWindowTitle('添加成果')
        self.setModal(True)
        self.result_data = result_data or {}
        self.project_result_id = project_result_id
        self.attachment_logic = ProjectResultAttachmentLogic()
        self.attachments_to_delete = []
        self.attachments_to_add = []
        self.init_ui()
        if self.project_result_id:
            self.load_attachments()

    def init_ui(self):
        # 设置弹窗宽度
        self.setFixedWidth(500)
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建表单布局
        form_layout = QFormLayout()

        # 成果类型
        self.result_type_combo = QComboBox()
        # 使用 ProjectResultType 枚举中定义的值
        from models.project_result import ProjectResultType
        self.result_type_combo.addItems([result_type.value for result_type in ProjectResultType])
        form_layout.addRow('成果类型 *', self.result_type_combo)

        # 成果名称
        self.result_name_edit = QLineEdit()
        self.result_name_edit.setPlaceholderText('请输入成果名称')
        form_layout.addRow('成果名称 *', self.result_name_edit)

        # 发表/获得时间
        self.result_date_edit = QDateEdit(QDate.currentDate())
        self.result_date_edit.setCalendarPopup(True)
        form_layout.addRow('发表/获得时间 *', self.result_date_edit)

        main_layout.addLayout(form_layout)

        # 附件管理
        attachment_group = QGroupBox('附件管理')
        attachment_layout = QVBoxLayout()

        self.attachment_list = QListWidget()
        attachment_layout.addWidget(self.attachment_list)

        attachment_btn_layout = QHBoxLayout()
        add_attachment_btn = QPushButton('添加附件')
        add_attachment_btn.clicked.connect(self.add_attachment)
        remove_attachment_btn = QPushButton('删除附件')
        remove_attachment_btn.clicked.connect(self.remove_attachment)
        download_attachment_btn = QPushButton('下载附件')
        download_attachment_btn.clicked.connect(self.download_attachment)
        attachment_btn_layout.addWidget(add_attachment_btn)
        attachment_btn_layout.addWidget(remove_attachment_btn)
        attachment_btn_layout.addWidget(download_attachment_btn)
        attachment_layout.addLayout(attachment_btn_layout)

        attachment_group.setLayout(attachment_layout)
        main_layout.addWidget(attachment_group)

        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # 如果有数据，填充表单
        if self.result_data:
            self.setWindowTitle('编辑成果')
            if 'type' in self.result_data:
                index = self.result_type_combo.findText(self.result_data['type'])
                if index >= 0:
                    self.result_type_combo.setCurrentIndex(index)
            if 'name' in self.result_data:
                self.result_name_edit.setText(self.result_data['name'])
            if 'date' in self.result_data:
                date = QDate.fromString(self.result_data['date'], 'yyyy-MM-dd')
                if date.isValid():
                    self.result_date_edit.setDate(date)

    def load_attachments(self):
        self.attachment_list.clear()
        attachments = self.attachment_logic.get_attachments_by_result(self.project_result_id)
        for attachment in attachments:
            item = QListWidgetItem(attachment['file_name'])
            item.setData(Qt.UserRole, attachment)
            self.attachment_list.addItem(item)

    def add_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择附件', '', 'All Files (*)')
        if file_path:
            file_name = os.path.basename(file_path)
            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, {'file_path': file_path, 'is_new': True})
            self.attachment_list.addItem(item)
            self.attachments_to_add.append(file_path)

    def remove_attachment(self):
        selected_item = self.attachment_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '提示', '请选择要删除的附件')
            return

        attachment_data = selected_item.data(Qt.UserRole)
        # 如果是已存在的附件，将其ID添加到待删除列表
        if 'id' in attachment_data and not attachment_data.get('is_new', False):
            self.attachments_to_delete.append(attachment_data['id'])
        # 如果是新添加的附件，从待添加列表中移除
        elif attachment_data.get('is_new', False) and 'file_path' in attachment_data:
            if attachment_data['file_path'] in self.attachments_to_add:
                self.attachments_to_add.remove(attachment_data['file_path'])

        self.attachment_list.takeItem(self.attachment_list.row(selected_item))

    def download_attachment(self):
        selected_item = self.attachment_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '提示', '请选择要下载的附件')
            return

        attachment_data = selected_item.data(Qt.UserRole)
        if attachment_data.get('is_new', False):
            QMessageBox.information(self, '提示', '新添加的附件尚未保存，无法下载')
            return

        file_path = attachment_data.get('file_path')
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, '错误', '附件文件不存在')
            return

        save_path, _ = QFileDialog.getSaveFileName(self, '保存附件', attachment_data['file_name'])
        if save_path:
            try:
                import shutil
                shutil.copy2(file_path, save_path)
                QMessageBox.information(self, '成功', '附件下载成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'下载失败: {e}')

    def get_result_data(self):
        """获取成果数据"""
        return {
            'type': self.result_type_combo.currentText(),
            'name': self.result_name_edit.text(),
            'date': self.result_date_edit.date().toString('yyyy-MM-dd'),
            'attachments_to_add': self.attachments_to_add,
            'attachments_to_delete': self.attachments_to_delete
        }

    def accept(self):
        """验证并接受表单"""
        result_name = self.result_name_edit.text()
        if not result_name:
            QMessageBox.warning(self, '输入错误', '成果名称不能为空')
            return
        super().accept()


class BaseProjectEditor(object):
    """项目编辑基类，包含共享的数据处理逻辑"""

    def __init__(self, project_id=None):
        self.project_logic = ProjectLogic()
        self.attachment_logic = ProjectResultAttachmentLogic()
        self.project_id = project_id
        self.original_project_name = None  # 初始化原始项目名称
        self.widget = None  # 存储UI组件的引用
        self.project_result_logic = ProjectResultLogic()

        print(f'创建BaseProjectEditor实例，项目ID: {project_id}')

    def init_ui(self, widget):
        """初始化UI，需要由子类提供widget"""
        self.widget = widget
        # 设置窗口属性
        self.widget.setMinimumSize(800, 600)

        # 创建主布局
        main_layout = QVBoxLayout(self.widget)

        # 创建标题
        title_label = QLabel('项目编辑')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 项目基本信息组
        basic_info_group = QGroupBox('项目基本信息')
        # 创建水平布局（用于并排放置两个 QFormLayout）
        self.h_layout = QHBoxLayout()
        
        # 创建第一个FormLayout
        basic_info_layout1 = QFormLayout()

        # 创建第二个FormLayout
        basic_info_layout2 = QFormLayout()
        
        # 项目名称
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText('请输入项目名称')
        self.project_name_edit.textChanged.connect(self.on_project_name_changed)
        basic_info_layout1.addRow('项目名称 *', self.project_name_edit)

        # 项目负责人
        self.leader_edit = QLineEdit()
        self.leader_edit.setPlaceholderText('请输入项目负责人')
        basic_info_layout2.addRow('项目负责人 *', self.leader_edit)

        # 科室
        self.department_edit = QLineEdit()
        self.department_edit.setPlaceholderText('请输入科室')
        basic_info_layout1.addRow('科室 *', self.department_edit)

        # 联系电话
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText('请输入联系电话')
        basic_info_layout2.addRow('联系电话 *', self.phone_edit)

        # 项目来源
        self.source_combo = QComboBox()
        self.source_combo.addItems(['请选择项目来源', '国家自然科学基金', '科技部项目', '教育部项目', '省级科技计划', '市级科技计划', '其他'])        
        basic_info_layout1.addRow('项目来源 *', self.source_combo)

        # 项目类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(['纵向课题', '横向课题', '研究者发起的临床研究项目', 'GCP项目'])        
        basic_info_layout2.addRow('项目类型 *', self.type_combo)

        
        # 项目级别
        self.level_combo = QComboBox()
        # 使用 ProjectLevel 枚举中定义的值
        from models.project import ProjectLevel
        self.level_combo.addItems([level.value for level in ProjectLevel])        
        basic_info_layout1.addRow('项目级别 *', self.level_combo)

        # 资助经费（万元）
        self.funding_amount_edit = QDoubleSpinBox()
        self.funding_amount_edit.setRange(0, 10000000)
        self.funding_amount_edit.setDecimals(2)
        basic_info_layout2.addRow('资助经费（万元） *', self.funding_amount_edit)

        # 资助单位
        self.funding_unit_edit = QLineEdit()
        self.funding_unit_edit.setPlaceholderText('请输入资助单位')
        basic_info_layout1.addRow('资助单位 *', self.funding_unit_edit)

        # 立项年度
        self.approval_year_edit = QLineEdit()
        self.approval_year_edit.setPlaceholderText('请输入立项年度，格式：YYYY')
        basic_info_layout2.addRow('立项年度 *', self.approval_year_edit)

        # 项目编号
        self.project_code_edit = QLineEdit()
        self.project_code_edit.setPlaceholderText('请输入项目编号')
        basic_info_layout1.addRow('项目编号 *', self.project_code_edit)
        # 项目状态
        self.status_combo = QComboBox()
        # 使用 ProjectStatus 枚举中定义的值
        from models.project import ProjectStatus
        self.status_combo.addItems([status.value for status in ProjectStatus])
        basic_info_layout2.addRow('项目状态 *', self.status_combo)

        # 项目开始时间
        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.dateChanged.connect(self.on_date_changed)
        basic_info_layout1.addRow('项目开始时间 *', self.start_date_edit)

        # 项目结束时间
        self.end_date_edit = QDateEdit(QDate.currentDate().addYears(1))
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.dateChanged.connect(self.on_date_changed)
        basic_info_layout2.addRow('项目结束时间 *', self.end_date_edit)



        # 项目持续时间
        self.duration_label = QLabel('1 年')
        basic_info_layout1.addRow('项目持续时间', self.duration_label)

        # 将两个FormLayout添加到水平布局
        self.h_layout.addLayout(basic_info_layout1)
        self.h_layout.addLayout(basic_info_layout2)
        basic_info_group.setLayout(self.h_layout)
        main_layout.addWidget(basic_info_group)


        # 创建项目result信息组
        result_info_group = QGroupBox('项目成果信息')
        result_info_layout = QVBoxLayout()

        # 成果列表
        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(['成果类型', '成果名称', '发表/获得时间'])
        # 设置列宽
        self.result_table.setColumnWidth(0, 120)
        self.result_table.setColumnWidth(1, 300)
        self.result_table.setColumnWidth(2, 150)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.doubleClicked.connect(self.edit_result)
        result_info_layout.addWidget(self.result_table)

        # 成果操作按钮布局
        btn_layout = QHBoxLayout()

        # 添加成果按钮
        add_result_btn = QPushButton('添加成果')
        add_result_btn.clicked.connect(self.add_result)
        btn_layout.addWidget(add_result_btn)

        # 删除成果按钮
        delete_result_btn = QPushButton('删除选中成果')
        delete_result_btn.clicked.connect(self.delete_selected_result)
        btn_layout.addWidget(delete_result_btn)

        result_info_layout.addLayout(btn_layout)

        result_info_group.setLayout(result_info_layout)
        main_layout.addWidget(result_info_group)

        # 创建按钮区域
        btn_layout = QHBoxLayout()

        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_project)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton('重置')
        reset_btn.clicked.connect(self.reset_form)
        btn_layout.addWidget(reset_btn)

        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.on_cancel)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)

        # 添加状态栏
        self.status_label = QLabel('请填写项目信息')
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    def load_funding_units(self):
        # 已移除，资助单位现在是文本输入框
        pass

    def load_project_data(self, project_id):
        # 加载项目数据
        project = self.project_logic.get_project_by_id(project_id)
        if not project:
            QMessageBox.warning(self.widget, '错误', '无法找到项目数据')
            return

        # 保存原始项目名称
        self.original_project_name = project.project_name

        # 填充基本信息
        self.project_name_edit.setText(project.project_name)
        self.leader_edit.setText(project.leader)
        self.department_edit.setText(project.department if hasattr(project, 'department') else '')
        self.phone_edit.setText(project.phone)
        
        # 设置项目来源
        source_index = self.source_combo.findText(project.project_source if hasattr(project, 'project_source') else '')
        if source_index >= 0:
            self.source_combo.setCurrentIndex(source_index)
        
        # 设置项目类型
        type_index = self.type_combo.findText(project.project_type if hasattr(project, 'project_type') else '')
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        # 设置立项年度和项目编号
        self.approval_year_edit.setText(project.approval_year if hasattr(project, 'approval_year') else '')
        self.project_code_edit.setText(project.project_number if hasattr(project, 'project_number') else '')

        # 设置日期
        if isinstance(project.start_date, str):
            start_date = QDate.fromString(project.start_date, 'yyyy-MM-dd')
        else:
            # 如果是 datetime.date 对象，直接转换为 QDate
            start_date = QDate(project.start_date.year, project.start_date.month, project.start_date.day)
        if start_date.isValid():
            self.start_date_edit.setDate(start_date)

        if isinstance(project.end_date, str):
            end_date = QDate.fromString(project.end_date, 'yyyy-MM-dd')
        else:
            # 如果是 datetime.date 对象，直接转换为 QDate
            end_date = QDate(project.end_date.year, project.end_date.month, project.end_date.day)
        if end_date.isValid():
            self.end_date_edit.setDate(end_date)

        # 设置资助信息
        funding_unit = project.funding_unit
        self.funding_unit_edit.setText(funding_unit)

        level_index = self.level_combo.findText(project.level)
        if level_index >= 0:
            self.level_combo.setCurrentIndex(level_index)

        self.funding_amount_edit.setValue(float(project.funding_amount))
        # 已移除货币单位字段

        status_index = self.status_combo.findText(project.status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)

        # 加载成果数据
        self.load_project_results()

        # 更新持续时间
        self.on_date_changed()
        
    def load_project_results(self):
        """加载项目成果数据"""
        if not self.project_id:
            return
            
        # 清空成果表格
        self.result_table.setRowCount(0)
        
        # 获取项目成果
        project_results = self.project_result_logic.get_project_results_by_project_id(self.project_id)
        
        # 填充成果表格
        for result in project_results:
            # 确保日期格式正确
            date_str = result.date
            if hasattr(result.date, 'strftime'):
                date_str = result.date.strftime('%Y-%m-%d')
                
            result_data = {
                'type': result.type,
                'name': result.name,
                'date': date_str,
                'id': result.id, # 存储成果ID
                'attachments': self.attachment_logic.get_attachments_by_result(result.id) # 加载附件
            }
            if not hasattr(self, 'results_data'):
                self.results_data = []
            self.results_data.append(result_data)
            self.add_result_to_table(result_data)

    def on_project_name_changed(self):
        # 项目名称实时校验
        project_name = self.project_name_edit.text()
        if Validator.is_valid_project_name(project_name):
            if self.project_logic.is_project_name_exists(project_name) and (
                    not self.project_id or project_name != self.original_project_name):
                self.status_label.setText('项目名称已存在，请更换')
                self.status_label.setStyleSheet('color: red')
            else:
                self.status_label.setText('项目名称可用')
                self.status_label.setStyleSheet('color: green')
        else:
            self.status_label.setText('项目名称不能为空且不能超过255个字符')
            self.status_label.setStyleSheet('color: red')

    def on_date_changed(self):
        # 计算项目持续时间
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        if Validator.is_valid_date_range(start_date.toPyDate(), end_date.toPyDate()):
            # 计算年数差
            years = end_date.year() - start_date.year()
            months = end_date.month() - start_date.month()
            days = end_date.day() - start_date.day()

            if months < 0 or (months == 0 and days < 0):
                years -= 1
                months += 12

            if years < 0:
                years = 0

            self.duration_label.setText(f'{years} 年 {months} 个月')
            self.status_label.setText('日期范围有效')
            self.status_label.setStyleSheet('color: green')
        else:
            self.status_label.setText('结束日期不能早于起始日期')
            self.status_label.setStyleSheet('color: red')

    def on_funding_unit_changed(self):
        # 已移除，资助单位现在是文本输入框
        pass

    def add_result(self):
        # 打开成果添加弹窗
        dialog = ResultDialog(self.widget)
        if dialog.exec_() == QDialog.Accepted:
            result_data = dialog.get_result_data()
            # 确保 result_data 包含 attachments_to_add 和 attachments_to_delete 字段
            if 'attachments_to_add' not in result_data:
                result_data['attachments_to_add'] = []
            if 'attachments_to_delete' not in result_data:
                result_data['attachments_to_delete'] = []

            self.add_result_to_table(result_data)
            if not hasattr(self, 'results_data'):
                self.results_data = []
            self.results_data.append(result_data)

    def edit_result(self):
        # 编辑选中的成果
        selected_rows = self.result_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.widget, '操作提示', '请先选择要编辑的成果')
            return

        row = selected_rows[0].row()
        result_id = self.result_table.item(row, 0).data(Qt.UserRole)
        
        # 从 self.results_data 中找到对应的 result_data
        result_data = next((r for r in getattr(self, 'results_data', []) if r.get('id') == result_id), None)

        if result_data:
            dialog = ResultDialog(self.widget, result_data=result_data, project_result_id=result_id)
            if dialog.exec_() == QDialog.Accepted:
                updated_result_data = dialog.get_result_data()
                # 更新 self.results_data 中的对应项
                for i, r in enumerate(getattr(self, 'results_data', [])):
                    if r.get('id') == result_id:
                        # 合并 attachments_to_add
                        existing_attachments_to_add = set(self.results_data[i].get('attachments_to_add', []))
                        new_attachments_to_add = set(updated_result_data.get('attachments_to_add', []))
                        self.results_data[i]['attachments_to_add'] = list(existing_attachments_to_add.union(new_attachments_to_add))

                        # 合并 attachments_to_delete
                        existing_attachments_to_delete = set(self.results_data[i].get('attachments_to_delete', []))
                        new_attachments_to_delete = set(updated_result_data.get('attachments_to_delete', []))
                        self.results_data[i]['attachments_to_delete'] = list(existing_attachments_to_delete.union(new_attachments_to_delete))

                        # 更新其他字段
                        self.results_data[i]['type'] = updated_result_data['type']
                        self.results_data[i]['name'] = updated_result_data['name']
                        self.results_data[i]['date'] = updated_result_data['date']
                        break
                # Update table items directly
                self.result_table.setItem(row, 0, QTableWidgetItem(updated_result_data['type']))
                self.result_table.setItem(row, 1, QTableWidgetItem(updated_result_data['name']))
                self.result_table.setItem(row, 2, QTableWidgetItem(updated_result_data['date']))
        else:
            QMessageBox.warning(self.widget, '错误', '未找到对应的成果数据')

    def delete_selected_result(self):
        # 删除选中的成果
        selected_rows = self.result_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.widget, '操作提示', '请先选择要删除的成果')
            return

        reply = QMessageBox.question(self.widget, '确认删除', '确定要删除选中的成果吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 从下往上删除，避免索引变化问题
            # 从下往上删除，避免索引变化问题
            for index in sorted(selected_rows, reverse=True):
                row = index.row()
                # 获取成果ID
                result_id = self.result_table.item(row, 0).data(Qt.UserRole)
                if result_id:
                    if not hasattr(self, 'results_to_delete_ids'):
                        self.results_to_delete_ids = []
                    self.results_to_delete_ids.append(result_id)

                # 从 self.results_data 中移除对应的成果数据
                if hasattr(self, 'results_data'):
                    self.results_data = [r for r in self.results_data if r.get('id') != result_id]

                self.result_table.removeRow(row)

    def add_result_to_table(self, result_data):
        """将成果数据添加到表格"""
        row_count = self.result_table.rowCount()
        self.result_table.insertRow(row_count)

        # 成果类型
        type_item = QTableWidgetItem(result_data['type'])
        if result_data.get('id'):
            type_item.setData(Qt.UserRole, result_data['id'])
        self.result_table.setItem(row_count, 0, type_item)

        # 成果名称
        self.result_table.setItem(row_count, 1, QTableWidgetItem(result_data['name']))

        # 发表/获得时间
        self.result_table.setItem(row_count, 2, QTableWidgetItem(result_data['date']))

    def collect_result_data(self):
        # 收集成果数据
        # self.results_data 在每次添加或编辑成果后被更新
        return getattr(self, 'results_data', [])

    def validate_form(self):
        # 验证表单数据
        project_name = self.project_name_edit.text()
        leader = self.leader_edit.text()
        phone = self.phone_edit.text()
        # 已移除邮箱字段
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        funding_unit = self.funding_unit_edit.text()
        level = self.level_combo.currentText()
        funding_amount = self.funding_amount_edit.value()

        # 验证项目名称
        if not Validator.is_valid_project_name(project_name):
            QMessageBox.warning(self.widget, '输入错误', '项目名称不能为空且不能超过255个字符')
            return False
        
        # 验证科室
        department = self.department_edit.text()
        if not Validator.is_valid_department(department):
            QMessageBox.warning(self.widget, '输入错误', '科室不能为空且不能超过50个字符')
            return False
        
        # 验证项目来源
        project_source = self.source_combo.currentText()
        if project_source == '请选择项目来源':
            QMessageBox.warning(self.widget, '输入错误', '请选择项目来源')
            return False
        
        # 验证立项年度
        approval_year = self.approval_year_edit.text()
        if not Validator.is_valid_approval_year(approval_year):
            QMessageBox.warning(self.widget, '输入错误', '请输入有效的立项年度(格式:YYYY)')
            return False
        
        # 验证项目编号
        project_number = self.project_code_edit.text()
        if not Validator.is_valid_project_number(project_number):
            QMessageBox.warning(self.widget, '输入错误', '项目编号不能为空且不能超过50个字符')
            return False

        # 验证项目名称唯一性
        if self.project_logic.is_project_name_exists(project_name) and (
                not self.project_id or project_name != self.original_project_name):
            QMessageBox.warning(self.widget, '输入错误', '项目名称已存在，请更换')
            return False

        # 验证负责人
        if not Validator.is_valid_leader(leader):
            QMessageBox.warning(self.widget, '输入错误', '负责人姓名不能为空且不能超过50个字符')
            return False

        # 验证电话
        if not Validator.is_valid_phone(phone):
            QMessageBox.warning(self.widget, '输入错误', '请输入有效的联系电话')
            return False

        # 已移除邮箱字段验证

        # 验证日期范围
        if not Validator.is_valid_date_range(start_date.toPyDate(), end_date.toPyDate()):
            QMessageBox.warning(self.widget, '输入错误', '结束日期不能早于起始日期')
            return False

        # 验证资助单位
        if not Validator.is_valid_funding_unit(funding_unit):
            QMessageBox.warning(self.widget, '输入错误', '资助单位不能为空且不能超过100个字符')
            return False

        # 验证资助经费
        if not Validator.is_valid_funding_amount(funding_amount):
            QMessageBox.warning(self.widget, '输入错误', '资助经费必须大于0')
            return False

        return True

    def collect_form_data(self):
        # 收集表单数据，与Pydantic模型兼容
        data = {
            'project_name': self.project_name_edit.text(),
            'leader': self.leader_edit.text(),
            'department': self.department_edit.text(),
            'phone': self.phone_edit.text(),
            'project_source': self.source_combo.currentText(),
            'project_type': self.type_combo.currentText(),
            'level': self.level_combo.currentText(),
            'funding_amount': self.funding_amount_edit.value(),
            'funding_unit': self.funding_unit_edit.text(),
            'approval_year': self.approval_year_edit.text(),
            'project_number': self.project_code_edit.text(),
            'start_date': self.start_date_edit.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date_edit.date().toString('yyyy-MM-dd'),
            'status': self.status_combo.currentText()
            # 'result': self.collect_result_data()
        }

        # 如果是编辑模式，添加项目ID
        if self.project_id:
            data['id'] = self.project_id

        return data

    def save_project(self):
        # 保存项目信息
        if self.validate_form():
            project_data = self.collect_form_data()
            success = False
            project_id = None

            if self.project_id:
                # 更新项目
                from models.project import ProjectUpdate
                project_update = ProjectUpdate(**project_data)
                success = self.project_logic.update_project(self.project_id, project_update)
                project_id = self.project_id
            else:
                # 新建项目
                from models.project import ProjectCreate
                project_create = ProjectCreate(**project_data)
                project_id = self.project_logic.create_project(project_create)
                success = project_id > 0

            # 如果项目保存成功，保存项目成果
            if success and project_id:
                # 收集当前UI上的成果数据
                current_results_on_ui = self.collect_result_data()

                # 用于存储已保存的成果，以便后续处理附件
                processed_results = []

                # 遍历当前UI上的成果数据，区分新增和更新
                for result_data in current_results_on_ui:
                    result_id = result_data.get('id')
                    attachments_to_add = result_data.get('attachments_to_add', [])
                    attachments_to_delete = result_data.get('attachments_to_delete', [])

                    if result_id:
                        # 更新现有成果
                        from models.project_result import ProjectResultUpdate
                        update_data = ProjectResultUpdate(
                            type=result_data['type'],
                            name=result_data['name'],
                            date=result_data['date']
                        )
                        self.project_result_logic.update_project_result(result_id, update_data)
                        processed_results.append({'id': result_id, **result_data})
                    else:
                        # 创建新成果
                        from models.project_result import ProjectResultCreate
                        create_data = ProjectResultCreate(
                            project_id=project_id,
                            type=result_data['type'],
                            name=result_data['name'],
                            date=result_data['date']
                        )
                        new_result_id = self.project_result_logic.create_project_result(create_data)
                        if new_result_id > 0:
                            result_data['id'] = new_result_id # 更新ID以便后续附件处理
                            processed_results.append({'id': new_result_id, **result_data})
                        else:
                            QMessageBox.warning(self.widget, '保存失败', f'创建成果 {result_data["name"]} 失败')
                            continue

                    # 处理当前成果的附件
                    # 删除附件
                    for att_id in attachments_to_delete:
                        self.attachment_logic.delete_attachment(att_id)
                    # 添加附件
                    for file_path in attachments_to_add:
                        self.attachment_logic.create_attachment(result_data['id'], file_path)

                    # 清空已处理的附件列表，防止重复处理或影响其他成果
                    # 并且更新 self.results_data 中对应成果的附件列表
                    for i, r in enumerate(self.results_data):
                        if r.get('id') == result_data['id']:
                            # 重新加载附件列表，确保是最新的
                            self.results_data[i]['attachments'] = self.attachment_logic.get_attachments_by_result(result_data['id'])
                            self.results_data[i]['attachments_to_add'] = []
                            self.results_data[i]['attachments_to_delete'] = []
                            break

                ## 处理删除的成果及其附件
                if hasattr(self, 'results_to_delete_ids') and self.results_to_delete_ids:
                    for result_id_to_delete in self.results_to_delete_ids:
                        # 删除成果的所有附件
                        self.attachment_logic.delete_result_attachments(result_id_to_delete)
                        # 删除成果本身
                        self.project_result_logic.delete_project_result(result_id_to_delete)
                    self.results_to_delete_ids = [] # 清空列表



                QMessageBox.information(self.widget, '保存成功', '项目信息已成功保存')
                if hasattr(self, 'on_save_success') and callable(self.on_save_success):
                    self.on_save_success()
                # 如果是对话框模式，保存成功后关闭
                if hasattr(self, 'accept') and callable(self.accept):
                    self.accept()
            else:
                QMessageBox.warning(self.widget, '保存失败', '项目信息保存失败，请重试')

    def reset_form(self):
        # 重置表单
        self.project_name_edit.clear()
        self.leader_edit.clear()
        self.phone_edit.clear()
        # 已移除邮箱字段
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate().addYears(1))
        self.funding_unit_edit.clear()
        self.level_combo.setCurrentIndex(0)
        self.funding_amount_edit.setValue(0)
        # 已移除货币单位字段
        self.status_combo.setCurrentIndex(0)
        self.result_table.setRowCount(0)
        self.status_label.setText('请填写项目信息')
        self.status_label.setStyleSheet('color: black')

        # 如果是编辑模式，重新加载数据
        if self.project_id:
            self.load_project_data(self.project_id)

    def sub_cancel(self):
        """取消操作，由子类实现具体行为"""
        print("执行取消（父）")
        pass

    def on_cancel(self):
        self.sub_cancel()


class ProjectEditor(QWidget):
    """项目编辑组件，继承自QWidget，用于项目登记入口"""

    def __init__(self, project_id=None):
        super().__init__()
        self.base_editor = BaseProjectEditor(project_id)

        # 设置窗口属性
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowTitle('项目新增')
        self.get_result_flag = 0

        try:
            self.base_editor.init_ui(self)

            # 如果提供了项目ID，加载项目数据
            if project_id:
                self.base_editor.load_project_data(project_id)

            self.base_editor.sub_cancel = self.hide
            print('ProjectEditor初始化完成')
        except Exception as e:
            print(f'ProjectEditor初始化出错: {str(e)}')
            QMessageBox.critical(self, '错误', f'编辑器初始化出错: {str(e)}')

    def show(self):
        """显示窗口"""
        super().show()


class ProjectEditorDialog(QDialog):
    """项目编辑对话框，继承自QDialog，用于项目双击操作入口"""

    def __init__(self, project_id=None, parent=None):
        super().__init__(parent)
        self.base_editor = BaseProjectEditor(project_id)

        # 设置窗口属性
        self.setWindowTitle('项目编辑')
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.get_result_flag = 1

        try:
            self.base_editor.init_ui(self)
            self.base_editor.load_funding_units()

            # 如果提供了项目ID，加载项目数据
            if project_id:
                self.base_editor.load_project_data(project_id)

            self.base_editor.sub_cancel = self.reject
            print('ProjectEditorDialog初始化完成')
        except Exception as e:
            print(f'ProjectEditorDialog初始化出错: {str(e)}')
            QMessageBox.critical(self, '错误', f'编辑器初始化出错: {str(e)}')

    def accept(self):
        """重写accept方法，在保存成功后关闭对话框"""
        super().accept()

    def reject(self):
        """重写reject方法，取消操作"""
        print("执行取消")
        super().reject()

    def exec_(self):
        """执行对话框"""
        return super().exec_()
