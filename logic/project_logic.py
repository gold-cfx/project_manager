#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 项目业务逻辑
"""
from typing import List, Optional, Dict, Any

from data.project_dao import ProjectDAO
from models.project import Project, ProjectCreate, ProjectUpdate, ProjectStatus
from utils.decorators import validate_model_data, log_operation


class ProjectLogic:
    """项目业务逻辑类"""

    def __init__(self):
        self.project_dao = ProjectDAO()

    @validate_model_data(ProjectCreate)
    @log_operation("创建项目")
    def create_project(self, project_data: ProjectCreate) -> int:
        """创建新项目
        
        Args:
            project_data: 项目数据，ProjectCreate模型实例
            
        Returns:
            int: 新创建的项目ID，失败返回-1
        """
        # 检查项目名称是否已存在
        if self.is_project_name_exists(project_data.project_name):
            raise ValueError(f"项目名称 '{project_data.project_name}' 已存在")

        # 创建项目
        return self.project_dao.insert(project_data)

    @validate_model_data(ProjectUpdate)
    @log_operation("更新项目")
    def update_project(self, project_id: int, project_data: ProjectUpdate) -> bool:
        """更新项目信息
        
        Args:
            project_id: 项目ID
            project_data: 项目更新数据，ProjectUpdate模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 检查项目是否存在
        existing_project = self.get_project_by_id(project_id)
        if not existing_project:
            raise ValueError(f"项目ID {project_id} 不存在")

        # 如果更新了项目名称，检查名称是否已存在
        if project_data.project_name and project_data.project_name != existing_project.project_name:
            if self.is_project_name_exists(project_data.project_name):
                raise ValueError(f"项目名称 '{project_data.project_name}' 已存在")

        # 更新项目
        return self.project_dao.update(project_id, project_data)

    @log_operation("删除项目")
    def delete_project(self, project_id: int, operator_id: int = None) -> bool:
        """删除项目
        
        Args:
            project_id: 项目ID
            operator_id: 操作者ID，用于权限验证（可选）
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            PermissionError: 当前用户无删除权限
        """
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除项目")
            
        return self.project_dao.delete(project_id)

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """根据ID获取项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Project]: 项目对象，不存在返回None
        """
        return self.project_dao.get_by_id(project_id)

    def get_project_by_name(self, project_name: str) -> Optional[Project]:
        """根据名称获取项目
        
        Args:
            project_name: 项目名称
            
        Returns:
            Optional[Project]: 项目对象，不存在返回None
        """
        return self.project_dao.get_by_name(project_name)

    def is_project_name_exists(self, project_name: str) -> bool:
        """检查项目名称是否已存在
        
        Args:
            project_name: 项目名称
            
        Returns:
            bool: 是否存在
        """
        return self.get_project_by_name(project_name) is not None

    def get_all_projects(self) -> List[Project]:
        """获取所有项目
        
        Returns:
            List[Project]: 项目列表
        """
        return self.project_dao.get_all()

    def search_projects(self, criteria: Dict[str, Any]) -> List[Project]:
        """搜索项目
        
        Args:
            criteria: 搜索条件
            
        Returns:
            List[Project]: 符合条件的项目列表
        """
        return self.project_dao.search(criteria)

    def get_project_statistics(self) -> Dict[str, Any]:
        """获取项目统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        all_projects = self.get_all_projects()
        status_count = self.project_dao.count_by_status()

        # 计算总资金
        total_funding = sum(float(p.funding_amount) for p in all_projects)

        return {
            "total_count": len(all_projects),
            "status_count": status_count,
            "total_funding": total_funding
        }

    def change_project_status(self, project_id: int, status: ProjectStatus) -> bool:
        """更改项目状态
        
        Args:
            project_id: 项目ID
            status: 新状态
            
        Returns:
            bool: 更改是否成功
        """
        update_data = ProjectUpdate(status=status)
        return self.project_dao.update(project_id, update_data)
