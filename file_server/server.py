# -*- coding: utf-8 -*-
"""
文件服务器实现
"""
import os
import uuid
from datetime import datetime

from flask import Flask, request, send_file, jsonify, abort
from werkzeug.utils import secure_filename

from file_server.config import file_server_config


class FileServer:
    """文件服务器类"""

    def __init__(self):
        self.app = Flask(__name__)
        self.root_dir = file_server_config.root_dir
        self._setup_routes()

        # 确保存储目录存在
        os.makedirs(self.root_dir, exist_ok=True)

    def _setup_routes(self):
        """设置路由"""

        @self.app.route('/api/files/upload', methods=['POST'])
        def upload_file():
            """上传文件接口"""
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': '没有文件部分'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': '没有选择文件'}), 400

            try:
                # 获取子目录参数
                sub_dir = request.form.get('sub_dir', '')

                # 生成安全的文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                safe_filename = secure_filename(file.filename)
                new_filename = f"{timestamp}_{unique_id}_{safe_filename}"

                # 构建完整的文件路径
                if sub_dir:
                    save_dir = os.path.join(self.root_dir, sub_dir)
                    os.makedirs(save_dir, exist_ok=True)
                    file_path = os.path.join(save_dir, new_filename)
                else:
                    file_path = os.path.join(self.root_dir, new_filename)

                # 保存文件
                file.save(file_path)

                # 计算相对路径（相对于root_dir）
                rel_path = os.path.relpath(file_path, self.root_dir)

                return jsonify({
                    'success': True,
                    'file_path': rel_path,
                    'file_name': safe_filename,
                    'full_path': file_path
                })
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        @self.app.route('/api/files/download/<path:file_path>', methods=['GET'])
        def download_file(file_path):
            """下载文件接口"""
            try:
                # 构建完整的文件路径
                full_path = os.path.join(self.root_dir, file_path)

                # 检查文件是否存在
                if not os.path.exists(full_path):
                    abort(404)

                # 获取文件名（用于下载时显示）
                file_name = os.path.basename(full_path)
                # 尝试从文件名中提取原始文件名（去掉时间戳和UUID部分）
                if '_' in file_name:
                    parts = file_name.split('_')
                    if len(parts) >= 3:
                        original_name = '_'.join(parts[2:])
                    else:
                        original_name = file_name
                else:
                    original_name = file_name

                return send_file(full_path, as_attachment=True, download_name=original_name)
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        @self.app.route('/api/files/delete/<path:file_path>', methods=['DELETE'])
        def delete_file(file_path):
            """删除文件接口"""
            try:
                # 构建完整的文件路径
                full_path = os.path.join(self.root_dir, file_path)

                # 检查文件是否存在
                if not os.path.exists(full_path):
                    return jsonify({'success': False, 'message': '文件不存在'}), 404

                # 删除文件
                os.remove(full_path)

                # 如果目录为空，尝试删除目录
                dir_path = os.path.dirname(full_path)
                if dir_path != self.root_dir and not os.listdir(dir_path):
                    os.rmdir(dir_path)

                return jsonify({'success': True, 'message': '文件已删除'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        @self.app.route('/api/files/exists/<path:file_path>', methods=['GET'])
        def check_file_exists(file_path):
            """检查文件是否存在接口"""
            full_path = os.path.join(self.root_dir, file_path)
            exists = os.path.exists(full_path)
            return jsonify({'exists': exists})

        @self.app.route('/api/server/status', methods=['GET'])
        def server_status():
            """获取服务器状态接口"""
            return jsonify({
                'status': 'running',
                'version': '1.0.0',
                'root_dir': self.root_dir,
                'total_space': self._get_directory_size(self.root_dir)
            })

    def _get_directory_size(self, path):
        """获取目录大小（字节）"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_size += os.path.getsize(fp)
        except Exception:
            pass
        return total_size

    def run(self, host=None, port=None, debug=False):
        """启动文件服务器"""
        if host is None:
            host = file_server_config.host
        if port is None:
            port = file_server_config.port

        logger.info(f"文件服务器启动于 http://{host}:{port}")
        logger.info(f"文件存储目录: {self.root_dir}")

        # 启动Flask服务器
        self.app.run(host=host, port=port, debug=debug, threaded=True)


# 创建全局文件服务器实例
file_server = FileServer()

# 如果直接运行此脚本，则启动文件服务器
if __name__ == '__main__':
    file_server.run(debug=True)
