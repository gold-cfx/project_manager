#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 登录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from logic.user_logic import UserLogic
from models.user import User


class LoginDialog(QDialog):
    """登录对话框"""
    
    login_success = pyqtSignal(User)  # 登录成功信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_logic = UserLogic()
        self.current_user = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('科研项目管理系统 - 登录')
        self.setFixedSize(500, 320)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title_label = QLabel('科研项目管理系统')
        title_label.setFont(QFont('Microsoft YaHei', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        #
        # subtitle_label = QLabel('登录')
        # subtitle_label.setFont(QFont('Microsoft YaHei', 14))
        # subtitle_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(subtitle_label)
        
        # 用户名
        username_layout = QVBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFont(QFont('Microsoft YaHei', 10))
        self.username_edit = QLineEdit()
        self.username_edit.setFont(QFont('Microsoft YaHei', 10))
        self.username_edit.setPlaceholderText('请输入用户名')
        self.username_edit.setMinimumHeight(35)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 密码
        password_layout = QVBoxLayout()
        password_label = QLabel('密码:')
        password_label.setFont(QFont('Microsoft YaHei', 10))
        self.password_edit = QLineEdit()
        self.password_edit.setFont(QFont('Microsoft YaHei', 10))
        self.password_edit.setPlaceholderText('请输入密码')
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(35)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        #
        # # 记住密码
        # self.remember_checkbox = QCheckBox('记住密码')
        # self.remember_checkbox.setFont(QFont('Microsoft YaHei', 10))
        # layout.addWidget(self.remember_checkbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        self.login_button = QPushButton('登录')
        self.login_button.setFont(QFont('Microsoft YaHei', 11))
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        
        self.exit_button = QPushButton('退出')
        self.exit_button.setFont(QFont('Microsoft YaHei', 11))
        self.exit_button.setMinimumHeight(40)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
            QPushButton:pressed {
                background-color: #cf1322;
            }
        """)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 信号连接
        self.login_button.clicked.connect(self.on_login)
        self.exit_button.clicked.connect(self.reject)
        
        # 回车键登录
        self.username_edit.returnPressed.connect(self.on_login)
        self.password_edit.returnPressed.connect(self.on_login)
        
    def on_login(self):
        """处理登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, '输入错误', '请输入用户名！')
            self.username_edit.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, '输入错误', '请输入密码！')
            self.password_edit.setFocus()
            return
            
        try:
            # 先检查用户是否存在
            user = self.user_logic.get_user_by_username(username)
            if not user:
                QMessageBox.warning(self, '登录失败', '用户名或密码错误！')
                self.password_edit.clear()
                self.password_edit.setFocus()
                return
                
            # 检查用户状态
            if user.status != 'active':
                QMessageBox.warning(self, '登录失败', '当前用户不可用，请联系管理员处理！')
                self.password_edit.clear()
                self.password_edit.setFocus()
                return
                
            # 检查密码
            authenticated_user = self.user_logic.authenticate_user(username, password)
            if authenticated_user:
                self.current_user = authenticated_user
                # 设置用户会话
                from utils.session import SessionManager
                SessionManager.set_current_user(authenticated_user)
                self.login_success.emit(authenticated_user)
                self.accept()
            else:
                QMessageBox.warning(self, '登录失败', '用户名或密码错误！')
                self.password_edit.clear()
                self.password_edit.setFocus()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'登录失败：{str(e)}')
            
    def get_current_user(self) -> User:
        """获取当前登录用户"""
        return self.current_user