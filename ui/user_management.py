#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 用户管理界面
"""
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QMessageBox, QComboBox, QDialog, QFormLayout,
                             QDialogButtonBox, QHeaderView)

from logic.user_logic import UserLogic
from models.user import UserCreate, UserUpdate, UserRole, UserStatus


class UserDialog(QDialog):
    """用户编辑对话框"""

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.user_logic = UserLogic()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('添加用户' if not self.user else '编辑用户')
        self.setFixedSize(500, 500)

        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # 用户名
        self.username_edit = QLineEdit()
        self.username_edit.setFont(QFont('Microsoft YaHei', 10))
        if self.user:
            self.username_edit.setText(self.user.username)
            self.username_edit.setEnabled(False)
        layout.addRow('用户名:', self.username_edit)

        # 真实姓名
        self.real_name_edit = QLineEdit()
        self.real_name_edit.setFont(QFont('Microsoft YaHei', 10))
        if self.user:
            self.real_name_edit.setText(self.user.real_name)
        layout.addRow('真实姓名:', self.real_name_edit)

        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setFont(QFont('Microsoft YaHei', 10))
        self.password_edit.setEchoMode(QLineEdit.Password)
        if not self.user:
            self.password_edit.setPlaceholderText('请输入密码（至少6位）')
        else:
            self.password_edit.setPlaceholderText('不修改请留空')
        layout.addRow('密码:' if not self.user else '新密码:', self.password_edit)

        # 确认密码
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setFont(QFont('Microsoft YaHei', 10))
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText('请再次输入密码')
        layout.addRow('确认密码:', self.confirm_password_edit)

        # 角色
        self.role_combo = QComboBox()
        self.role_combo.setFont(QFont('Microsoft YaHei', 10))
        self.role_combo.addItems(['用户', '管理员'])
        self.role_combo.setCurrentText('管理员' if not self.user else
                                       ('管理员' if self.user.role == UserRole.ADMIN else '用户'))
        layout.addRow('角色:', self.role_combo)

        # 状态
        self.status_combo = QComboBox()
        self.status_combo.setFont(QFont('Microsoft YaHei', 10))
        self.status_combo.addItems(['激活', '禁用'])
        self.status_combo.setCurrentText('激活' if not self.user else
                                         ('激活' if self.user.status == UserStatus.ACTIVE else '禁用'))
        layout.addRow('状态:', self.status_combo)

        # 邮箱
        self.email_edit = QLineEdit()
        self.email_edit.setFont(QFont('Microsoft YaHei', 10))
        if self.user and self.user.email:
            self.email_edit.setText(self.user.email)
        layout.addRow('邮箱:', self.email_edit)

        # 电话
        self.phone_edit = QLineEdit()
        self.phone_edit.setFont(QFont('Microsoft YaHei', 10))
        if self.user and self.user.phone:
            self.phone_edit.setText(self.user.phone)
        layout.addRow('电话:', self.phone_edit)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_user_data(self):
        """获取用户数据"""
        return {
            'username': self.username_edit.text().strip(),
            'real_name': self.real_name_edit.text().strip(),
            'password': self.password_edit.text().strip(),
            'confirm_password': self.confirm_password_edit.text().strip(),
            'role': UserRole.ADMIN if self.role_combo.currentText() == '管理员' else UserRole.USER,
            'status': UserStatus.ACTIVE if self.status_combo.currentText() == '激活' else UserStatus.INACTIVE,
            'email': self.email_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None
        }


class UserManagementWidget(QWidget):
    """用户管理界面"""

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.user_logic = UserLogic()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel('用户管理')
        title_label.setFont(QFont('Microsoft YaHei', 16, QFont.Bold))
        layout.addWidget(title_label)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setFont(QFont('Microsoft YaHei', 10))
        self.search_edit.setPlaceholderText('搜索用户名或真实姓名...')
        self.search_edit.setMinimumWidth(200)
        self.search_edit.textChanged.connect(self.on_search)
        toolbar_layout.addWidget(self.search_edit)

        toolbar_layout.addStretch()

        # 添加用户按钮
        self.add_button = QPushButton('添加用户')
        self.add_button.setFont(QFont('Microsoft YaHei', 10))
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        self.add_button.clicked.connect(self.on_add_user)
        toolbar_layout.addWidget(self.add_button)

        layout.addLayout(toolbar_layout)

        # 用户表格
        self.table = QTableWidget()
        self.table.setFont(QFont('Microsoft YaHei', 10))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', '用户名', '真实姓名', '角色', '状态', '邮箱', '电话'
        ])

        # 设置表格样式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(1, 100)  # 用户名
        self.table.setColumnWidth(2, 100)  # 真实姓名
        self.table.setColumnWidth(3, 80)  # 角色
        self.table.setColumnWidth(4, 80)  # 状态
        self.table.setColumnWidth(5, 150)  # 邮箱

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # 操作按钮
        button_layout = QHBoxLayout()

        self.edit_button = QPushButton('编辑')
        self.edit_button.setFont(QFont('Microsoft YaHei', 10))
        self.edit_button.clicked.connect(self.on_edit_user)

        self.delete_button = QPushButton('删除')
        self.delete_button.setFont(QFont('Microsoft YaHei', 10))
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
        """)
        self.delete_button.clicked.connect(self.on_delete_user)

        self.reset_password_button = QPushButton('重置密码')
        self.reset_password_button.setFont(QFont('Microsoft YaHei', 10))
        self.reset_password_button.clicked.connect(self.on_reset_password)

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.reset_password_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_users(self):
        """加载用户列表"""
        try:
            users = self.user_logic.get_all_users()
            self.display_users(users)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载用户列表失败：{str(e)}')

    def display_users(self, users):
        """显示用户列表"""
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.real_name))
            self.table.setItem(row, 3, QTableWidgetItem(
                '管理员' if user.role == UserRole.ADMIN else '用户'))
            self.table.setItem(row, 4, QTableWidgetItem(
                '激活' if user.status == UserStatus.ACTIVE else '禁用'))
            self.table.setItem(row, 5, QTableWidgetItem(user.email or ''))
            self.table.setItem(row, 6, QTableWidgetItem(user.phone or ''))

    def on_search(self):
        """搜索用户"""
        search_text = self.search_edit.text().strip().lower()
        if not search_text:
            self.load_users()
            return

        try:
            users = self.user_logic.get_all_users()
            filtered_users = [
                user for user in users
                if search_text in user.username.lower() or
                   search_text in user.real_name.lower()
            ]
            self.display_users(filtered_users)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'搜索失败：{str(e)}')

    def on_add_user(self):
        """添加用户"""
        dialog = UserDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_user_data()

            # 验证数据
            if not data['username']:
                QMessageBox.warning(self, '输入错误', '用户名不能为空！')
                return
            if not data['real_name']:
                QMessageBox.warning(self, '输入错误', '真实姓名不能为空！')
                return
            if not data['password']:
                QMessageBox.warning(self, '输入错误', '密码不能为空！')
                return
            if len(data['password']) < 6:
                QMessageBox.warning(self, '输入错误', '密码长度不能少于6位！')
                return
            if data['password'] != data['confirm_password']:
                QMessageBox.warning(self, '输入错误', '两次输入的密码不一致！')
                return

            try:
                user_create = UserCreate(
                    username=data['username'],
                    real_name=data['real_name'],
                    password=data['password'],
                    role=data['role'],
                    status=data['status'],
                    email=data['email'],
                    phone=data['phone']
                )

                if self.user_logic.create_user(user_create):
                    QMessageBox.information(self, '成功', '用户创建成功！')
                    self.load_users()
                else:
                    QMessageBox.warning(self, '失败', '用户创建失败！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'创建用户失败：{str(e)}')

    def on_edit_user(self):
        """编辑用户"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要编辑的用户！')
            return

        user_id = int(self.table.item(current_row, 0).text())
        user = self.user_logic.get_user_by_id(user_id)
        if not user:
            QMessageBox.warning(self, '错误', '用户不存在！')
            return

        # 不能编辑自己
        if user.id == self.current_user.id:
            QMessageBox.warning(self, '提示', '不能编辑当前登录用户！')
            return

        dialog = UserDialog(user=user, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_user_data()

            # 验证数据
            if not data['real_name']:
                QMessageBox.warning(self, '输入错误', '真实姓名不能为空！')
                return
            if data['password'] and len(data['password']) < 6:
                QMessageBox.warning(self, '输入错误', '密码长度不能少于6位！')
                return
            if data['password'] != data['confirm_password']:
                QMessageBox.warning(self, '输入错误', '两次输入的密码不一致！')
                return

            try:
                user_update = UserUpdate(
                    real_name=data['real_name'],
                    role=data['role'],
                    status=data['status'],
                    email=data['email'],
                    phone=data['phone']
                )

                if data['password']:
                    user_update.password = data['password']

                if self.user_logic.update_user(user_id, user_update):
                    QMessageBox.information(self, '成功', '用户信息更新成功！')
                    self.load_users()
                else:
                    QMessageBox.warning(self, '失败', '用户信息更新失败！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'更新用户失败：{str(e)}')

    def on_delete_user(self):
        """删除用户"""
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            QMessageBox.warning(self, '权限不足', '只有管理员才能删除用户')
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要删除的用户！')
            return

        user_id = int(self.table.item(current_row, 0).text())
        username = self.table.item(current_row, 1).text()

        # 不能删除自己
        if user_id == self.current_user.id:
            QMessageBox.warning(self, '提示', '不能删除当前登录用户！')
            return

        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除用户 "{username}" 吗？\n此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.user_logic.delete_user(user_id):
                    QMessageBox.information(self, '成功', '用户删除成功！')
                    self.load_users()
                else:
                    QMessageBox.warning(self, '失败', '用户删除失败！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除用户失败：{str(e)}')

    def on_reset_password(self):
        """重置密码"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要重置密码的用户！')
            return

        user_id = int(self.table.item(current_row, 0).text())
        username = self.table.item(current_row, 1).text()

        new_password = '12345678'
        reply = QMessageBox.question(
            self, '确认重置密码',
            f'确定要将用户 "{username}" 的密码重置为 "{new_password}" 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.user_logic.reset_password(user_id, new_password):
                    QMessageBox.information(self, '成功',
                                            f'密码重置成功！\n新密码：{new_password}')
                else:
                    QMessageBox.warning(self, '失败', '密码重置失败！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'重置密码失败：{str(e)}')
