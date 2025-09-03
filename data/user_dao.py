#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 用户数据访问对象
"""
import hashlib
from typing import List, Optional

from pymysql.cursors import Cursor, DictCursor

from data.db_connection import with_db_connection
from models.user import User, UserCreate, UserUpdate


class UserDAO:
    """用户数据访问对象"""

    @staticmethod
    @with_db_connection(cursor_type=Cursor)
    def create_user(user_data: UserCreate, cursor: Cursor) -> Optional[int]:
        """创建用户
        
        Args:
            user_data: 用户创建数据
            cursor: 数据库游标
            
        Returns:
            Optional[int]: 用户ID，创建失败返回None
        """
        # 密码加密
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()

        sql = """
            INSERT INTO users (username, password, real_name, role, status, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (
                user_data.username,
                hashed_password,
                user_data.real_name,
                user_data.role.value,
                user_data.status.value,
                user_data.email,
                user_data.phone
            ))
            return cursor.lastrowid
        except Exception as e:
            print(f"创建用户失败: {e}")
            return None

    @staticmethod
    @with_db_connection()
    def get_user_by_username(username: str, cursor: DictCursor) -> Optional[User]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            cursor: 数据库游标
            
        Returns:
            Optional[User]: 用户信息
        """
        sql = """
            SELECT id, username, password, real_name, role, status, 
                   email, phone, last_login, create_time, update_time
            FROM users WHERE username = %s
        """
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                real_name=row['real_name'],
                role=row['role'],
                status=row['status'],
                email=row['email'],
                phone=row['phone'],
                last_login=row['last_login'],
                create_time=row['create_time'],
                update_time=row['update_time']
            )
        return None

    @staticmethod
    @with_db_connection()
    def get_user_by_id(user_id: int, cursor: DictCursor) -> Optional[User]:
        """根据用户ID获取用户
        
        Args:
            user_id: 用户ID
            cursor: 数据库游标
            
        Returns:
            Optional[User]: 用户信息
        """
        sql = """
            SELECT id, username, password, real_name, role, status, 
                   email, phone, last_login, create_time, update_time
            FROM users WHERE id = %s
        """
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                real_name=row['real_name'],
                role=row['role'],
                status=row['status'],
                email=row['email'],
                phone=row['phone'],
                last_login=row['last_login'],
                create_time=row['create_time'],
                update_time=row['update_time']
            )
        return None

    @staticmethod
    @with_db_connection(cursor_type=Cursor)
    def update_user(user_id: int, user_data: UserUpdate, cursor: Cursor) -> bool:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            cursor: 数据库游标
            
        Returns:
            bool: 更新是否成功
        """
        fields = []
        values = []

        if user_data.real_name is not None:
            fields.append("real_name = %s")
            values.append(user_data.real_name)
        if user_data.role is not None:
            fields.append("role = %s")
            values.append(user_data.role.value)
        if user_data.status is not None:
            fields.append("status = %s")
            values.append(user_data.status.value)
        if user_data.email is not None:
            fields.append("email = %s")
            values.append(user_data.email)
        if user_data.phone is not None:
            fields.append("phone = %s")
            values.append(user_data.phone)
        if user_data.password is not None:
            hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
            fields.append("password = %s")
            values.append(hashed_password)

        if not fields:
            return False

        fields.append("update_time = NOW()")
        values.append(user_id)

        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"

        try:
            cursor.execute(sql, values)
            return cursor.rowcount > 0
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False

    @staticmethod
    @with_db_connection(cursor_type=Cursor)
    def delete_user(user_id: int, cursor: Cursor) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            cursor: 数据库游标
            
        Returns:
            bool: 删除是否成功
        """
        sql = "DELETE FROM users WHERE id = %s"
        try:
            cursor.execute(sql, (user_id,))
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False

    @staticmethod
    @with_db_connection()
    def get_all_users(cursor: DictCursor) -> List[User]:
        """获取所有用户
        
        Args:
            cursor: 数据库游标
            
        Returns:
            List[User]: 用户列表
        """
        sql = """
            SELECT id, username, password, real_name, role, status, 
                   email, phone, last_login, create_time, update_time
            FROM users ORDER BY create_time DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append(User(
                id=row['id'],
                username=row['username'],
                real_name=row['real_name'],
                role=row['role'],
                status=row['status'],
                email=row['email'],
                phone=row['phone'],
                last_login=row['last_login'],
                create_time=row['create_time'],
                update_time=row['update_time']
            ))
        return users

    @staticmethod
    @with_db_connection()
    def authenticate_user(username: str, password: str, cursor: DictCursor) -> Optional[User]:
        """用户认证
        
        Args:
            username: 用户名
            password: 密码
            cursor: 数据库游标
            
        Returns:
            Optional[User]: 认证成功返回用户信息，失败返回None
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 检查用户是否存在
        sql = """
            SELECT id, username, password, real_name, role, status, 
                   email, phone, last_login, create_time, update_time
            FROM users WHERE username = %s
        """
        cursor.execute(sql, (username,))
        row = cursor.fetchone()

        if not row:
            return None

        # 检查密码是否正确
        if row['password'] != hashed_password:
            return None

        # 检查用户状态
        if row['status'] != 'active':
            return None

        # 更新最后登录时间
        update_sql = "UPDATE users SET last_login = NOW() WHERE id = %s"
        cursor.execute(update_sql, (row['id'],))

        return User(
            id=row['id'],
            username=row['username'],
            real_name=row['real_name'],
            role=row['role'],
            status=row['status'],
            email=row['email'],
            phone=row['phone'],
            last_login=row['last_login'],
            create_time=row['create_time'],
            update_time=row['update_time']
        )

    @staticmethod
    @with_db_connection()
    def is_username_exists(username: str, cursor: DictCursor) -> bool:
        """检查用户名是否存在
        
        Args:
            username: 用户名
            cursor: 数据库游标
            
        Returns:
            bool: 是否存在
        """
        sql = "SELECT COUNT(*) as count FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        return row['count'] > 0

    @staticmethod
    @with_db_connection()
    def verify_password(username: str, password: str, cursor: DictCursor) -> bool:
        """验证用户密码是否正确
        
        Args:
            username: 用户名
            password: 密码
            cursor: 数据库游标
            
        Returns:
            bool: 密码是否正确
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        sql = "SELECT password FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        
        if not row:
            return False
            
        return row['password'] == hashed_password

    @staticmethod
    @with_db_connection(cursor_type=Cursor)
    def change_password(username: str, new_password: str, cursor: Cursor) -> bool:
        """修改用户密码
        
        Args:
            username: 用户名
            new_password: 新密码
            cursor: 数据库游标
            
        Returns:
            bool: 修改是否成功
        """
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        sql = "UPDATE users SET password = %s, update_time = NOW() WHERE username = %s"
        try:
            cursor.execute(sql, (hashed_password, username))
            return cursor.rowcount > 0
        except Exception as e:
            print(f"修改密码失败: {e}")
            return False
