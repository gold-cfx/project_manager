import os
import tempfile
import time

from file_server.client import file_server_client
from file_server.start_server import start_file_server, get_file_server_status


def test_file_server():
    """测试文件服务器的基本功能"""
    print("开始测试文件服务器...")

    try:
        # 检查文件服务器状态
        status = get_file_server_status()
        print(f"文件服务器初始状态: {status}")

        # 如果文件服务器没有运行，尝试启动它
        if not status['is_running']:
            print("尝试启动文件服务器...")
            success = start_file_server()
            print(f"文件服务器启动{'成功' if success else '失败'}")

            # 等待服务器启动
            if success:
                print("等待2秒让服务器完全启动...")
                time.sleep(2)

                # 再次检查状态
                status = get_file_server_status()
                print(f"文件服务器启动后状态: {status}")

        if status['is_running']:
            print("\n开始测试文件操作...")

            # 创建测试文件
            test_content = "这是一个测试文件内容\n包含多行\n用于测试文件服务器功能"
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
            temp_file.write(test_content)
            temp_file.close()

            try:
                # 测试上传文件
                test_filename = "test_upload.txt"
                file_path = file_server_client.upload_file(temp_file.name, test_filename)
                print(f"文件上传成功，路径: {file_path}")

                # 测试检查文件是否存在
                exists = file_server_client.check_file_exists(file_path)
                print(f"文件存在检查: {'存在' if exists else '不存在'}")

                # 测试下载文件
                download_path = os.path.join(tempfile.gettempdir(), "test_download.txt")
                success, error = file_server_client.download_file(file_path, download_path)
                print(f"文件下载{'成功' if success else '失败'}")

                # 验证下载的内容
                if success:
                    with open(download_path, 'r', encoding='utf-8') as f:
                        downloaded_content = f.read()
                    print(f"下载内容验证: {'一致' if downloaded_content == test_content else '不一致'}")

                    # 清理下载的文件
                    os.remove(download_path)
                    print("已清理下载的测试文件")

                # 测试删除文件
                success = file_server_client.delete_file(file_path)
                print(f"文件删除{'成功' if success else '失败'}")

                # 再次检查文件是否存在
                exists = file_server_client.check_file_exists(file_path)
                print(f"删除后文件存在检查: {'存在' if exists else '不存在'}")

            finally:
                # 清理临时文件
                if os.path.exists(temp_file.name):
                    os.remove(temp_file.name)
                    print("已清理原始测试文件")

            # 测试获取服务器状态
            server_status = file_server_client.get_server_status()
            print(f"\n获取服务器状态: {server_status}")

        else:
            print("文件服务器未启动，无法进行文件操作测试")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 测试结束，停止文件服务器（如果是由本测试启动的）
        # 注意：在实际应用中，通常不需要手动停止文件服务器，因为它会随主程序启动和关闭
        # stop_file_server()
        print("\n文件服务器测试完成")


if __name__ == "__main__":
    test_file_server()
