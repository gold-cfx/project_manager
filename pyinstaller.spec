# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_all

# 获取当前目录
work_path = os.path.dirname(os.path.abspath(__file__))

# 收集PyQt5数据文件
datas = []
binaries = []
hiddenimports = []

# 添加配置文件
datas.append((os.path.join(work_path, 'config_file'), 'config_file'))
datas.append((os.path.join(work_path, 'help'), 'help'))
datas.append((os.path.join(work_path, 'icon'), 'icon'))


# 添加PyQt5依赖
def collect_pyqt5_data():
    pyqt5_datas = []
    pyqt5_binaries = []
    
    # 收集PyQt5文件
    pyqt5_path = None
    for path in sys.path:
        if path and 'PyQt5' in path and 'site-packages' in path:
            pyqt5_path = path
            break
    
    if pyqt5_path:
        # 添加Qt插件
        qt_plugins = os.path.join(pyqt5_path, 'PyQt5', 'Qt5', 'plugins')
        if os.path.exists(qt_plugins):
            datas.append((qt_plugins, 'PyQt5/Qt5/plugins'))
    
    return pyqt5_datas, pyqt5_binaries

pyqt5_datas, pyqt5_binaries = collect_pyqt5_data()
datas.extend(pyqt5_datas)
binaries.extend(pyqt5_binaries)

# 主程序配置
a = Analysis(
    ['main.py'],
    pathex=[work_path],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'PyQt5.QtSql',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.ext.declarative',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='科研项目管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/icon.ico' if os.path.exists('icon/icon.ico') else None,
)