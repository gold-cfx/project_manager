import json
import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QGroupBox, QHBoxLayout, QTabWidget,
    QRadioButton, QLabel
)

from config import settings
from config.settings import pod_ip


class SystemSettings(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 系统配置标签页
        self.system_config_widget = QWidget()
        self.init_system_config_tab()
        self.tab_widget.addTab(self.system_config_widget, "系统配置")
        
        # 用户管理标签页（仅管理员可见）
        if self.current_user and self.current_user.role == "admin":
            from .user_management import UserManagementWidget
            self.user_management_widget = UserManagementWidget(self.current_user)
            self.tab_widget.addTab(self.user_management_widget, "用户管理")
        
        main_layout.addWidget(self.tab_widget)

    def init_system_config_tab(self):
        # 创建系统配置标签页的布局
        config_layout = QVBoxLayout(self.system_config_widget)

        # 数据库配置
        db_group = QGroupBox('数据库配置')
        db_layout = QFormLayout()

        self.db_config_host = QLineEdit()
        self.db_config_host.setPlaceholderText('请输入数据库连接主机ip地址')
        db_layout.addRow('数据库主机', self.db_config_host)
        self.db_config_db_name = QLineEdit()
        self.db_config_db_name.setPlaceholderText('请输入数据库连接库名')
        db_layout.addRow('数据库连接库名', self.db_config_db_name)
        self.db_config_user = QLineEdit()
        self.db_config_user.setPlaceholderText('请输入数据库连接用户名')
        db_layout.addRow('数据库连接用户名', self.db_config_user)
        self.db_config_password = QLineEdit()
        self.db_config_password.setPlaceholderText('请输入数据库连接密码')
        self.db_config_password.setEchoMode(QLineEdit.Password)
        db_layout.addRow('数据库连接密码', self.db_config_password)

        db_group.setLayout(db_layout)
        config_layout.addWidget(db_group)

        # 文件服务器配置
        file_server_group = QGroupBox('文件服务器配置')
        file_server_layout = QFormLayout()

        # 服务器模式选择
        mode_layout = QHBoxLayout()
        self.local_server_radio = QRadioButton('本地服务器')
        self.remote_server_radio = QRadioButton('远程服务器')
        mode_layout.addWidget(self.local_server_radio)
        mode_layout.addWidget(self.remote_server_radio)
        file_server_layout.addRow('服务器模式', mode_layout)

        # 本地服务器配置
        self.local_host_edit = QLineEdit()
        self.local_host_edit.setPlaceholderText(f'默认: {pod_ip}')
        self.local_port_edit = QLineEdit()
        self.local_port_edit.setPlaceholderText('默认: 5001')
        file_server_layout.addRow('本地主机地址', self.local_host_edit)
        file_server_layout.addRow('本地端口', self.local_port_edit)

        # 远程服务器配置
        self.remote_host_edit = QLineEdit()
        self.remote_host_edit.setPlaceholderText('远程服务器IP地址')
        self.remote_port_edit = QLineEdit()
        self.remote_port_edit.setPlaceholderText('默认: 5001')
        file_server_layout.addRow('远程主机地址', self.remote_host_edit)
        file_server_layout.addRow('远程端口', self.remote_port_edit)

        # 文件存储目录
        self.file_server_dir_edit = QLineEdit()
        self.file_server_dir_edit.setPlaceholderText('请选择文件存储目录')
        self.file_server_dir_edit.setReadOnly(True)
        self.select_file_server_dir_button = QPushButton('选择目录')
        self.select_file_server_dir_button.clicked.connect(self.select_file_server_directory)
        file_server_layout.addRow('文件存储目录', self.file_server_dir_edit)
        file_server_layout.addRow('', self.select_file_server_dir_button)

        # 添加提示信息
        hint_label = QLabel('注意：修改文件服务器配置后需要重启应用程序才能生效')
        hint_label.setStyleSheet('color: #888; font-size: 10px;')
        file_server_layout.addRow('', hint_label)

        file_server_group.setLayout(file_server_layout)
        config_layout.addWidget(file_server_group)

        # 保存按钮
        self.save_button = QPushButton('保存配置')
        self.save_button.clicked.connect(self.save_config)
        config_layout.addWidget(self.save_button, alignment=QtCore.Qt.AlignCenter)

        # 信号连接
        self.local_server_radio.toggled.connect(self.toggle_server_mode)
        self.remote_server_radio.toggled.connect(self.toggle_server_mode)

        # 加载现有配置
        self.load_config()

        # 初始化服务器模式
        self.toggle_server_mode()

    def select_directory(self):
        # 这个方法现在可能不再需要，但为了兼容性保留
        directory = QFileDialog.getExistingDirectory(self, '选择目录', os.getcwd())
        if directory:
            self.file_server_dir_edit.setText(directory)

    def select_file_server_directory(self):
        directory = QFileDialog.getExistingDirectory(self, '选择文件存储目录', os.getcwd())
        if directory:
            self.file_server_dir_edit.setText(directory)

    def toggle_server_mode(self):
        # 根据选择的服务器模式启用/禁用相应的配置项
        is_remote = self.remote_server_radio.isChecked()

        # 本地服务器配置
        self.local_host_edit.setEnabled(False)
        self.local_port_edit.setEnabled(not is_remote)
        self.file_server_dir_edit.setEnabled(not is_remote)
        self.select_file_server_dir_button.setEnabled(not is_remote)

        # 远程服务器配置
        self.remote_host_edit.setEnabled(is_remote)
        self.remote_port_edit.setEnabled(is_remote)

    def load_config(self):
        # 从配置文件加载数据库配置
        db_config = settings.DB_CONFIG
        self.db_config_host.setText(db_config.get('host', '127.0.0.1'))
        self.db_config_db_name.setText(db_config.get('db_name', settings.default_db_name))
        self.db_config_user.setText(db_config.get('user', 'root'))
        self.db_config_password.setText(db_config.get('password', ''))

        # 服务器模式
        remote_server = settings.FILE_SERVER_CONFIG.get('remote_server', False)
        if remote_server:
            self.remote_server_radio.setChecked(True)
        else:
            self.local_server_radio.setChecked(True)

        # 本地服务器配置
        self.local_host_edit.setText(pod_ip)
        self.local_port_edit.setText(str(settings.FILE_SERVER_CONFIG.get('port', 5001)))

        # 远程服务器配置
        self.remote_host_edit.setText(settings.FILE_SERVER_CONFIG.get('remote_host', ''))
        self.remote_port_edit.setText(str(settings.FILE_SERVER_CONFIG.get('remote_port', 5001)))

        # 文件存储目录
        root_dir = settings.FILE_SERVER_CONFIG.get('root_dir', '')
        self.file_server_dir_edit.setText(root_dir)

    def save_config(self):
        settings_config = {}
        # 保存数据库配置
        db_config = {
            'host': self.db_config_host.text(),
            'db_name': self.db_config_db_name.text(),
            'user': self.db_config_user.text(),
            'password': self.db_config_password.text()
        }
        settings_config['database'] = db_config

        # 保存文件服务器配置
        file_server_config = {
            'enabled': True,  # 始终启用
            'remote_server': self.remote_server_radio.isChecked(),
            'host': "0.0.0.0",
            'port': int(self.local_port_edit.text()) if self.local_port_edit.text().isdigit() else 5001,
            'remote_host': self.remote_host_edit.text(),
            'remote_port': int(self.remote_port_edit.text()) if self.remote_port_edit.text().isdigit() else 5001,
            'root_dir': self.file_server_dir_edit.text()
        }
        settings_config["file_server"] = file_server_config

        # 保存到配置文件
        with open(settings.config_path, 'w', encoding='utf-8') as fw:
            json.dump(settings_config, fw, ensure_ascii=False, indent=2)

        # 提示用户配置已保存并需要重启
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, '配置保存成功', '文件服务器配置已保存，请重启应用程序使配置生效！')
