# -*- coding: utf-8 -*-
"""
文件服务器配置模块
"""
import json
from typing import Tuple

from config import settings
from config.settings import FILE_SERVER_CONFIG, DEFAULT_ROOT_DIR


class FileServerConfig:
    """文件服务器配置类"""
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = '5001'

    def __init__(self):
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        self._config = FILE_SERVER_CONFIG
        # 确保总是启用文件服务器
        self._config['enabled'] = True

    @property
    def host(self) -> str:
        """文件服务器主机地址"""
        return self._config.get('host', self.DEFAULT_HOST)

    @host.setter
    def host(self, value: str):
        self._config['host'] = value
        self._save_config()

    @property
    def port(self) -> int:
        """文件服务器端口"""
        return self._config.get('port', self.DEFAULT_PORT)

    @port.setter
    def port(self, value: int):
        self._config['port'] = value
        self._save_config()

    @property
    def root_dir(self) -> str:
        """文件存储根目录"""
        return self._config.get('root_dir', DEFAULT_ROOT_DIR)

    @root_dir.setter
    def root_dir(self, value: str):
        self._config['root_dir'] = value
        self._save_config()

    @property
    def remote_server(self) -> bool:
        """是否使用远程文件服务器"""
        return self._config.get('remote_server', False)

    @remote_server.setter
    def remote_server(self, value: bool):
        self._config['remote_server'] = value
        self._save_config()

    @property
    def remote_host(self) -> str:
        """远程文件服务器主机地址"""
        return self._config.get('remote_host', '')

    @remote_host.setter
    def remote_host(self, value: str):
        self._config['remote_host'] = value
        self._save_config()

    @property
    def remote_port(self) -> int:
        """远程文件服务器端口"""
        return self._config.get('remote_port', self.DEFAULT_PORT)

    @remote_port.setter
    def remote_port(self, value: int):
        self._config['remote_port'] = value
        self._save_config()

    def get_server_url(self) -> str:
        """获取文件服务器URL"""
        if self.remote_server and self.remote_host:
            return f"http://{self.remote_host}:{self.remote_port}"
        return f"http://{self.host}:{self.port}"

    def get_effective_config(self) -> Tuple[str, int, str]:
        """获取当前生效的服务器配置（始终返回remote模式）"""
        if self.remote_server and self.remote_host:
            return self.remote_host, self.remote_port, "remote"
        # 即使是本地配置，也返回remote模式，强制通过API访问
        return self.host, self.port, "remote"

    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(settings.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            config['file_server'] = self._config

            with open(settings.config_path, 'w', encoding='utf-8') as fw:
                json.dump(config, fw, ensure_ascii=False, indent=2)
        except Exception:
            # 忽略保存配置时的错误
            pass


# 创建全局配置实例
file_server_config = FileServerConfig()
