import json
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMainWindow
from config import settings

class SystemSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建表单布局
        form_layout = QFormLayout()

        # 数据库配置
        self.db_config_host = QLineEdit()
        self.db_config_host.setPlaceholderText('请输入数据库连接主机ip地址')
        form_layout.addRow('数据库主机', self.db_config_host)
        self.db_config_db_name = QLineEdit()
        self.db_config_db_name.setPlaceholderText('请输入数据库连接库名')
        form_layout.addRow('数据库连接库名', self.db_config_db_name)
        self.db_config_user = QLineEdit()
        self.db_config_user.setPlaceholderText('请输入数据库连接用户名')
        form_layout.addRow('数据库连接用户名', self.db_config_user)
        self.db_config_password = QLineEdit()
        self.db_config_password.setPlaceholderText('请输入数据库连接密码')
        form_layout.addRow('数据库连接密码', self.db_config_password)

        # 上传目录配置
        self.upload_dir_edit = QLineEdit()
        self.upload_dir_edit.setPlaceholderText('请选择附件存储目录')
        self.upload_dir_edit.setReadOnly(True)
        self.select_dir_button = QPushButton('选择目录')
        self.select_dir_button.clicked.connect(self.select_directory)
        form_layout.addRow('附件存储目录', self.upload_dir_edit)
        form_layout.addRow('', self.select_dir_button)

        # 保存按钮
        self.save_button = QPushButton('保存配置')
        self.save_button.clicked.connect(self.save_config)
        form_layout.addRow('', self.save_button)

        main_layout.addLayout(form_layout)

        # 加载现有配置
        self.load_config()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, '选择附件存储目录')
        if directory:
            self.upload_dir_edit.setText(directory)

    def load_config(self):
        self.upload_dir_edit.setText(settings.UPLOAD_DIR)
        db_config = settings.DB_CONFIG
        self.db_config_host.setText(db_config.get("host"))
        self.db_config_user.setText(db_config.get("user"))
        self.db_config_db_name.setText(db_config.get("db"))
        self.db_config_password.setText(db_config.get("password"))

    def save_config(self):
        db_config = {
            'host': self.db_config_host.text(),
            'user': self.db_config_user.text(),
            'password': self.db_config_password.text(),
            'db': self.db_config_db_name.text(),
            'charset': 'utf8mb4'  # 字符集
        }
        config = {
            'database': db_config,
            'upload_dir': self.upload_dir_edit.text()
        }
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            main_window.statusBar().showMessage('配置已保存, 重启后生效！')
