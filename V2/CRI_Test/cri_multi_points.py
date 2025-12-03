import math
import socket
import struct
import time
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
from scipy.interpolate import CubicSpline  # 核心算法库

from Codroid import Codroid


# ==========================================
# 1. 数据结构定义
# ==========================================

class CommandType(Enum):
    """控制模式枚举"""
    JOINT = 0
    END_EFFECTOR = 1


@dataclass
class CommandData:
    """UDP 数据包结构"""
    timestamp: int = 0
    position: List[float] = None
    cmd_type: CommandType = CommandType.JOINT

    def __post_init__(self):
        if self.position is None:
            self.position = [0.0] * 6


# ==========================================
# 2. 运动规划器 (基于 Scipy 三次样条)
# ==========================================

class SplineMotionPlanner:
    """
    负责将离散的关键帧点转换成密集的、平滑的控制指令点。
    使用 Cubic Spline 保证加速度连续。
    """

    def __init__(self, control_frequency: float = 1000.0):
        self.control_frequency = control_frequency
        self.dt = 1.0 / control_frequency

    def generate_trajectory(self, waypoints: List[List[float]], total_duration: float) -> np.ndarray:
        """
        生成平滑轨迹。

        Args:
            waypoints: 关键帧列表 [[j1...j6], [j1...j6], ...]
            total_duration: 总运动时间 (秒)

        Returns:
            numpy array: 形状为 (N, 6) 的密集轨迹点数组
        """
        points = np.array(waypoints)
        n_points, n_dims = points.shape

        if n_points < 2:
            # 如果只有一个点，为了防止报错，生成一段静止的数据
            num_steps = int(total_duration * self.control_frequency)
            return np.tile(points[0], (num_steps, 1))

        # --- 1. 时间轴分配 (Time Allocation) ---
        # 根据每一段的欧氏距离分配时间，防止忽快忽慢
        dists = np.linalg.norm(points[1:] - points[:-1], axis=1)
        total_dist = np.sum(dists)

        if total_dist == 0:
            num_steps = int(total_duration * self.control_frequency)
            return np.tile(points[0], (num_steps, 1))

        # 生成关键帧对应的时间戳 [0, t1, t2, ..., total_duration]
        key_times = np.zeros(n_points)
        accumulated_dist = 0
        for i in range(n_points - 1):
            accumulated_dist += dists[i]
            key_times[i + 1] = (accumulated_dist / total_dist) * total_duration
        key_times[-1] = total_duration  # 修正浮点误差

        # --- 2. 构建样条函数 (Cubic Spline Construction) ---
        # axis=0: 对6个关节独立插值
        # bc_type='clamped': 强制 起点速度=0, 终点速度=0 (静止启停)
        # 这就是实现平滑且加速度连续的核心步骤
        cs = CubicSpline(key_times, points, axis=0, bc_type='clamped')

        # --- 3. 重采样 (Resampling) ---
        # 生成高频控制点 (例如 0s, 0.001s, 0.002s ...)
        num_steps = int(total_duration * self.control_frequency)
        t_eval = np.linspace(0, total_duration, num_steps)

        trajectory = cs(t_eval)  # 计算所有时刻的位置

        return trajectory


# ==========================================
# 3. UDP 通信发送器
# ==========================================

class UDPCommandSender:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def send_command(self, command: CommandData):
        """
        打包并发送数据。结构必须与 C++ 接收端严格一致。
        结构: int64(ts) + 6*double(pos) + uint8(type) + 7*uint8(padding) = 64 bytes
        """
        command.timestamp = self.sequence_number
        self.sequence_number += 1

        # 'q': long long (8 bytes)
        data = struct.pack('q', command.timestamp)

        # 'd': double (8 bytes) * 6
        for pos in command.position:
            data += struct.pack('d', pos)

        # 'B': unsigned char (1 byte)
        data += struct.pack('B', command.cmd_type.value)

        # Padding (7 bytes)
        data += struct.pack('7B', 0, 0, 0, 0, 0, 0, 0)

        try:
            self.sock.sendto(data, (self.host, self.port))
        except OSError as e:
            print(f"发送错误: {e}")

    def close(self):
        self.sock.close()


# ==========================================
# 4. 机器人控制器 (主类)
# ==========================================

class RobotController:
    def __init__(self, udp_host: str, udp_port: int, control_frequency: float = 1000.0):
        self.planner = SplineMotionPlanner(control_frequency)
        self.sender = UDPCommandSender(udp_host, udp_port)
        self.control_frequency = control_frequency
        self.dt = 1.0 / control_frequency
        self.current_position = [0.0] * 6  # 初始状态

    def set_current_position(self, position: List[float]):
        """手动更新当前记录的机械臂位置"""
        if len(position) == 6:
            self.current_position = list(position)

    def move_trajectory(self, waypoints: List[List[float]], duration: float,
                        motion_type: CommandType = CommandType.JOINT):
        """
        执行多点连续轨迹规划与发送
        """
        if len(waypoints) == 0:
            return

        # 1. 路径预处理：将当前位置作为起点加入规划
        # 这样确保机器人从当前状态平滑过渡到轨迹的第一个点
        full_waypoints = [self.current_position] + waypoints

        print(f"[{time.strftime('%H:%M:%S')}] 开始规划... 途径点数: {len(waypoints)}, 预计耗时: {duration}s")

        # 2. 生成密集轨迹
        # start_time_calc = time.time()
        trajectory_np = self.planner.generate_trajectory(full_waypoints, duration)
        # print(f"规划耗时: {(time.time() - start_time_calc)*1000:.2f}ms. 总控制点数: {len(trajectory_np)}")

        # 3. 实时发送循环 (Soft Real-time)
        print(f"[{time.strftime('%H:%M:%S')}] 开始发送轨迹...")

        traj_start_time = time.time()

        for i, point_np in enumerate(trajectory_np):
            # 这里的 point_np 是 numpy array，转为 list
            point_list = point_np.tolist()

            # --- 时间同步补偿 ---
            # 确保循环频率稳定在 1000Hz (或其他设定值)
            expected_time = i * self.dt
            actual_time = time.time() - traj_start_time

            if actual_time < expected_time:
                # 如果代码跑得太快，就睡一会儿
                time.sleep(expected_time - actual_time)

            # --- 发送 ---
            cmd = CommandData(position=point_list, cmd_type=motion_type)
            self.sender.send_command(cmd)

            # 更新内部状态
            self.current_position = point_list

        print(f"[{time.strftime('%H:%M:%S')}] 运动完成.")

    def close(self):
        self.sender.close()


def _parse_line(line):
    """
    内部辅助函数：处理单行文本
    去除方括号、空格，按逗号分割并转为浮点数
    """
    # 去除可能存在的方括号（以防你直接复制了列表字符串）和首尾空格
    clean_line = line.strip().replace('[', '').replace(']', '').replace(' ', '')

    if not clean_line:
        return None

    try:
        # 分割并转为浮点数
        return [float(x) for x in clean_line.split(',') if x]
    except ValueError:
        print(f"警告: 无法解析行 '{line}'，已跳过")
        return None


def remove_consecutive_duplicates(points, tolerance=1e-6):
    """
    辅助函数：去除连续重复的点，防止轨迹规划报错
    """
    if not points:
        return []

    cleaned_points = [points[0]]
    for i in range(1, len(points)):
        # 计算当前点与上一个点的欧氏距离
        dist = np.linalg.norm(np.array(points[i]) - np.array(cleaned_points[-1]))
        if dist > tolerance:
            cleaned_points.append(points[i])

    return cleaned_points


def get_path_degrees(file_path, remove_duplicates=True):
    """
    读取txt文件，返回角度值的二维列表
    :param file_path: 文件路径
    :param remove_duplicates: 是否自动去除连续重复点（建议True）
    :return: List[List[float]]
    """
    path_points = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                point = _parse_line(line)
                if point:
                    path_points.append(point)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return []

    # 去重处理
    if remove_duplicates:
        original_len = len(path_points)
        path_points = remove_consecutive_duplicates(path_points)
        if len(path_points) < original_len:
            print(f"[角度模式] 已自动过滤 {original_len - len(path_points)} 个重复点")

    return path_points


def get_path_radians(file_path, remove_duplicates=True):
    """
    读取txt文件，返回弧度值的二维列表
    :param file_path: 文件路径
    :param remove_duplicates: 是否自动去除连续重复点（建议True）
    :return: List[List[float]]
    """
    # 先获取角度数据（复用上面的逻辑）
    degree_points = get_path_degrees(file_path, remove_duplicates)

    radian_points = []
    for point in degree_points:
        # 将每个轴的角度转换为弧度，并保留4位小数
        # 注意：如果你需要极高精度控制机器人，可以去掉 round(..., 4)
        rad_point = [round(math.radians(angle), 4) for angle in point]
        radian_points.append(rad_point)

    return radian_points


def get_first_point_degrees(file_path):
    """
    读取txt文件的第一行，返回角度值的列表。

    :param file_path: 文件路径
    :return: List[float] 包含6个角度值的列表，如果读取失败则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                # 跳过空行
                clean_line = line.strip()
                if not clean_line:
                    continue

                # 解析第一行非空行
                point = _parse_line(clean_line)
                if point and len(point) == 6:
                    return point
                else:
                    print(f"警告: 第一行数据格式无效或维度不为6: {line}")
                    return None

        print("警告: 文件为空或没有有效数据")
        return None

    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def get_first_point_radians(file_path):
    """
    读取txt文件的第一行，返回弧度值的列表。

    :param file_path: 文件路径
    :return: List[float] 包含6个弧度值的列表，如果读取失败则返回None
    """
    degree_point = get_first_point_degrees(file_path)
    if degree_point is None:
        return None

    # 将角度转换为弧度，保留4位小数
    try:
        radian_point = [round(math.radians(angle), 4) for angle in degree_point]
        return radian_point
    except Exception as e:
        print(f"角度转弧度时发生错误: {e}")
        return None

# ==========================================
# 5. 使用示例 (Main)
# ==========================================

if __name__ == "__main__":

    input_file = "onewPath.txt"

    # 1. 获取角度版本
    degrees = get_path_degrees(input_file)
    # # 打印前2行看看
    # for p in degrees[:2]:
    #     print(p)

    first_degree = get_first_point_degrees(input_file)

    first_radians = get_first_point_radians(input_file)
    # 2. 获取弧度版本
    radians = get_path_radians(input_file)
    # # 打印前2行看看
    # for p in radians[:2]:
    #     print(p)

    # 配置IP
    ROBOT_IP = "192.168.1.136"
    # CRI端口
    CRI_PORT = 9030
    # 远程模式端口
    REMOTE_PORT = 9001

    # 初始化控制器 (100Hz = 10ms 周期)
    controller = RobotController(ROBOT_IP, CRI_PORT, control_frequency=100.0)

    # 初始化Codroid
    cod = Codroid(ROBOT_IP,REMOTE_PORT)
    cod.Connect()
    print("移动至初始点位")
    # 将机械臂移动到初始位置(单位：角度)
    cod.MovJ(first_degree)
    print("已移动到初始点位")
    # 等待机械臂到位
    time.sleep(5)

    print("准备开启实时控制模式")
    # 进入CRI远程控制模式 发送频率10ms,与RobotController初始化频率对应
    cod.CRIStartControl(filterType=0, duration=10, startBuffer=3)
    print("已开启实时控制模式")
    time.sleep(2)

    # 设置当前位置(单位弧度)
    controller.set_current_position(first_radians)
    print("设置初始位置完成")

    # 定义关键帧 (Waypoints) - 单位：弧度
    # 注意：不需要把当前位置放在列表第一个，代码会自动把 current_position 加到开头
    try:
        print("执行运动")
        # 120秒内走完这些点 (算法会自动处理中间的平滑过渡)
        controller.move_trajectory(radians, duration=120)
    except KeyboardInterrupt:
        print("\n用户中断停止.")
    finally:
        controller.close()