import math
import socket
import struct
import time
import numpy as np
from typing import List
from dataclasses import dataclass
from enum import Enum

# 假设这是官方提供的SDK，用于发送非实时指令（如MovJ）和开关实时模式
from Codroid import Codroid


class CommandType(Enum):
    """
    控制模式枚举
    JOINT: 关节空间控制 (直接控制6个关节角度)
    END_EFFECTOR: 末端空间控制 (控制TCP的XYZ和欧拉角/四元数)
    """
    JOINT = 0
    END_EFFECTOR = 1


@dataclass
class CommandData:
    """
    对应C++底层的 CommandData 结构体
    用于定义通过UDP发送的数据包格式
    """
    timestamp: int = 0  # 时间戳或序列号，用于检测丢包或乱序
    position: List[float] = None  # 6个自由度的位置数据 (关节角 或 XYZ+RPY)
    cmd_type: CommandType = CommandType.JOINT  # 指令类型

    def __post_init__(self):
        if self.position is None:
            self.position = [0.0] * 6


class MotionPlanner:
    """
    【运动规划器核心类】
    负责将两个离散的点（起点、终点）“加密”成一串连续的轨迹点。
    """

    def __init__(self, control_frequency: float = 1000.0):
        """
        Args:
            control_frequency: 控制频率(Hz)。例如1000Hz意味着每1ms发送一个点。
        """
        self.control_frequency = control_frequency
        self.dt = 1.0 / control_frequency  # 时间步长 (例如 0.001s)

    def linear_interpolation(self, start_pos: List[float], target_pos: List[float],
                             duration: float) -> List[List[float]]:
        """
        【线性插值算法 (Linear Interpolation)】
        原理： P(t) = P_start + t * (P_end - P_start), 其中 t 从 0 变化到 1。

        特点：
        - 路径是直线。
        - 速度是恒定的（但在起点和终点速度会瞬间突变）。
        - 缺点：加速度在起点和终点理论上无穷大，容易造成机器人抖动或冲击。

        Args:
            start_pos: 起始位置 [6]
            target_pos: 目标位置 [6]
            duration: 运动持续时间(s)
        Returns:
            轨迹点列表 [[J1, J2...J6], [J1, J2...J6], ...]
        """
        # 计算总共需要多少个点 = 时间 * 频率
        num_points = int(duration * self.control_frequency)
        if num_points < 2:
            return [target_pos]

        trajectory = []
        # 使用 numpy 进行向量化计算，提高效率
        start_pos = np.array(start_pos)
        target_pos = np.array(target_pos)

        for i in range(num_points):
            # 归一化时间 t: 范围 [0.0, 1.0]
            t = i / (num_points - 1)
            # 线性插值公式
            point = start_pos + t * (target_pos - start_pos)
            trajectory.append(point.tolist())

        return trajectory

    def cubic_polynomial_interpolation(self, start_pos: List[float], target_pos: List[float],
                                       start_vel: List[float], end_vel: List[float],
                                       duration: float) -> List[List[float]]:
        """
        【三次多项式插值算法 (Cubic Polynomial Interpolation)】
        原理：使用三次多项式 q(t) = a0 + a1*t + a2*t^2 + a3*t^3 来拟合轨迹。

        特点：
        - 可以指定起点和终点的**位置**以及**速度**。
        - 通常将起止速度设为0，这样机器人会“慢进慢出”（S形速度曲线），运动非常平滑。
        - 解决了线性插值起止冲击的问题。

        数学推导 (Hermite插值形式):
        通过求解方程组，可以得到基于归一化时间 t (0~1) 的基函数系数：
        h0 = 2t^3 - 3t^2 + 1       (对应起始位置的权重)
        h1 = t^3 - 2t^2 + t        (对应起始速度的权重)
        h2 = -2t^3 + 3t^2          (对应目标位置的权重)
        h3 = t^3 - t^2             (对应目标速度的权重)

        位置公式: P(t) = h0*P_start + h1*T*V_start + h2*P_end + h3*T*V_end
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
            # 1. 计算归一化时间 t (0 -> 1)
            t = i / (num_points - 1)
            t2 = t * t
            t3 = t2 * t

            # 2. 计算三次多项式的 Hermite 基函数系数
            h0 = 2 * t3 - 3 * t2 + 1
            h1 = t3 - 2 * t2 + t
            h2 = -2 * t3 + 3 * t2
            h3 = t3 - t2

            # 3. 计算当前时刻的位置
            # 注意：速度项需要乘以 duration (总时间 T)，这是因为 t 是归一化的，需要把时间尺度还原
            point = (h0 * start_pos +
                     h1 * duration * start_vel +
                     h2 * target_pos +
                     h3 * duration * end_vel)
            trajectory.append(point.tolist())

        return trajectory


class UDPCommandSender:
    """
    【通信层】
    负责将计算好的 Python 对象打包成 C++ 可识别的二进制数据流并发送。
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def send_command(self, command: CommandData):
        """
        发送二进制数据

        数据包结构 (Struct Packing):
        - q (int64):  timestamp (8 bytes)
        - d (double): position[0] (8 bytes) ... position[5] (8 bytes) -> 共 6*8 = 48 bytes
        - B (uint8):  cmd_type (1 byte)
        - 7个B (uint8): 填充字节 (Padding)，为了内存对齐或保留字段 -> 7 bytes
        总大小: 8 + 48 + 1 + 7 = 64 字节
        """
        # 更新包序号
        command.timestamp = self.sequence_number
        self.sequence_number += 1

        # struct.pack 用于将 Python 类型转换为 C 结构体二进制流
        data = struct.pack('q', command.timestamp)
        for pos in command.position:
            data += struct.pack('d', pos)
        data += struct.pack('B', command.cmd_type.value)
        data += struct.pack('BBBBBBB', 0, 0, 0, 0, 0, 0, 0)  # 补齐位，凑够整数字节

        self.sock.sendto(data, (self.host, self.port))

    def close(self):
        self.sock.close()


class RobotController:
    """
    【控制器主类】
    整合规划和通信，实现“软实时”控制循环。
    """

    def __init__(self, udp_host: str, udp_port: int, control_frequency: float = 1000.0):
        self.planner = MotionPlanner(control_frequency)
        self.sender = UDPCommandSender(udp_host, udp_port)
        self.control_frequency = control_frequency
        self.dt = 1.0 / control_frequency
        self.current_position = [0.0] * 6

    def move_to_target(self, target_position: List[float], duration: float = 3.0,
                       motion_type: CommandType = CommandType.JOINT,
                       use_cubic: bool = False):
        """
        执行运动的核心函数
        """
        print(f"开始规划运动: {self.current_position} -> {target_position}")

        # 1. 轨迹生成 (Offline Planning)
        # 在发送之前，先把所有路径点算出来
        if use_cubic:
            # 设定起止速度为0，保证运动开始和结束时平滑无冲击
            start_vel = [0.0] * 6
            end_vel = [0.0] * 6
            trajectory = self.planner.cubic_polynomial_interpolation(
                self.current_position, target_position, start_vel, end_vel, duration)
        else:
            trajectory = self.planner.linear_interpolation(
                self.current_position, target_position, duration)

        print(f"轨迹生成完毕，点数: {len(trajectory)}，准备发送...")

        # 2. 实时发送循环 (Real-time Loop)
        # 这是软实时系统的关键：必须严格控制循环的时间间隔
        start_time = time.time()

        for i, point in enumerate(trajectory):
            # --- 时间同步与补偿机制 ---
            # 计算从开始到现在实际流逝的时间
            elapsed_time = time.time() - start_time
            # 计算理论上应该流逝的时间 (例如第10个点应该是 10 * dt)
            expected_time = i * self.planner.dt

            # 如果处理太快，实际时间 < 理论时间，则需要睡眠等待 (Sleep)
            if elapsed_time < expected_time:
                time.sleep(expected_time - elapsed_time)
            # 如果处理太慢 (实际时间 > 理论时间)，则不睡眠，立即发送下一个点以追赶进度
            # 注意：如果此处延迟太大，机器人可能会出现顿挫

            # --- 发送指令 ---
            command = CommandData(position=point, cmd_type=motion_type)
            self.sender.send_command(command)

            # 更新内存中的当前位置
            self.current_position = point.copy()

            if i % 50 == 0:
                # 只是为了显示进度，不要每点都打印，否则IO操作会阻塞导致实时性下降
                print(f"进度: {i + 1}/{len(trajectory)}")

        print("运动完成!")

    def move_joints_smoothly(self, target_joints: List[float], duration: float = 3.0):
        """关节空间平滑运动 (推荐)"""
        self.move_to_target(target_joints, duration, CommandType.JOINT, use_cubic=True)

    def move_cart_smoothly(self, target_joints: List[float], duration: float = 3.0):
        """末端空间平滑运动 (直线运动)"""
        # 注意：这里的 target_joints 变量名可能有歧义，在 Cartesian 模式下通常代表 XYZ+RPY
        self.move_to_target(target_joints, duration, CommandType.END_EFFECTOR, use_cubic=True)

    def set_current_position(self, position: List[float]):
        """初始化当前位置，避免第一次规划时从0开始乱飞"""
        if len(position) == 6:
            self.current_position = position.copy()
        else:
            raise ValueError("位置数组必须包含6个元素")

    def close(self):
        self.sender.close()


# --- 业务逻辑 Demo ---

def demo1():
    print("=== Demo 1: 关节空间平滑运动 ===")
    UDP_HOST = "192.168.1.136"
    UDP_PORT = 9030  # 实时控制端口

    # 1. 连接机器人管理接口 (非实时，用于配置)
    cod = Codroid("192.168.1.136", 9001)
    cod.Connect()

    # 2. 移动到初始姿态 (使用指令式移动，非实时)
    # 这一步很重要，确保物理机器人和代码中的 current_position 一致
    init_pos_deg = [0, 0, 90, 0, 0, 0]  # 角度制
    cod.MovJ(init_pos_deg)
    time.sleep(3)  # 等待物理运动到位

    # 3. 开启实时控制模式
    # filterType=0: 关闭内部滤波 (完全信任外部指令)
    # duration=2: 期望的数据包间隔 (ms)，对应频率 500Hz
    # startBuffer=3: 缓冲3个点后开始运动，防止网络抖动
    cod.CRIStartControl(filterType=0, duration=2, startBuffer=3)
    time.sleep(1)  # 等待模式切换

    # 4. 创建实时控制器 (频率必须与 duration=2ms 对应，即 500Hz)
    controller = RobotController(UDP_HOST, UDP_PORT, control_frequency=500.0)

    # 将内部状态设为初始位置 (注意单位转换：角度 -> 弧度)
    # [0, 0, 90, 0, 0, 0] -> [0, 0, 1.57, 0, 0, 0]
    init_pos_rad = [math.radians(x) for x in init_pos_deg]
    controller.set_current_position(init_pos_rad)

    try:
        # 定义目标点 (弧度)
        target1 = [0.5, -0.3, 1.0, 0.2, -0.4, 0.1]

        # 执行平滑运动
        # 代码内部会生成 500Hz * 4s = 2000 个点，并通过UDP发过去
        controller.move_joints_smoothly(target1, duration=4.0)

        # 再回到原点
        time.sleep(1)
        controller.move_joints_smoothly(init_pos_rad, duration=4.0)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 5. 清理工作
        controller.close()  # 关闭UDP Socket
        cod.CRIStopControl()  # 告诉机器人退出实时模式
        time.sleep(1)
        cod.Disconnect()  # 断开管理连接


if __name__ == "__main__":
    demo1()