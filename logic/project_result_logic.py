#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科研项目管理系统 - 项目成果业务逻辑
"""
from typing import List, Optional, Dict, Any

from data.project_result_dao import ProjectResultDAO
from models.project_result import ProjectResult, ProjectResultCreate, ProjectResultUpdate
from utils.decorators import validate_model_data, log_operation


class ProjectResultLogic:
    """项目成果业务逻辑类"""

    def __init__(self):
        self.project_result_dao = ProjectResultDAO()

    @validate_model_data(ProjectResultCreate)
    @log_operation("创建项目成果")
    def create_project_result(self, result_data: ProjectResultCreate) -> int:
        """创建新项目成果
        
        Args:
            result_data: 项目成果数据，ProjectResultCreate模型实例
            
        Returns:
            int: 新创建的项目成果ID，失败返回-1
        """
        return self.project_result_dao.insert(result_data)

    @validate_model_data(ProjectResultUpdate)
    @log_operation("更新项目成果")
    def update_project_result(self, result_id: int, result_data: ProjectResultUpdate) -> bool:
        """更新项目成果信息
        
        Args:
            result_id: 项目成果ID
            result_data: 项目成果更新数据，ProjectResultUpdate模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 检查项目成果是否存在
        existing_result = self.get_project_result_by_id(result_id)
        if not existing_result:
            raise ValueError(f"项目成果ID {result_id} 不存在")

        # 更新项目成果
        return self.project_result_dao.update(result_id, result_data)

    @log_operation("删除项目成果")
    def delete_project_result(self, result_id: int) -> bool:
        """删除项目成果
        
        Args:
            result_id: 项目成果ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            PermissionError: 当前用户无删除权限
        """
        # 检查管理员权限
        from utils.session import SessionManager
        if not SessionManager.is_admin():
            raise PermissionError("只有管理员才能删除项目成果")

        return self.project_result_dao.delete(result_id)

    def get_project_result_by_id(self, result_id: int) -> Optional[ProjectResult]:
        """根据ID获取项目成果
        
        Args:
            result_id: 项目成果ID
            
        Returns:
            Optional[ProjectResult]: 项目成果对象，不存在返回None
        """
        return self.project_result_dao.get_by_id(result_id)

    def get_project_results_by_project_id(self, project_id: int) -> List[ProjectResult]:
        """根据项目ID获取所有项目成果
        
        Args:
            project_id: 项目ID
            
        Returns:
            List[ProjectResult]: 项目成果列表
        """
        return self.project_result_dao.get_by_project_id(project_id)

    @log_operation("批量创建项目成果")
    def batch_create_project_results(self, project_id: int, results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量创建项目成果
        
        Args:
            project_id: 项目ID
            results_data: 项目成果数据列表，每个元素包含type、name和date字段
            
        Returns:
            List[Dict[str, Any]]: 成功创建的项目成果列表，包含id和原始数据
        """
        # 先删除该项目的所有成果
        self.project_result_dao.delete_by_project_id(project_id)

        # 创建新的成果
        saved_results = []
        for result_data in results_data:
            # 确保包含project_id
            result_data['project_id'] = project_id

            try:
                # 创建成果
                create_data = ProjectResultCreate(**result_data)
                result_id = self.create_project_result(create_data)
                if result_id > 0:
                    # 将新创建的成果ID添加到结果数据中
                    result_data['id'] = result_id
                    saved_results.append(result_data)
                else:
                    print(f"创建项目成果失败，ID返回0或负数: {result_data.get('name')}")
            except Exception as e:
                print(f"创建项目成果失败: {e}")

        return saved_results
