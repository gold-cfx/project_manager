#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 日志模块
提供统一的日志记录功能，支持文件输出和自动清理
"""
import logging
import logging.handlers
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ProjectLogger:
    """项目日志管理器"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.log_dir = None
        self.logger = None
        self.setup_logger()

    def setup_logger(self, log_dir: Optional[str] = None, log_level: int = logging.INFO):
        """设置日志记录器
        
        Args:
            log_dir: 日志文件保存目录，默认为程序目录下的logs文件夹
            log_level: 日志级别，默认为INFO
        """
        if log_dir is None:
            # 默认日志目录为程序根目录下的logs文件夹
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 创建日志记录器
        self.logger = logging.getLogger('ProjectManagement')
        self.logger.setLevel(log_level)

        # 清除现有的处理器
        self.logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 创建文件处理器（按天轮转，保留7天）
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / 'project_management.log',
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 创建错误日志文件处理器
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / 'project_management_error.log',
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """获取日志记录器
        
        Args:
            name: 日志记录器名称，如果为None则返回根记录器
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name is None:
            return self.logger
        return logging.getLogger(f'ProjectManagement.{name}')

    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """记录信息"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """记录异常信息"""
        self.logger.exception(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)

    def cleanup_old_logs(self, days_to_keep: int = 7):
        """清理旧的日志文件
        
        Args:
            days_to_keep: 保留天数，默认为7天
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        for log_file in self.log_dir.glob('*.log*'):
            if log_file.is_file():
                try:
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        log_file.unlink()
                        self.logger.info(f"已删除旧日志文件: {log_file}")
                except Exception as e:
                    self.logger.error(f"删除旧日志文件失败: {log_file}, 错误: {e}")


# 创建全局日志实例
project_logger = ProjectLogger()


# 便捷的日志访问函数
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器"""
    return project_logger.get_logger(name)


def debug(message: str, *args, **kwargs):
    """记录调试信息"""
    project_logger.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """记录信息"""
    project_logger.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """记录警告信息"""
    project_logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """记录错误信息"""
    project_logger.error(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """记录异常信息"""
    project_logger.exception(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """记录严重错误信息"""
    project_logger.critical(message, *args, **kwargs)


# 日志装饰器
def log_function_call(level: int = logging.INFO):
    """函数调用日志装饰器
    
    Args:
        level: 日志级别
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.log(level, f"调用函数: {func.__name__}, 参数: args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"函数执行成功: {func.__name__}, 返回值: {result}")
                return result
            except Exception as e:
                logger.error(f"函数执行失败: {func.__name__}, 错误: {str(e)}")
                raise

        return wrapper

    return decorator
