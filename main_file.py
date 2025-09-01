import time

from file_server.start_server import start_file_server

if __name__ == '__main__':
    start_file_server()
    while True:
        time.sleep(2)
