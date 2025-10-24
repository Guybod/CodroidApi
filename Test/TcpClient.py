import socket
import json

class TCPClient:
    def __init__(self):
        """初始化TCP客户端"""
        self.host = None
        self.port = None
        self.socket = None
        self.connected = False

    def connect(self, host, port):
        """连接到服务器"""
        self.host = host
        self.port = port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"已连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开与服务器的连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.connected = False
            print("连接已关闭")

    def send(self, message,debug:bool=False):
        """发送消息到服务器并返回响应"""
        if not self.connected:
            print("未连接到服务器")
            return None
        try:
            # 发送消息
            if debug:
                print(f"发送消息：{message}")
            self.socket.send(message.encode('utf-8'))
            # 接收响应
            response = self.socket.recv(1024)
            if debug:
                print(f"接收到响应：{response.decode('utf-8')}")
            return response.decode('utf-8')
        except Exception as e:
            print(f"发送消息时出错: {e}")
            self.disconnect()
            return None

if __name__ == "__main__":
    client = TCPClient()
    client.connect("192.168.1.136", 9001)
    message_dict = {
        "id": "m8y21rn20ws74",
        "ty": "globalVar/saveVars",
        "db": {
            "bool1": {
                "nm": 10,
                "val": '"[1,1,1,1,1]"'
            },
            "bool2": {
                "nm": 10,
                "val": '"[1,1,1,1,1]"'
            }
        }
    }
    message_str = json.dumps(message_dict)
    response = client.send(message_str, True)


