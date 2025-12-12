import json
import struct
import numpy as np
import toppra as ta
import toppra.constraint as constraint
import toppra.algorithm as algo
import os
from enum import Enum
from dataclasses import dataclass
from typing import List
import socket
import threading
import time
import traceback

# 假设 Codroid 在同级目录下，如果报错请确保文件存在
from Codroid import Codroid


# ==========================================
# 1. 基础数据结构与 UDP 发送类
# ==========================================
class CommandType(Enum):
    JOINT = 0
    END_EFFECTOR = 1


@dataclass
class CommandData:
    timestamp: int = 0
    position: List[float] = None
    cmd_type: CommandType = CommandType.JOINT

    def __post_init__(self):
        if self.position is None:
            self.position = [0.0] * 6


class UDPCommandSender:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def send_command(self, command: CommandData):
        command.timestamp = self.sequence_number
        self.sequence_number += 1

        if len(command.position) != 6:
            print(f"错误: 关节数据长度应为6")
            return

        try:
            payload = struct.pack('<q6dB7x',
                                  command.timestamp,
                                  *command.position,
                                  command.cmd_type.value)
            self.sock.sendto(payload, (self.host, self.port))
        except struct.error as e:
            print(f"打包失败: {e}")

    def close(self):
        self.sock.close()


# ==========================================
# 2. Toppra 规划器
# ==========================================
class TrajectoryPlanner:
    def __init__(self, target_freq=100.0):
        self.target_freq = target_freq
        self.dt = 1.0 / target_freq
        self.dof = 6
        self.v_max = np.array([0.8] * self.dof)
        self.a_max = np.array([1.2] * self.dof)

    def plan(self, waypoints_deg: List[List[float]]) -> List[List[float]]:
        if not waypoints_deg or len(waypoints_deg) < 2:
            print("错误: 至少需要两个点才能规划轨迹")
            return []

        raw_np = np.array(waypoints_deg)
        diffs = np.linalg.norm(np.diff(raw_np, axis=0), axis=1)
        keep_mask = np.concatenate(([True], diffs > 1e-4))
        clean_waypoints = raw_np[keep_mask]

        if len(clean_waypoints) < 2:
            print("错误: 去重后点数不足。")
            return []

        waypoints_rad = np.deg2rad(clean_waypoints)

        try:
            path = ta.SplineInterpolator(np.linspace(0, 1, len(waypoints_rad)), waypoints_rad)
        except Exception as e:
            print(f"Spline插值失败: {e}")
            return []

        pc_vel = constraint.JointVelocityConstraint(self.v_max)
        pc_acc = constraint.JointAccelerationConstraint(self.a_max)

        num_grid_points = max(100, len(waypoints_rad) * 2)
        grid_array = np.linspace(0, path.duration, num_grid_points)

        try:
            instance = algo.TOPPRA([pc_vel, pc_acc], path, solver_wrapper='seidel', gridpoints=grid_array)
            jnt_traj = instance.compute_trajectory()
        except Exception as e:
            print(f"Toppra 求解崩溃: {e}")
            return []

        if jnt_traj is None:
            print("规划失败！无法找到满足约束的轨迹。")
            return []

        duration = jnt_traj.duration
        print(f"规划成功! 预计总耗时: {duration:.4f} 秒")

        t_samples = np.arange(0, duration, self.dt)
        if t_samples[-1] < duration:
            t_samples = np.append(t_samples, duration)

        interpolated_rad = jnt_traj(t_samples)
        return interpolated_rad.tolist()


# ==========================================
# 3. 订阅客户端 (TCP)
# ==========================================
class SubscriptionClient(threading.Thread):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.sock = None
        self.running = False
        self.daemon = True  # 【修改】设置为守护线程，主程序退出时它会自动退出

        self.sub_msg = "{\"ty\": \"publish/RobotPosture\",\"tc\": 10}"
        self.trigger_cmd1 = "{\"id\": 1,\"ty\": \"IOManager/SetIOValue\",\"db\": {\"type\": \"DO\", \"port\": 0, \"value\": 1}}"
        self.trigger_cmd0 = "{\"id\": 1,\"ty\": \"IOManager/SetIOValue\",\"db\": {\"type\": \"DO\", \"port\": 0, \"value\": 0}}"

    def run(self):
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(None)
            self.sock.connect((self.ip, self.port))
            print(f"[TCP客户端] 已连接服务器 {self.ip}:{self.port}")

            print(f"[TCP客户端] 发送订阅: {self.sub_msg}")
            self.sock.sendall(self.sub_msg.encode('utf-8'))

            while self.running:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        print("[TCP客户端] 服务器断开连接")
                        break

                    msg_str = data.decode('utf-8', errors='ignore').strip()
                    if not msg_str: continue

                    # 【修改】简单的防崩处理
                    try:
                        # 尝试处理粘包（如果不严重）或单包
                        # 这里做一个简单的处理，只取最后一条完整json（如果粘包严重需重写Buffer逻辑）
                        if msg_str.count('}{') > 0:
                            # 简单的分割逻辑，取最后一个完整的
                            msg_str = "{" + msg_str.split('}{')[-1]

                        msg = json.loads(msg_str)

                        # 【修改】安全检查：防止 'NoneType' 报错
                        db_data = msg.get("db")
                        if db_data is None:
                            # 收到心跳包或无数据包，跳过
                            continue

                        joint_data = db_data.get("joint")
                        if joint_data:
                            # print(f"Current: {joint_data}") # 调试用
                            self.check_and_trigger(joint_data)

                    except json.JSONDecodeError:
                        # print("JSON解析错误，跳过坏包")
                        pass
                    except Exception as e:
                        print(f"处理逻辑异常: {e}")

                except socket.error as e:
                    print(f"[TCP客户端] 连接错误: {e}")
                    break
        except Exception as e:
            print(f"[TCP客户端] 致命错误: {e}")
        finally:
            self.close_connection()

    def check_and_trigger(self, msg: list):
        threshold = 0.2
        target_configs = [
            ([88.09, 27.46, 94.54, 56.53, 90.21, 122.65], 1),
            ([56.64, 95.25, 59.18, 23.85, 58.77, 172.33], 0),
            ([56.93, 91.41, 63.64, 23.23, 59.06, 171.61], 1),
            ([91.45, 33.37, 83.05, 62.10, 93.57, 121.91], 0),
            ([89.13, 33.56, 84.90, 60.07, 91.25, 122.62], 1),
            ([59.69, 99.80, 46.75, 31.78, 61.80, 172.78], 0),
            ([59.97, 95.61, 52.03, 30.69, 62.08, 172.02], 1),
            ([92.15, 39.64, 73.37, 65.54, 94.07, 120.33], 0),
            ([89.86, 39.68, 75.37, 63.50, 91.78, 121.21], 1),
            ([61.70, 106.43, 28.89, 43.16, 63.01, 173.60], 0),
            ([61.95, 101.13, 36.50, 40.85, 63.27, 172.71], 1),
            ([91.47, 43.87, 65.31, 69.46, 92.78, 123.22], 0),
        ]

        def is_close(curr, target):
            if not curr or len(curr) != len(target): return False
            for a, b in zip(curr, target):
                if abs(a - b) > threshold: return False
            return True

        matched_cmd_id = None
        for target_pos, cmd_id in target_configs:
            if is_close(msg, target_pos):
                matched_cmd_id = cmd_id
                break

        if matched_cmd_id is not None:
            try:
                if matched_cmd_id == 1:
                    print(f"--> [触发] 动作1，发送IO开")
                    self.sock.sendall(self.trigger_cmd1.encode('utf-8'))
                else:
                    print(f"--> [触发] 动作0，发送IO关")
                    self.sock.sendall(self.trigger_cmd0.encode('utf-8'))
            except Exception as e:
                print(f"触发指令发送失败: {e}")

    def close_connection(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

    def stop(self):
        self.running = False
        self.close_connection()


# ==========================================
# 4. 主控制流程
# ==========================================
def main():
    # 配置
    IP = "192.168.1.136"
    PORT_UDP = 9030
    PORT_TCP = 9001
    FREQ = 100.0
    FILE_PATH = "joint.txt"

    # --- 【重要修改】 线程启动逻辑 ---
    print("正在启动 TCP 订阅线程...")
    sub = SubscriptionClient(IP, PORT_TCP)
    sub.start()  # 必须用 start()，不能用 run()！
    # 注意：这里删除了原来重复定义的 sub = ... sub.run()

    # 稍等一下让连接建立
    time.sleep(1)

    # 连接机器人控制接口
    print("正在连接机器人控制接口...")
    try:
        cod = Codroid(IP, PORT_TCP)
        cod.Connect()
        print("机器人控制接口已连接")

        # 启动外部控制模式
        print("发送 StartControl 指令...")
        cod.CRIStartControl(filterType=0, duration=int(1000 / FREQ), startBuffer=10)
    except Exception as e:
        print(f"机器人连接失败: {e}")
        sub.stop()
        return

    # 初始化规划和发送器
    sender = UDPCommandSender(IP, PORT_UDP)
    planner = TrajectoryPlanner(target_freq=FREQ)

    # 读取文件
    raw_waypoints = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    parts = [float(x) for x in line.split(',')]
                    if len(parts) == 6:
                        raw_waypoints.append(parts)
                except ValueError:
                    pass
    else:
        print(f"找不到文件 {FILE_PATH}")
        sub.stop()
        return

    # 规划
    print("开始规划轨迹...")
    try:
        smooth_trajectory = planner.plan(raw_waypoints)
    except Exception as e:
        traceback.print_exc()
        sub.stop()
        return

    if not smooth_trajectory:
        print("轨迹为空，终止。")
        sub.stop()
        return

    # 播放
    print(f"规划完成，共 {len(smooth_trajectory)} 个点。")
    print(">>> 请确保机器人处于初始位置，否则会引起关节速度突变 <<<")
    print(">>> 初始关节角度应该为[0.00,-25.00,155.00,-43.00,-3.00,181.00] <<<")
    print(">>> 按回车键开始播放运动 <<<")
    input()

    start_time = time.perf_counter()
    dt = 0.01  # 10ms

    try:
        print("开始发送 UDP 数据...")
        for i, pos in enumerate(smooth_trajectory):
            sender.send_command(CommandData(position=pos))

            # 简单的延时控制 (Soft Real-time)
            target = start_time + (i + 1) * dt
            remain = target - time.perf_counter()
            if remain > 0:
                time.sleep(remain)

            if i % 100 == 0:
                print(f"进度: {i}/{len(smooth_trajectory)}")

        print("运动结束。")

    except KeyboardInterrupt:
        print("用户强制停止")
    except Exception as e:
        print(f"运行时错误: {e}")
    finally:
        sender.close()
        sub.stop()  # 停止 TCP 线程
        print("程序退出")


if __name__ == "__main__":
    main()