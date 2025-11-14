import socket
import struct
import time
from typing import Tuple, NamedTuple

from V2.Python.Codroid import Codroid

class PushData(NamedTuple):
    """对应C++中的PushData结构体"""
    isControlling: bool
    errorCode: int
    jointPosition: Tuple[float, float, float, float, float, float]
    endPosition: Tuple[float, float, float, float, float, float]

class UDPReceiver:
    def __init__(self, host: str = '0.0.0.0', port: int = 8888, buffer_size: int = 1024):
        """
        初始化UDP接收器

        Args:
            host: 监听地址，默认监听所有接口
            port: 监听端口
            buffer_size: 缓冲区大小
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.sock = None

    def start(self):
        """启动UDP接收器"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print(f"UDP接收器已启动，监听 {self.host}:{self.port}")

    def receive_data(self) -> PushData:
        """
        接收并解析数据

        Returns:
            PushData: 解析后的数据结构
        """
        if not self.sock:
            raise RuntimeError("接收器未启动，请先调用start()方法")

        # 接收数据
        data, addr = self.sock.recvfrom(self.buffer_size)

        # 解析二进制数据
        # 结构体大小：Bool(1) + UInt8(1) + UInt8[6](6) + Float64[6](48) + Float64[6](48) = 104字节
        if len(data) != 104:
            print(f"警告：接收到的数据长度异常，期望104字节，实际{len(data)}字节")
            # 尝试解析，但可能不准确
            if len(data) < 104:
                # 数据不完整，填充0
                data = data.ljust(104, b'\x00')
            else:
                # 数据过长，截断
                data = data[:104]

        # 使用struct解析二进制数据
        # 格式说明：
        # ?: bool (1字节)
        # B: unsigned char (1字节)
        # 6B: 6个unsigned char
        # 6d: 6个double (关节位置)
        # 6d: 6个double (末端位置)
        unpacked = struct.unpack('?B6B6d6d', data)

        # 解析数据
        is_controlling = unpacked[0]
        error_code = unpacked[1]
        # nc[6] 是 unpacked[2:8]，这里忽略
        joint_position = unpacked[8:14]  # 索引8-13: 6个关节位置
        end_position = unpacked[14:20]  # 索引14-19: 6个末端位置

        push_data = PushData(
            isControlling=is_controlling,
            errorCode=error_code,
            jointPosition=joint_position,
            endPosition=end_position
        )

        return push_data, addr

    def stop(self):
        """停止接收器"""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("UDP接收器已停止")

def main():
    # 创建接收器实例
    receiver = UDPReceiver(host='192.168.1.200', port=9040)

    try:
        receiver.start()

        print("开始接收数据...")
        print("按 Ctrl+C 停止接收")

        while True:
            try:
                # 接收数据
                push_data, addr = receiver.receive_data()

                # 打印接收到的数据
                print(f"\n[{(time.time_ns() / 1e6):.1f}] 来自 {addr} 的数据:")
                print(f"是否允许控制: {push_data.isControlling}")
                print(f"错误码: {push_data.errorCode}")
                print(f"关节位置: {[f'{x:.6f}' for x in push_data.jointPosition]}")
                print(f"末端位置: {[f'{x:.6f}' for x in push_data.endPosition]}")

            except KeyboardInterrupt:
                print("\n用户中断接收")
                break
            except Exception as e:
                print(f"接收数据时发生错误: {e}")
                continue

    except Exception as e:
        print(f"程序运行错误: {e}")
    finally:
        receiver.stop()

if __name__ == "__main__":
    cod = Codroid("192.168.1.200", 9001)
    cod.Connect()
    cod.CRIStartDataPush("192.168.1.200",9040,100)
    time.sleep(2)
    main()
    cod.CRIStopDataPush()
    cod.Disconnect()