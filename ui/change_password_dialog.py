#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修改密码对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFormLayout)

from data.user_dao import UserDAO


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.user_dao = UserDAO()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('🔐 修改密码')
        self.setFixedSize(450, 300)

        # 设置对话框边框和居中显示
        self.setStyleSheet('''
            QLineEdit {
                padding: 12px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                font-family: "Microsoft YaHei";
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: #f8f9ff;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #666;
            }
        ''')

        # 设置对话框居中显示
        self.center_on_screen()

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 当前用户显示
        user_label = QLabel(f'当前用户: {self.current_user.real_name} ({self.current_user.username})')
        user_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        main_layout.addWidget(user_label)
        main_layout.addSpacing(10)

        # 原密码
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        self.old_password_input.setPlaceholderText('请输入当前密码')
        form_layout.addRow('当前密码:', self.old_password_input)

        # 新密码
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText('请输入新密码（至少6位）')
        form_layout.addRow('新密码:', self.new_password_input)

        # 确认密码
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText('请再次输入新密码')
        form_layout.addRow('确认密码:', self.confirm_password_input)

        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        # 密码规则提示
        hint_label = QLabel('密码要求：长度至少6位，建议包含字母、数字和特殊字符')
        hint_label.setStyleSheet('color: #666; font-size: 12px;')
        hint_label.setWordWrap(True)
        main_layout.addWidget(hint_label)

        main_layout.addStretch()

        # 按钮布局
        button_layout = QHBoxLayout()

        self.save_button = QPushButton('确认修改')
        self.save_button.clicked.connect(self.change_password)

        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def center_on_screen(self):
        """将窗口居中显示"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def change_password(self):
        """修改密码"""
        old_password = self.old_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # 验证输入
        if not old_password:
            QMessageBox.warning(self, '警告', '请输入当前密码')
            self.old_password_input.setFocus()
            return

        if not new_password:
            QMessageBox.warning(self, '警告', '请输入新密码')
            self.new_password_input.setFocus()
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, '警告', '新密码长度至少为6位')
            self.new_password_input.setFocus()
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, '警告', '两次输入的新密码不一致')
            self.confirm_password_input.setFocus()
            return

        if old_password == new_password:
            QMessageBox.warning(self, '警告', '新密码不能与当前密码相同')
            self.new_password_input.setFocus()
            return

        try:
            # 验证原密码是否正确
            if not self.user_dao.verify_password(self.current_user.username, old_password):
                QMessageBox.warning(self, '警告', '当前密码输入错误')
                self.old_password_input.setFocus()
                return

            # 修改密码
            if self.user_dao.change_password(self.current_user.username, new_password):
                QMessageBox.information(self, '成功', '密码修改成功！')
                self.accept()
            else:
                QMessageBox.warning(self, '失败', '密码修改失败，请稍后重试')

        except Exception as e:
            QMessageBox.warning(self, '错误', f'密码修改失败：{str(e)}')
