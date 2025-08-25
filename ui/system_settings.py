from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMainWindow
import json
import os

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
        self.db_config_edit = QLineEdit()
        self.db_config_edit.setPlaceholderText('请输入数据库连接字符串')
        form_layout.addRow('数据库配置', self.db_config_edit)

        # 上传目录配置
        self.upload_dir_edit = QLineEdit()
        self.upload_dir_edit.setPlaceholderText('请选择上传目录')
        self.upload_dir_edit.setReadOnly(True)
        self.select_dir_button = QPushButton('选择目录')
        self.select_dir_button.clicked.connect(self.select_directory)
        form_layout.addRow('上传目录', self.upload_dir_edit)
        form_layout.addRow('', self.select_dir_button)

        # 保存按钮
        self.save_button = QPushButton('保存配置')
        self.save_button.clicked.connect(self.save_config)
        form_layout.addRow('', self.save_button)

        main_layout.addLayout(form_layout)

        # 加载现有配置
        self.load_config()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, '选择上传目录')
        if directory:
            self.upload_dir_edit.setText(directory)

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.db_config_edit.setText(config.get('database', ''))
                self.upload_dir_edit.setText(config.get('upload_dir', ''))

    def save_config(self):
        config = {
            'database': self.db_config_edit.text(),
            'upload_dir': self.upload_dir_edit.text()
        }
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            main_window.statusBar().showMessage('配置已保存')