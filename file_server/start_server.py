# -*- coding: utf-8 -*-
"""
文件服务器启动模块
"""
import logging
import threading
import time

from file_server.config import file_server_config
from file_server.server import file_server

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('file_server')


class FileServerManager:
    """文件服务器管理类"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FileServerManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """初始化文件服务器管理器"""
        self.server_thread = None
        self.server_running = False
        self._stop_event = threading.Event()

    def start_server(self):
        """启动文件服务器"""
        with self._lock:
            # 文件服务器始终启用

            # 检查是否使用远程服务器
            if file_server_config.remote_server and file_server_config.remote_host:
                logger.info(f"使用远程文件服务器: {file_server_config.remote_host}:{file_server_config.remote_port}")
                return True  # 即使使用远程服务器，也返回成功标志

            # 确保配置中enabled为True
            file_server_config._config['enabled'] = True

            # 检查服务器是否已在运行
            if self.server_running:
                logger.info("文件服务器已经在运行中")
                return True

            # 创建并启动服务器线程
            self._stop_event.clear()
            self.server_thread = threading.Thread(
                target=self._server_thread_func,
                daemon=True
            )
            self.server_thread.start()

            # 等待服务器启动
            max_wait_time = 5  # 最大等待时间（秒）
            start_time = time.time()
            while not self.server_running and time.time() - start_time < max_wait_time:
                time.sleep(0.1)

            if self.server_running:
                logger.info(f"文件服务器已成功启动于 http://{file_server_config.host}:{file_server_config.port}")
                return True
            else:
                logger.error("文件服务器启动失败")
                return False

    def _server_thread_func(self):
        """服务器线程函数"""
        try:
            # 标记服务器开始运行
            self.server_running = True

            # 启动文件服务器
            file_server.run(
                host=file_server_config.host,
                port=file_server_config.port,
                debug=False  # 生产环境中不使用debug模式
            )
        except Exception as e:
            logger.error(f"文件服务器运行出错: {str(e)}")
            self.server_running = False
        finally:
            # 确保服务器状态被正确标记
            self.server_running = False

    def stop_server(self):
        """停止文件服务器"""
        with self._lock:
            if not self.server_running:
                return True

            # 设置停止事件
            self._stop_event.set()

            # 等待服务器线程结束
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)  # 等待最多5秒

            # 检查线程是否已结束
            if self.server_thread and self.server_thread.is_alive():
                logger.warning("文件服务器线程未能在超时时间内结束")
                return False

            self.server_running = False
            logger.info("文件服务器已停止")
            return True

    def is_server_running(self) -> bool:
        """检查文件服务器是否在运行"""
        return self.server_running

    def get_server_status(self) -> dict:
        """获取服务器状态信息"""
        if file_server_config.remote_server and file_server_config.remote_host:
            mode = "remote"
            status = "connected" if self._check_remote_server() else "disconnected"
        else:
            mode = "local"
            status = "running" if self.server_running else "stopped"

        return {
            'mode': mode,
            'status': status,
            'host': file_server_config.get_effective_config()[0],
            'port': file_server_config.get_effective_config()[1],
            'root_dir': file_server_config.root_dir,
            'enabled': file_server_config.enabled
        }

    def _check_remote_server(self) -> bool:
        """检查远程服务器连接状态"""
        try:
            from file_server.client import file_server_client
            status = file_server_client.get_server_status()
            return status is not None
        except Exception:
            return False


# 创建全局文件服务器管理器实例
file_server_manager = FileServerManager()


# 启动文件服务器的便捷函数
def start_file_server():
    """启动文件服务器
    
    Returns:
        bool: 启动是否成功
    """
    return file_server_manager.start_server()


# 停止文件服务器的便捷函数
def stop_file_server():
    """停止文件服务器
    
    Returns:
        bool: 停止是否成功
    """
    return file_server_manager.stop_server()


# 检查文件服务器状态的便捷函数
def get_file_server_status():
    """获取文件服务器状态
    
    Returns:
        dict: 包含服务器状态信息的字典
    """
    return file_server_manager.get_server_status()
