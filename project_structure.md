# 科研项目管理系统 - 项目结构

## 目录结构

```
office-v3/
├── main.py              # 主程序入口
├── ui/                  # 界面模块
│   ├── __init__.py
│   ├── main_window.py   # 主窗口
│   ├── project_registration.py  # 项目登记界面
│   ├── project_query.py         # 项目查询界面
│   ├── reminder_management.py   # 提醒管理界面
│   └── styles.qss       # QSS样式表
├── logic/               # 业务逻辑模块
│   ├── __init__.py
│   ├── project_logic.py  # 项目业务逻辑
│   ├── query_logic.py   # 查询业务逻辑
│   └── reminder_logic.py # 提醒业务逻辑
├── data/                # 数据访问模块
│   ├── __init__.py
│   ├── db_connection.py  # 数据库连接
│   ├── project_dao.py   # 项目数据访问
│   └── reminder_dao.py  # 提醒数据访问
├── utils/               # 工具模块
│   ├── __init__.py
│   ├── validators.py    # 数据验证
│   └── helpers.py       # 辅助函数
└── config/              # 配置模块
    ├── __init__.py
    └── settings.py      # 系统设置
```

## 开发计划

1. 创建基础目录结构
2. 实现数据库连接和初始化
3. 开发主窗口界面
4. 实现项目登记功能
5. 实现项目查询和图表生成功能
6. 实现提醒管理功能
7. 优化界面和用户体验
8. 测试和调试