#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
科研项目管理系统 - 数据字典初始化脚本
"""

import sys
from pathlib import Path

from utils.logger import get_logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.data_dict_dao import DataDictDAO

logger = get_logger(__name__)


def initialize_data_dict():
    """初始化数据字典表和默认数据"""
    try:
        logger.info("开始初始化数据字典...")

        # 创建数据字典DAO实例
        dao = DataDictDAO()

        # 初始化默认数据
        dao.initialize_default_data()

        logger.info("数据字典初始化完成！")

        # 验证数据
        logger.info("\n验证数据字典内容：")

        # 项目状态
        statuses = dao.get_by_type("project_status")
        logger.info(f"项目状态: {[s.dict_value for s in statuses]}")

        # 项目级别
        levels = dao.get_by_type("project_level")
        logger.info(f"项目级别: {[l.dict_value for l in levels]}")

        # 项目来源
        sources = dao.get_by_type("project_source")
        logger.info(f"项目来源: {[s.dict_value for s in sources]}")

        # 项目类型
        types = dao.get_by_type("project_type")
        logger.info(f"项目类型: {[t.dict_value for t in types]}")

        # 成果类型
        result_types = dao.get_by_type("result_type")
        logger.info(f"成果类型: {[r.dict_value for r in result_types]}")

        return True

    except Exception as e:
        logger.error(f"初始化数据字典时出错: {str(e)}")
        return False


if __name__ == "__main__":
    success = initialize_data_dict()
    if success:
        logger.info("\n数据字典初始化成功！")
    else:
        logger.error("\n数据字典初始化失败！")
        sys.exit(1)
