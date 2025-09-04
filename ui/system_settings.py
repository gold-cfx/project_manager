import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QGroupBox, QHBoxLayout, QTabWidget,
    QRadioButton, QLabel, QSpinBox, QMessageBox
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

        # 提醒配置标签页（所有用户可见）
        self.reminder_config_widget = QWidget()
        self.init_reminder_config_tab()
        self.tab_widget.addTab(self.reminder_config_widget, "提醒配置")

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

        self.db_config_port = QLineEdit()
        self.db_config_port.setPlaceholderText('默认端口: 3306')
        db_layout.addRow('数据库端口', self.db_config_port)

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

        # 数据库操作按钮
        db_button_layout = QHBoxLayout()

        self.test_connection_button = QPushButton('测试连接')
        self.test_connection_button.clicked.connect(self.test_database_connection)
        db_button_layout.addWidget(self.test_connection_button)

        self.init_db_button = QPushButton('初始化数据库')
        self.init_db_button.clicked.connect(self.init_database_tables)
        self.init_db_button.setToolTip("首次使用时创建数据库表结构")
        db_button_layout.addWidget(self.init_db_button)

        config_layout.addLayout(db_button_layout)

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

    def init_reminder_config_tab(self):
        """初始化提醒配置标签页"""
        # 创建提醒配置标签页的布局
        reminder_layout = QVBoxLayout(self.reminder_config_widget)

        # 提醒配置说明
        reminder_info = QLabel("设置系统自动检查提醒的时间间隔")
        reminder_info.setStyleSheet('color: #666; font-size: 12px; margin-bottom: 10px;')
        reminder_layout.addWidget(reminder_info)

        # 提醒配置组
        reminder_group = QGroupBox('提醒设置')
        reminder_form_layout = QFormLayout()

        self.reminder_interval_spinbox = QSpinBox()
        self.reminder_interval_spinbox.setRange(1, 24)  # 1-24小时
        self.reminder_interval_spinbox.setSuffix(' 小时')
        self.reminder_interval_spinbox.setValue(1)  # 默认1小时
        self.reminder_interval_spinbox.setToolTip('设置系统自动检查提醒的时间间隔')

        reminder_form_layout.addRow('提醒检查间隔', self.reminder_interval_spinbox)

        reminder_group.setLayout(reminder_form_layout)
        reminder_layout.addWidget(reminder_group)

        # 提醒说明
        reminder_desc = QLabel(
            "说明：\n"
            "• 系统会按照设定的时间间隔自动检查待办提醒\n"
            "• 当发现有需要提醒的项目时，会自动弹出提醒窗口\n"
            "• 修改后立即生效，无需重启应用程序"
        )
        reminder_desc.setStyleSheet('color: #666; font-size: 11px; margin-top: 10px;')
        reminder_desc.setWordWrap(True)
        reminder_layout.addWidget(reminder_desc)

        # 保存按钮
        self.reminder_save_button = QPushButton('保存提醒配置')
        self.reminder_save_button.clicked.connect(self.save_reminder_config)
        reminder_layout.addWidget(self.reminder_save_button, alignment=QtCore.Qt.AlignCenter)

        # 加载提醒配置
        self.load_reminder_config()

    def load_config(self):
        # 从配置文件加载数据库配置
        db_config = settings.DB_CONFIG
        self.db_config_host.setText(db_config.get('host', '127.0.0.1'))
        self.db_config_port.setText(str(db_config.get('port', 3306)))
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

    def test_database_connection(self):
        """测试数据库连接"""
        try:
            from data.db_connection import DatabaseConnection
            import pymysql

            # 获取当前配置
            host = self.db_config_host.text().strip()
            port = int(self.db_config_port.text()) if self.db_config_port.text().strip() else 3306
            db_name = self.db_config_db_name.text().strip()
            user = self.db_config_user.text().strip()
            password = self.db_config_password.text()

            if not all([host, db_name, user]):
                QMessageBox.warning(self, '配置不完整', '请填写完整的数据库连接信息！')
                return

            # 使用临时配置测试连接
            temp_config = {
                'host': host,
                'port': port,
                'db_name': "mysql",
                'user': user,
                'password': password,
                'charset': 'utf8mb4'
            }

            # 创建临时连接实例
            temp_db = DatabaseConnection()
            temp_db.config = temp_config

            # 测试连接
            conn = temp_db.connect()
            if conn and conn.open:
                # 检查数据库是否存在
                cursor = conn.cursor()
                cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
                db_exists = cursor.fetchone() is not None
                cursor.close()
                temp_db.close()

                if db_exists:
                    QMessageBox.information(self, '连接成功',
                                            f'数据库连接成功！\n\n主机: {host}:{port}\n数据库: {db_name}\n状态: 数据库已存在')
                else:
                    reply = QMessageBox.question(self, '数据库不存在',
                                                 f'数据库连接成功，但数据库 "{db_name}" 不存在。\n\n是否初始化数据库？',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                    if reply == QMessageBox.Yes:
                        self.init_database_tables()
            else:
                QMessageBox.critical(self, '连接失败', '数据库连接失败！')

        except pymysql.Error as e:
            QMessageBox.critical(self, '连接失败', f'数据库连接失败！\n\n错误信息: {str(e)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'测试连接时发生错误: {str(e)}')

    def init_database_tables(self):
        """初始化数据库表结构"""
        try:
            import pymysql
            from data.db_connection import init_database

            # 获取当前配置
            host = self.db_config_host.text().strip()
            port = int(self.db_config_port.text()) if self.db_config_port.text().strip() else 3306
            db_name = self.db_config_db_name.text().strip()
            user = self.db_config_user.text().strip()
            password = self.db_config_password.text()

            if not all([host, db_name, user]):
                QMessageBox.warning(self, '配置不完整', '请填写完整的数据库连接信息！')
                return

            # 临时更新配置以使用新设置
            from config.settings import DB_CONFIG
            original_config = DB_CONFIG.copy()

            try:
                # 更新为当前界面配置
                DB_CONFIG.update({
                    'host': host,
                    'port': port,
                    'db_name': db_name,
                    'user': user,
                    'password': password,
                    'charset': 'utf8mb4'
                })

                # 创建数据库（如果不存在）
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    charset='utf8mb4'
                )

                cursor = conn.cursor()
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.close()
                conn.close()

                # 使用现有的初始化方法
                init_success = init_database()

                if init_success:
                    from init_data_dict import initialize_data_dict
                    success = initialize_data_dict()

                    if success:
                        QMessageBox.information(self, '初始化成功',
                                                f'数据库初始化完成！\n\n'
                                                f'数据库: {db_name}\n'
                                                f'表结构创建: 成功！😄\n'
                                                f'数据初始化: 成功！😄')
                    else:
                        QMessageBox.information(self, '初始化完成',
                                                f'数据库初始化完成！\n\n'
                                                f'数据库: {db_name}\n'
                                                f'表结构创建: 成功！😄\n'
                                                f'数据初始化: 失败！😭')

                else:
                    QMessageBox.critical(self, '初始化失败', '数据库初始化失败！')

            finally:
                # 恢复原始配置
                DB_CONFIG.clear()
                DB_CONFIG.update(original_config)

        except pymysql.Error as e:
            QMessageBox.critical(self, '初始化失败', f'数据库初始化失败！\n\n错误信息: {str(e)}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'初始化时发生错误: {str(e)}')

    def load_reminder_config(self):
        """加载提醒配置"""
        try:
            from logic.auto_reminder import auto_reminder
            self.reminder_interval_spinbox.setValue(auto_reminder.reminder_interval_hours)
        except Exception as e:
            print(f"加载提醒配置时发生错误: {e}")

    def save_config(self):
        settings_config = {}
        # 保存数据库配置
        db_config = {
            'host': self.db_config_host.text(),
            'port': int(self.db_config_port.text()) if self.db_config_port.text().isdigit() else 3306,
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

        # 使用新的备份保存函数
        from config.settings import save_config_with_backup
        save_config_with_backup('config.json', settings_config)

        # 提示用户配置已保存
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, '配置保存成功',
                                '文件服务器配置保存成功，已同步备份到C:\\research_project\\config目录，需重启应用程序生效。')

    def save_reminder_config(self):
        """保存提醒配置"""
        try:
            from logic.auto_reminder import auto_reminder
            interval = self.reminder_interval_spinbox.value()

            # 检查是否为隐藏管理员
            from utils.session import SessionManager
            current_user = SessionManager.get_current_user()
            is_hidden_admin = current_user and current_user.username == "cfx"

            if is_hidden_admin:
                # 隐藏管理员只保存配置到文件，不重新加载数据
                auto_reminder.reminder_interval_hours = interval
                auto_reminder.save_timer_config()
                QMessageBox.information(self, '配置保存成功',
                                        '提醒配置已保存到文件（隐藏管理员模式：不重新加载数据）')
            else:
                auto_reminder.reminder_interval_hours = interval
                auto_reminder.save_timer_config()
                # 普通用户正常更新配置并重新加载
                auto_reminder.update_interval(interval)
                QMessageBox.information(self, '配置保存成功', '提醒配置已保存并立即生效')
        except Exception as e:
            QMessageBox.critical(self, '保存失败', f'保存提醒配置时发生错误：{str(e)}')
