#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目打包脚本
用于将科研项目管理系统打包为可执行文件
"""

import os
import shutil
import subprocess
import sys


def clean_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")

    # 清理Python缓存文件
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name in ['__pycache__', '.pytest_cache']:
                cache_dir = os.path.join(root, dir_name)
                shutil.rmtree(cache_dir)
                print(f"已清理缓存: {cache_dir}")
        
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                cache_file = os.path.join(root, file)
                os.remove(cache_file)
                print(f"已清理缓存文件: {cache_file}")

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("✗ PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # 检查requirements.txt中的依赖
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        print("正在检查requirements.txt中的依赖...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])

def build_exe():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        # '--onedir',  # 单目录模式，便于调试
        '--onefile',  # 单文件模式，发布时使用
        '--windowed',  # 无控制台窗口
        '--name=科研项目管理系统',
        '--icon=icon/icon.svg' if os.path.exists('icon/icon.svg') else None,
        '--add-data=config_file;config_file',
        '--add-data=help;help',
        '--add-data=icon;icon',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtSql',
        '--hidden-import=sqlalchemy.dialects.sqlite',
        '--collect-all=PyQt5',
        'main.py'
    ]
    
    # 移除None参数
    cmd = [arg for arg in cmd if arg is not None]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        
        # 复制必要的文件到dist目录
        dist_dir = 'dist/科研项目管理系统'
        if os.path.exists(dist_dir):
            # 复制配置文件
            for item in ['config_file', 'help', 'icon']:
                src_path = item
                dst_path = os.path.join(dist_dir, item)
                if os.path.exists(src_path) and not os.path.exists(dst_path):
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                    print(f"已复制 {item} 目录")
        
    except subprocess.CalledProcessError as e:
        print("构建失败!")
        print("错误输出:")
        print(e.stdout)
        print(e.stderr)
        return False
    
    return True

def create_run_script():
    """创建运行脚本"""
    dist_dir = 'dist/科研项目管理系统'
    if os.path.exists(dist_dir):
        # Windows运行脚本
        bat_content = f"""@echo off
echo 正在启动科研项目管理系统...
cd /d "%~dp0"
start 科研项目管理系统.exe
pause
"""
        
        with open(os.path.join(dist_dir, '运行系统.bat'), 'w', encoding='gbk') as f:
            f.write(bat_content)
        
        print("已创建运行脚本")

def main():
    """主函数"""
    print("=" * 50)
    print("科研项目管理系统 打包工具")
    print("=" * 50)
    
    # 清理旧构建
    print("1. 清理旧构建文件...")
    clean_build()
    
    # 检查依赖
    print("2. 检查依赖...")
    check_dependencies()
    
    # 构建
    print("3. 开始构建...")
    if build_exe():
        print("4. 创建运行脚本...")
        create_run_script()
        
        print("\n" + "=" * 50)
        print("构建完成!")
        print("可执行文件位置: dist/科研项目管理系统/科研项目管理系统.exe")
        print("双击运行脚本: dist/科研项目管理系统/运行系统.bat")
        print("=" * 50)
    else:
        print("构建失败，请检查错误信息")

if __name__ == '__main__':
    main()