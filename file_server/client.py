# -*- coding: utf-8 -*-
"""
文件服务器客户端模块
"""
import os
from typing import Optional, Dict, Any

import requests

from file_server.config import file_server_config
from utils.logger import get_logger

logger = get_logger(__name__)


class FileServerClient:
    """文件服务器客户端类"""

    def __init__(self, host: str = None, port: str = None, root_dir: str = None):
        # 如果提供了自定义参数，使用它们
        self.custom_config = {
            'host': host,
            'port': port,
            'root_dir': root_dir
        }
        self._update_server_url()

    def _update_server_url(self):
        """更新服务器URL（统一使用API访问）"""
        # 如果有自定义配置，使用自定义配置
        if self.custom_config['host'] and self.custom_config['port']:
            self.server_url = f"http://{self.custom_config['host']}:{self.custom_config['port']}"
            self.host = self.custom_config['host']
            self.port = self.custom_config['port']
            self.mode = 'custom'
        else:
            # 获取当前生效的配置（总是返回remote模式）
            host, port, _ = file_server_config.get_effective_config()
            self.server_url = f"http://{host}:{port}"
            self.host = host
            self.port = port
            self.mode = 'remote'

    def upload_file(self, file_path: str, sub_dir: str = '') -> Dict[str, Any]:
        """上传文件到文件服务器（统一通过API上传）
        
        Args:
            file_path: 本地文件路径
            sub_dir: 上传到的子目录
            
        Returns:
            包含上传结果的字典
        """
        self._update_server_url()

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {'success': False, 'message': '文件不存在'}

        # 统一通过API上传文件
        try:
            url = f"{self.server_url}/api/files/upload"
            files = {'file': open(file_path, 'rb')}
            data = {'sub_dir': sub_dir}

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'success': False, 'message': f'上传失败: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'上传失败: {str(e)}'}

    def download_file(self, file_path: str, save_dir: str = '') -> (bool, str):
        """从文件服务器下载文件（统一通过API下载）
        
        Args:
            file_path: 文件在服务器上的相对路径
            save_dir: 保存目录（可选，默认保存到当前目录）
        
        Returns:
            保存的文件路径，如果失败则返回None
        """
        self._update_server_url()

        # 统一通过API下载文件
        try:
            url = f"{self.server_url}/api/files/download/{file_path}"
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # 获取文件名
            file_name = os.path.basename(file_path)
            if save_dir:
                save_dir, save_name = os.path.split(save_dir)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, save_name)
            else:
                save_path = file_name

            # 保存文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True, ""
        except requests.exceptions.RequestException as e:
            logger.error(f"下载失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return False, str(e)

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """从文件服务器删除文件（统一通过API删除）
        
        Args:
            file_path: 文件在服务器上的路径
        
        Returns:
            包含删除结果的字典
        """
        self._update_server_url()

        # 统一通过API删除文件
        try:
            url = f"{self.server_url}/api/files/delete/{file_path}"
            response = requests.delete(url)
            response.raise_for_status()

            return {
                'success': True,
                'message': '文件删除成功'
            }
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return {'success': False, 'message': str(e)}

    def check_file_exists(self, file_path: str) -> bool:
        """检查文件是否存在于文件服务器（统一通过API检查）
        
        Args:
            file_path: 文件在服务器上的路径
            
        Returns:
            文件是否存在
        """
        self._update_server_url()

        # 统一通过API检查文件是否存在
        try:
            url = f"{self.server_url}/api/files/exists/{file_path}"
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            return result.get('exists', False)
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False

    def get_server_status(self) -> Optional[Dict[str, Any]]:
        """获取服务器状态（统一通过API获取）
        
        Returns:
            包含服务器状态的字典，如果失败则返回None
        """
        self._update_server_url()

        # 统一通过API获取服务器状态
        try:
            url = f"{self.server_url}/api/server/status"
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            result['mode'] = 'remote'
            return result
        except Exception as e:
            logger.error(f"获取服务器状态失败: {str(e)}")
            return None

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


# 创建全局客户端实例
file_server_client = FileServerClient()
