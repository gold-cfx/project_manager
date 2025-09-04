import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QGroupBox, QHBoxLayout, QTabWidget,
    QRadioButton, QLabel, QSpinBox, QMessageBox, QComboBox
)

from config import settings
from config.settings import pod_ip
from utils.logger import get_logger

logger = get_logger(__name__)


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

        # 日志配置标签页
        self.log_config_widget = QWidget()
        self.init_log_config_tab()
        self.tab_widget.addTab(self.log_config_widget, "日志配置")

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

    def select_log_directory(self):
        directory = QFileDialog.getExistingDirectory(self, '选择日志保存目录', os.getcwd())
        if directory:
            self.log_dir_edit.setText(directory)

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

    def init_log_config_tab(self):
        """初始化日志配置标签页"""
        # 创建日志配置标签页的布局
        log_layout = QVBoxLayout(self.log_config_widget)

        # 日志配置说明
        log_info = QLabel("配置系统日志的存储位置、级别和清理策略")
        log_info.setStyleSheet('color: #666; font-size: 12px; margin-bottom: 10px;')
        log_layout.addWidget(log_info)

        # 日志配置组
        log_group = QGroupBox('日志设置')
        log_form_layout = QFormLayout()

        # 日志目录选择
        self.log_dir_edit = QLineEdit()
        self.log_dir_edit.setPlaceholderText('请选择日志文件保存目录')
        self.log_dir_edit.setReadOnly(True)
        self.select_log_dir_button = QPushButton('选择目录')
        self.select_log_dir_button.clicked.connect(self.select_log_directory)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.log_dir_edit)
        dir_layout.addWidget(self.select_log_dir_button)
        log_form_layout.addRow('日志目录:', dir_layout)

        # 日志级别选择
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['调试', '信息', '警告', '错误', '严重'])
        self.log_level_combo.setCurrentText('信息')
        self.log_level_combo.setToolTip('选择日志的详细程度：调试(最详细) → 严重(最简洁)')
        
        level_label = QLabel('日志级别:')
        level_label.setToolTip('控制日志的详细程度')
        log_form_layout.addRow(level_label, self.log_level_combo)

        # 日志保留天数
        self.log_days_spinbox = QSpinBox()
        self.log_days_spinbox.setRange(1, 365)
        self.log_days_spinbox.setValue(7)
        self.log_days_spinbox.setSuffix(' 天')
        self.log_days_spinbox.setToolTip('超过此天数的日志文件将被自动清理')
        
        days_label = QLabel('保留天数:')
        days_label.setToolTip('日志文件自动清理的周期')
        log_form_layout.addRow(days_label, self.log_days_spinbox)

        log_group.setLayout(log_form_layout)
        log_layout.addWidget(log_group)

        # 日志信息提示
        log_hint = QLabel(
            '💡 提示：\n'
            '• 修改日志配置后需要重启应用程序才能生效\n'
            '• 建议选择有足够磁盘空间的目录\n'
            '• 生产环境建议使用INFO级别，调试时可使用DEBUG级别'
        )
        log_hint.setStyleSheet('color: #666; font-size: 11px; background-color: #f9f9f9; padding: 10px; border-radius: 5px;')
        log_hint.setWordWrap(True)
        log_layout.addWidget(log_hint)

        # 添加保存按钮
        save_log_button = QPushButton('保存日志配置')
        save_log_button.clicked.connect(self.save_log_config)
        log_layout.addWidget(save_log_button, alignment=QtCore.Qt.AlignCenter)

        # 加载现有日志配置
        self.load_log_config()

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
        """加载现有配置"""
        try:
            # 加载数据库配置
            db_config = settings.DB_CONFIG
            self.db_config_host.setText(str(db_config.get('host', 'localhost')))
            self.db_config_port.setText(str(db_config.get('port', 3306)))
            self.db_config_db_name.setText(str(db_config.get('db_name', 'research_project')))
            self.db_config_user.setText(str(db_config.get('user', 'root')))
            self.db_config_password.setText(str(db_config.get('password', '')))

            # 加载文件服务器配置
            file_server_config = settings.FILE_SERVER_CONFIG
            is_remote = file_server_config.get('remote_server', False)
            self.local_server_radio.setChecked(not is_remote)
            self.remote_server_radio.setChecked(is_remote)
            self.local_port_edit.setText(str(file_server_config.get('port', 5001)))
            self.remote_host_edit.setText(str(file_server_config.get('remote_host', '')))
            self.remote_port_edit.setText(str(file_server_config.get('remote_port', 5001)))
            self.file_server_dir_edit.setText(str(file_server_config.get('root_dir', '')))

            self.toggle_server_mode()

        except Exception as e:
            logger.error(f"加载配置时发生错误: {e}")
            QMessageBox.warning(self, '错误', f'加载配置时发生错误: {e}')

    def load_log_config(self):
        """加载日志配置"""
        try:
            # 加载日志配置
            log_config = settings.LOG_CONFIG
            
            self.log_dir_edit.setText(str(log_config.get('log_dir', 'C:\\research_project\\log')))
            
            # 将日志级别字符串转换为中文显示
            log_level_map = {'DEBUG': '调试', 'INFO': '信息', 'WARNING': '警告', 'ERROR': '错误', 'CRITICAL': '严重'}
            log_level_str = str(log_config.get('log_level', 'INFO'))
            chinese_level = log_level_map.get(log_level_str, '信息')
            self.log_level_combo.setCurrentText(chinese_level)
            
            self.log_days_spinbox.setValue(int(log_config.get('max_days', 7)))

        except Exception as e:
            logger.error(f"加载日志配置时发生错误: {e}")
            QMessageBox.warning(self, '错误', f'加载日志配置时发生错误: {e}')

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
            logger.error(f"加载提醒配置时发生错误: {e}")

    def save_config(self):
        """保存配置"""
        try:
            # 收集数据库配置
            db_config = {
                'host': self.db_config_host.text().strip(),
                'port': int(self.db_config_port.text().strip() or 3306),
                'db_name': self.db_config_db_name.text().strip(),
                'user': self.db_config_user.text().strip(),
                'password': self.db_config_password.text().strip()
            }

            # 收集文件服务器配置
            file_server_config = {
                'enabled': True,
                'remote_server': self.remote_server_radio.isChecked(),
                'host': "0.0.0.0",
                'port': int(self.local_port_edit.text().strip() or 5001),
                'remote_host': self.remote_host_edit.text().strip(),
                'remote_port': int(self.remote_port_edit.text().strip() or 5001),
                'root_dir': self.file_server_dir_edit.text().strip()
            }

            # 保存配置
            settings.save_config_with_backup('config.json', {
                'database': db_config,
                'file_server': file_server_config
            })

            QMessageBox.information(self, '成功', '配置保存成功！\n重启应用程序后生效。')

        except ValueError as e:
            QMessageBox.warning(self, '错误', f'端口格式错误: {e}')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存配置时发生错误: {e}')

    def save_log_config(self):
        """保存日志配置"""
        try:
            # 收集日志配置
            log_level_map = {'调试': 'DEBUG', '信息': 'INFO', '警告': 'WARNING', '错误': 'ERROR', '严重': 'CRITICAL'}
            log_config = {
                'log_dir': self.log_dir_edit.text().strip() or 'C:\\research_project\\log',
                'log_level': log_level_map.get(self.log_level_combo.currentText(), 'INFO'),
                'max_days': self.log_days_spinbox.value()
            }

            # 保存配置
            settings.save_config_with_backup('config.json', {
                'log_config': log_config
            })

            QMessageBox.information(self, '成功', '日志配置保存成功！\n重启应用程序后生效。')

        except Exception as e:
            QMessageBox.critical(self, '保存失败', f'保存日志配置时发生错误：{str(e)}')

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
