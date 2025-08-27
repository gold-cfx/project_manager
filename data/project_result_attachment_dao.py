#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果附件数据访问对象
"""

from data.db_connection import with_db_connection
from models.project_result_attachment import ProjectResultAttachmentCreate, ProjectResultAttachmentUpdate


class ProjectResultAttachmentDAO:
    """项目成果附件数据访问对象"""

    @staticmethod
    def insert(attachment: ProjectResultAttachmentCreate):
        """插入新的项目成果附件"""

        def op(cursor):
            sql = "INSERT INTO project_result_attachment (project_result_id, file_name, file_path, file_server_host, file_server_port, file_storage_directory) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                attachment.project_result_id,
                attachment.file_name,
                attachment.file_path,
                attachment.file_server_host,
                attachment.file_server_port,
                attachment.file_storage_directory
            ))
            return cursor.lastrowid

        return with_db_connection(op)

    @staticmethod
    def get_by_id(attachment_id: int):
        """根据ID获取项目成果附件"""

        def op(cursor):
            sql = "SELECT * FROM project_result_attachment WHERE id = %s"
            cursor.execute(sql, (attachment_id,))
            return cursor.fetchone()

        return with_db_connection(op)

    @staticmethod
    def get_by_project_result_id(project_result_id: int):
        """根据项目成果ID获取所有附件"""

        def op(cursor):
            sql = "SELECT * FROM project_result_attachment WHERE project_result_id = %s"
            cursor.execute(sql, (project_result_id,))
            return cursor.fetchall()

        return with_db_connection(op)

    @staticmethod
    def update(attachment_id: int, attachment: ProjectResultAttachmentUpdate):
        """更新项目成果附件信息"""

        def op(cursor):
            sql = "UPDATE project_result_attachment SET file_name=%s, file_path=%s, file_server_host=%s, file_server_port=%s, file_storage_directory=%s WHERE id=%s"
            cursor.execute(sql, (
                attachment.file_name,
                attachment.file_path,
                attachment.file_server_host or '',
                attachment.file_server_port or '',
                attachment.file_storage_directory or '',
                attachment_id
            ))
            return cursor.rowcount > 0

        return with_db_connection(op)

    @staticmethod
    def delete(attachment_id: int):
        """删除项目成果附件"""

        def op(cursor):
            sql = "DELETE FROM project_result_attachment WHERE id = %s"
            cursor.execute(sql, (attachment_id,))
            return cursor.rowcount > 0

        return with_db_connection(op)

    @staticmethod
    def delete_by_project_result_id(project_result_id: int):
        """根据项目成果ID删除所有附件"""

        def op(cursor):
            sql = "DELETE FROM project_result_attachment WHERE project_result_id = %s"
            cursor.execute(sql, (project_result_id,))
            return cursor.rowcount > 0

        return with_db_connection(op)
