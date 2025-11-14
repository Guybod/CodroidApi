import math
import socket
import struct
import time
import numpy as np
from typing import List, Tuple
import threading
from dataclasses import dataclass
from enum import Enum

from V2.Python.Codroid import Codroid

class CommandType(Enum):
    JOINT = 0
    END_EFFECTOR = 1

@dataclass
class CommandData:
    """对应C++中的CommandData结构体"""
    timestamp: int = 0
    position: List[float] = None
    cmd_type: CommandType = CommandType.JOINT

    def __post_init__(self):
        if self.position is None:
            self.position = [0.0] * 6

class MotionPlanner:
    """运动规划器"""

    def __init__(self, control_frequency: float = 1000.0):
        """
        Args:
            control_frequency: 控制频率(Hz)
        """
        self.control_frequency = control_frequency
        self.dt = 1.0 / control_frequency

    def linear_interpolation(self, start_pos: List[float], target_pos: List[float],
                             duration: float) -> List[List[float]]:
        """线性插值规划

        Args:
            start_pos: 起始位置 [6]
            target_pos: 目标位置 [6]
            duration: 运动持续时间(s)

        Returns:
            轨迹点列表
        """
        num_points = int(duration * self.control_frequency)
        if num_points < 2:
            return [target_pos]

        trajectory = []
        start_pos = np.array(start_pos)
        target_pos = np.array(target_pos)

        for i in range(num_points):
            t = i / (num_points - 1)
            point = start_pos + t * (target_pos - start_pos)
            trajectory.append(point.tolist())

        return trajectory

    def cubic_polynomial_interpolation(self, start_pos: List[float], target_pos: List[float],
                                       start_vel: List[float], end_vel: List[float],
                                       duration: float) -> List[List[float]]:
        """三次多项式插值规划

        Args:
            start_pos: 起始位置
            target_pos: 目标位置
            start_vel: 起始速度
            end_vel: 结束速度
            duration: 运动时间

        Returns:
            轨迹点列表
        """
        num_points = int(duration * self.control_frequency)
        if num_points < 2:
            return [target_pos]

        trajectory = []
        start_pos = np.array(start_pos)
        target_pos = np.array(target_pos)
        start_vel = np.array(start_vel)
        end_vel = np.array(end_vel)

        for i in range(num_points):
            t = i / (num_points - 1)
            t2 = t * t
            t3 = t2 * t

            # 三次多项式系数
            h0 = 2 * t3 - 3 * t2 + 1
            h1 = t3 - 2 * t2 + t
            h2 = -2 * t3 + 3 * t2
            h3 = t3 - t2

            point = (h0 * start_pos + h1 * duration * start_vel +
                     h2 * target_pos + h3 * duration * end_vel)
            trajectory.append(point.tolist())

        return trajectory

class UDPCommandSender:
    """UDP命令发送器"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def send_command(self, command: CommandData):
        """发送命令数据

        Args:
            command: 命令数据
        """
        # 设置时间戳（自增1）
        command.timestamp = self.sequence_number
        self.sequence_number += 1

        # 打包二进制数据
        # Int64: q (long long), Float64: d (double), UInt8: B (unsigned char)
        data = struct.pack('q', command.timestamp)  # timestamp
        for pos in command.position:  # position[6]
            data += struct.pack('d', pos)
        data += struct.pack('B', command.cmd_type.value)  # type
        data += struct.pack('BBBBBBB', 0, 0, 0, 0, 0, 0, 0)  # nc[7] 填充0

        # 发送数据
        self.sock.sendto(data, (self.host, self.port))

    def close(self):
        """关闭socket"""
        self.sock.close()

class RobotController:
    """机器人控制器"""

    def __init__(self, udp_host: str, udp_port: int, control_frequency: float = 1000.0):
        self.planner = MotionPlanner(control_frequency)
        self.sender = UDPCommandSender(udp_host, udp_port)
        self.control_frequency = control_frequency
        self.is_running = False
        self.current_position = [0.0] * 6  # 当前位置
        self.thread = None

    def move_to_target(self, target_position: List[float], duration: float = 3.0,
                       motion_type: CommandType = CommandType.JOINT,
                       use_cubic: bool = False):
        """移动到目标位置

        Args:
            target_position: 目标位置 [6个关节角度，单位rad]
            duration: 运动持续时间(s)
            motion_type: 运动类型（关节空间或末端空间）
            use_cubic: 是否使用三次多项式插值
        """
        print(f"开始规划运动: {self.current_position} -> {target_position}")
        print(f"运动时间: {duration}s, 类型: {motion_type}")

        # 生成轨迹
        if use_cubic:
            # 使用三次多项式插值（起始和结束速度设为0）
            start_vel = [0.0] * 6
            end_vel = [0.0] * 6
            trajectory = self.planner.cubic_polynomial_interpolation(
                self.current_position, target_position, start_vel, end_vel, duration)
        else:
            # 使用线性插值
            trajectory = self.planner.linear_interpolation(
                self.current_position, target_position, duration)

        print(f"轨迹点数: {len(trajectory)}")

        # 发送轨迹点
        start_time = time.time()
        for i, point in enumerate(trajectory):
            # 计算实际经过的时间
            elapsed_time = time.time() - start_time
            expected_time = i * self.planner.dt

            # 时间补偿
            if elapsed_time < expected_time:
                time.sleep(expected_time - elapsed_time)

            # 创建命令并发送
            command = CommandData(position=point, cmd_type=motion_type)
            self.sender.send_command(command)

            # 更新当前位置
            self.current_position = point.copy()

            if i % 50 == 0:  # 每50个点打印一次进度
                print(f"进度: {i + 1}/{len(trajectory)}, 位置: {[f'{p:.3f}' for p in point]}")

        print("运动完成!")

    def move_joints_smoothly(self, target_joints: List[float], duration: float = 3.0):
        """平滑移动到关节目标位置（使用三次多项式插值）"""
        self.move_to_target(target_joints, duration, CommandType.JOINT, use_cubic=True)

    def move_cart_smoothly(self, target_joints: List[float], duration: float = 3.0):
        """平滑移动到关节目标位置（使用三次多项式插值）"""
        self.move_to_target(target_joints, duration, CommandType.END_EFFECTOR, use_cubic=True)

    def move_joints_linear(self, target_joints: List[float], duration: float = 3.0):
        """线性移动到关节目标位置"""
        self.move_to_target(target_joints, duration, CommandType.JOINT, use_cubic=False)

    def set_current_position(self, position: List[float]):
        """设置当前位置"""
        if len(position) == 6:
            self.current_position = position.copy()
            print(f"当前位置已设置为: {position}")
        else:
            raise ValueError("位置数组必须包含6个元素")

    def stop(self):
        """停止运动"""
        self.is_running = False

    def close(self):
        """关闭连接"""
        self.sender.close()

# 使用示例
def main():
    # 配置参数
    UDP_HOST = "192.168.1.136"  # C++服务端IP地址
    UDP_PORT = 9030  # C++服务端端口

    # 创建控制器
    controller = RobotController(UDP_HOST, UDP_PORT, control_frequency=500.0)

    try:
        # 设置初始位置（单位：rad）
        initial_position = [0.0, 0.0, 1.570796, 0.0, 0.0, 0.0]
        controller.set_current_position(initial_position)

        # 示例运动序列
        print("=== 开始运动演示 ===")

        # 1. 平滑移动到第一个目标位置
        target1 = [0.5, -0.3, 0.8, 0.2, -0.4, 0.1]
        controller.move_joints_smoothly(target1, duration=4.0)

        time.sleep(3)  # 暂停1秒

        # 2. 线性移动到第二个目标位置
        target2 = [-0.3, 0.6, -0.2, 0.4, 0.3, -0.5]
        controller.move_joints_smoothly(target2, duration=3.0)

        time.sleep(3)

        # 3. 返回初始位置
        controller.move_joints_smoothly(initial_position, duration=5.0)

        print("=== 运动演示完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        controller.close()

# 使用示例
def main2():
    # 配置参数
    UDP_HOST = "192.168.1.136"  # C++服务端IP地址
    UDP_PORT = 9030  # C++服务端端口

    # 创建控制器
    controller = RobotController(UDP_HOST, UDP_PORT, control_frequency=250.0)

    try:
        # 设置初始位置（单位：rad）
        initial_position = [0.494, 0.191000, 0.424500, -3.141593, 0, -1.570796]
        controller.set_current_position(initial_position)

        # 示例运动序列
        print("=== 开始运动演示 ===")

        # 1. 平滑移动到第一个目标位置
        target1 = [0.494, 0.191000, 0.224500, -3.141593, 0, -1.570796]
        controller.move_cart_smoothly(target1, duration=2.0)

        target2 = [0.494, 0.191000, 0.424500, -3.141593, 0, -1.570796]
        controller.move_cart_smoothly(target2, duration=2.0)

        print("=== 运动演示完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        controller.close()

# 实时控制示例
class RealTimeController:
    """实时控制器（支持外部输入）"""

    def __init__(self, udp_host: str, udp_port: int):
        self.controller = RobotController(udp_host, udp_port)

    def interactive_control(self):
        """交互式控制"""
        print("交互式控制模式")
        print("输入目标位置（6个关节角度，用空格分隔，单位rad）")
        print("输入 'quit' 退出")

        while True:
            try:
                user_input = input("\n目标位置: ").strip()
                if user_input.lower() == 'quit':
                    break

                # 解析输入
                positions = [float(x) for x in user_input.split()]
                if len(positions) != 6:
                    print("错误：请输入6个关节角度")
                    continue

                # 获取运动时间
                duration = float(input("运动时间(s): ").strip())

                # 执行运动
                self.controller.move_joints_smoothly(positions, duration)

            except ValueError:
                print("错误：请输入有效的数字")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")

# 封装好的demo
def demo1():
    # 启动之前先发送打开实时控制接口命令
    cod = Codroid("192.168.1.136", 9001)
    cod.Connect()
    # 设置初始位置（单位：rad）
    # initial_position = [0.0, 0.0, 1.570796, 0.0, 0.0, 0.0]
    # 由于main的初始地址为[0,0,90,0,0,0]，所以先移动到该位置
    cod.MovJ([0, 0, 90, 0, 0, 0])
    time.sleep(2)
    # 开启实时控制接口（关闭滤波，指令间隔2ms，启动缓冲点数量3个）
    # 指令间隔由RobotController的control_frequency决定 (500hz，2ms)
    # controller = RobotController(UDP_HOST, UDP_PORT, control_frequency=500.0)
    cod.CRIStartControl(filterType=0, duration=2, startBuffer=3)
    time.sleep(2)
    main()
    time.sleep(2)
    # 关闭实时控制接口
    cod.CRIStopControl()
    time.sleep(2)
    cod.Disconnect()

# 封装好的demo
def demo2():
    # 启动之前先发送打开实时控制接口命令
    cod = Codroid("192.168.1.136", 9001)
    cod.Connect()
    # 设置初始位置（单位：rad）
    # initial_position = [0.494, 0.191000, 0.424500, -3.141593, 0, -1.570796]
    init = [0.494, 0.191000, 0.424500, -3.141593, 0, -1.570796]
    po = [math.degrees(init[0]), math.degrees(init[1]), math.degrees(init[2]),
          math.degrees(init[3]), math.degrees(init[4]), math.degrees(init[5])]
    # 由于main的初始地址为[0.494, 0.191000, 0.424500, -3.141593, 0, -1.570796]，所以先移动到该位置
    cod.MovJ(po)
    time.sleep(2)
    # 开启实时控制接口（关闭滤波，指令间隔2ms，启动缓冲点数量3个）
    # 指令间隔由RobotController的control_frequency决定 (250hz，4ms)
    # controller = RobotController(UDP_HOST, UDP_PORT, control_frequency=500.0)
    cod.CRIStartControl(filterType=0, duration=4, startBuffer=3)
    time.sleep(2)
    main2()
    time.sleep(2)
    # 关闭实时控制接口
    cod.CRIStopControl()
    time.sleep(2)
    cod.Disconnect()

# 封装好的demo
def demo3():
    # 启动之前先发送打开实时控制接口命令
    cod = Codroid("192.168.1.136", 9001)
    cod.Connect()
    # 指令间隔由RobotController的control_frequency决定 默认1000(默认1000hz，1ms)
    cod.CRIStartControl(filterType=0, duration=1, startBuffer=3)
    time.sleep(2)
    # 或者运行交互式控制
    realtime_ctrl = RealTimeController("127.0.0.1", 8888)
    realtime_ctrl.interactive_control()
    time.sleep(2)
    # 关闭实时控制接口
    cod.CRIStopControl()
    time.sleep(2)
    cod.Disconnect()


if __name__ == "__main__":
    demo1()

