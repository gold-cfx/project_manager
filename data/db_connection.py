#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 数据库连接管理
"""
import pymysql
from pymysql.cursors import DictCursor

from config.settings import DB_CONFIG


class DatabaseConnection:
    """数据库连接管理类"""
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.config = DB_CONFIG
            self._connection = None

    def connect(self):
        """建立数据库连接"""
        if self._connection is None or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.config['host'],
                    user=self.config['user'],
                    password=self.config['password'],
                    db=self.config['db'],
                    charset=self.config['charset'],
                    cursorclass=DictCursor
                )
                print("数据库连接成功")
            except Exception as e:
                print(f"数据库连接失败: {e}")
                self._connection = None
        return self._connection

    def close(self):
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
            print("数据库连接已关闭")

    def get_connection(self):
        """获取数据库连接"""
        return self.connect()


# 全局数据库连接实例
_db_instance = DatabaseConnection()


def get_connection():
    """获取数据库连接"""
    return _db_instance.get_connection()


from utils.decorators import format_datetime_in_result


def with_db_connection(operation, cursor_type=DictCursor, commit=True):
    """
    执行数据库操作的公共函数，封装连接创建、游标初始化、异常处理和资源释放
    
    Args:
        operation: 一个函数，接受cursor参数，包含具体的数据库操作
        cursor_type: 游标的类型，默认为DictCursor
        commit: 是否需要commit

    Returns:
        数据库操作的结果
    """

    @format_datetime_in_result
    def execute_operation():
        conn = get_connection()
        cursor = conn.cursor(cursor_type)
        try:
            result = operation(cursor)
            if commit:
                conn.commit()
            return result
        except Exception as e:
            print(f"数据库操作失败: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return execute_operation()


def init_database():
    """初始化数据库"""
    conn = get_connection()
    if not conn:
        print("无法连接到数据库，初始化失败")
        return False

    cursor = conn.cursor()
    try:

        # 创建项目表
        create_projects_table = """
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL UNIQUE,
                leader VARCHAR(50) NOT NULL,
                department VARCHAR(50) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                project_source VARCHAR(50) NOT NULL,
                project_type VARCHAR(50) NOT NULL,
                level VARCHAR(20) NOT NULL,
                funding_amount DECIMAL(15, 2) NOT NULL,
                funding_unit VARCHAR(100) NOT NULL,
                approval_year VARCHAR(20) NOT NULL,
                project_number VARCHAR(50) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT '进行中',
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_projects_table)

        # 创建项目成果表
        create_project_result_table = """
            CREATE TABLE IF NOT EXISTS project_result (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                type VARCHAR(20) NOT NULL,
                name VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """
        cursor.execute(create_project_result_table)

        # 创建项目成果附件表
        create_project_result_attachment_table = """
            CREATE TABLE IF NOT EXISTS project_result_attachment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_result_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_result_id) REFERENCES project_result(id) ON DELETE CASCADE
            )
        """
        cursor.execute(create_project_result_attachment_table)

        # 创建提醒表
        create_reminders_table = """
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                reminder_type VARCHAR(20) NOT NULL,
                days_before INT NOT NULL,
                reminder_way VARCHAR(20) NOT NULL,
                content TEXT,
                start_date DATE NOT NULL,
                status VARCHAR(10) NOT NULL DEFAULT '未读',
                create_time TIMESTAMP NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """
        cursor.execute(create_reminders_table)

        # 创建系统配置表
        create_system_config_table = """
            CREATE TABLE IF NOT EXISTS system_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                config_key VARCHAR(50) NOT NULL UNIQUE,
                config_value TEXT NOT NULL,
                description VARCHAR(255),
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_system_config_table)

        create_help_info_table = f"""
            CREATE TABLE IF NOT EXISTS help_docs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                version VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_help_info_table)

        conn.commit()
        print("数据库初始化成功")
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"数据库初始化失败: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
