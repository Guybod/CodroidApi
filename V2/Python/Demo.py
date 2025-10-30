from Codroid import Codroid
import threading
import time
from Define import *

# 车间
# test_project_ID = "mha5llws0pre1ca6"
# 8楼
test_project_ID = "mh4iixxj0pr135b8"

cod = Codroid("192.168.1.136",9001)
cod.Connect()
time.sleep(1)
cod.DEBUG = True

# 2.2.1.1 运行脚本
if 0:
    cod.RunScript(mainProgram="a = a+b \nprint(a)", vars={"a":10,"b":20})

# 2.2.1.2 进入远程脚本模式
if 0:
    cod.EnterRemoteScriptMode()

#2.2.1.3 运行工程
if 0:
    cod.RunProject(test_project_ID)

# 2.2.1.4 单步运行
if 0:
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)
    time.sleep(2)
    cod.RunStep(test_project_ID)

# 2.2.1.5 暂停工程
# 2.2.1.6 恢复运行工程
# 2.2.1.7 停止运行工程
if 0:
    cod.StopProject()
    time.sleep(2)
    cod.RunProject(test_project_ID)
    time.sleep(2)
    cod.PauseProject()
    time.sleep(2)
    cod.ResumeProject()
    time.sleep(2)
    cod.StopProject()
    time.sleep(2)

# 2.2.1.8 设置断点
# 2.2.1.9 添加断点
# 2.2.1.10 删除断点
# 2.2.1.11 清除所有断点
if 0:
    cod.SetBreakpoint(test_project_ID, [5])
    cod.AddBreakpoint(test_project_ID, [6])
    cod.RemoveBreakpoint(test_project_ID,[5])
    cod.ClearBreakpoint()

# 2.2.1.12 设置启动行
if 0:
    cod.StopProject()
    cod.SetStartLine(5)
    cod.RunProject(test_project_ID)
    time.sleep(2)
    cod.StopProject()
    time.sleep(2)
    cod.ClearStartLine()
    cod.RunProject(test_project_ID)
    time.sleep(2)
    cod.StopProject()

# 2.2.2.3 获取全局变量
if 0:
    cod.GetGlobalVars()

# 2.2.2.4 保存全局变量(目前不支持bool变量直接发送)
if 0:
    cod.SetGlobalVar("Test_str", "100000","这是一个字符串")
    # 注意变量名规范，不能以数字开头，不能有特殊字符，不能有空格
    # cod.SetGlobalVar("111Test_str", "100000","这是一个字符串")
    cod.SetGlobalVar("v991", 100)
    cod.SetGlobalVar("v992", 90.4)
    cod.SetGlobalVar("v993", [1,2,3,4,5])
    cod.SetGlobalVar("v994", {"aaa":100})
    # cod.SetGlobalVar("v995", true," ")

# 2.2.2.5 删除全局变量
if 0:
    cod.RemoveGlobalVars(["v99"])

# 2.2.3.1 获取当前所有工程变量值
if 0:
    cod.RunProject(test_project_ID)
    time.sleep(2)
    cod.GetProjectVars()

# 2.2.4.1 485初始化(485功能暂不可用)
if 0:
    cod.RS485Init(9600)
    # 2.2.4.4 485发送数据(485功能暂不可用)
    time.sleep(0.5)
    cod.RS485Write([1,2,3,4,5])
# 2.2.4.2 485清空缓存(485功能暂不可用)
if 0:
    cod.RS485FlushReadBuffer()
# 2.2.4.3 485读取数据(485功能暂不可用)
if 0:
    cod.RS485Read(1,10000)

# 2.2.5.1 ModbusTcp创建设备连接
if 0:
    # 创建设备
    cod.SetModbusTcpDevice("ad","192.168.1.100",502)
    time.sleep(1)
    # 创建设备
    cod.SetModbusTcpDevice("dd","192.168.1.200",502)
    time.sleep(1)
    # 重置设备
    cod.ResetModbusTcpDevice("ad", "192.168.1.150", 502)

# 2.2.5.2 ModbusTcp删除连接设备
if 0:
    cod.RemoveModbusTcpDevice("ad")

# 2.2.5.3创建/修改通信表
if 0:
    # 创建表
    cod.SetModbusTcpTable("dd","a",ModbusTcpFunctionCodeType.ReadHoldingRegisters,0,10,1000)
    # 修改表
    cod.ResetModbusTcpTable("dd","a",ModbusTcpFunctionCodeType.WriteSingleCoil,30,10,1000)
    # 创建表
    cod.SetModbusTcpTable("dd","b",ModbusTcpFunctionCodeType.WriteMultipleHolds,50,10,1000)

# 2.2.5.4删除通信表
if 0:
    cod.RemoveModbusTcpTable("dd","a")

# 2.2.5.5修改表的通信周期
if 0:
    cod.SetModbusTcpPeriod("dd","b",500)

# 2.2.5.6给地址设置别名
if 0:
    cod.SetModbusTcpTableName("dd","b",51,"leo")

# 2.2.5.7给地址段设置数据类型
if 0:
    cod.SetModbusTcpTableType("dd","b",51,ModbusTcpTableType.int16,10)

# 2.2.5.8修改地址的值
if 0:
    cod.SetModbusTcpValue("dd","b",52,100)

# 2.2.5.9获取所有设备配置
if 0:
    cod.GetModbusTcpConfig()

# 2.2.5.10获取所有设备状态
if 0:
    cod.GetModbusTcpState()

# 2.2.5.11获取数据
if 0:
    res:list = cod.GetModbusTcpValue("dd","b")
    print( res)

# 2.2.9.1 逆解(需要连接本体实体)
if 0:
    cpos1 = [927.496,214.506,598.994,180,0,-89.999]
    res1 = cod.IK(cpos1)
    res2 = cod.Cpos2Apos_mm_deg(cpos1)
    cod.PrintResponse(res1)
    cod.PrintResponse(res2)
    # cod.Cpos2Apos_m_rad()

# 2.2.10.1 MoveTo
if 0:
    cod.MoveTo(MoveType.Home)
    i = 1
    while i<10:
        cod.MoveToHeartbeatOnce()
        time.sleep(0.4)
        i+=1

# 2.2.11.2 设置 IO 值(无效)
if 0:
    cod.SetIOValue(
        [{"type":"DO", "port":0, "value":1}]
    )

# 2.2.11.1 获取 IO 值
if 0:
    cod.GetIOValue(
        [{"type":"DI", "port":0},
        {"type":"DO", "port":0}]
    )
    print(cod.GetDI(0))
    print(cod.GetDI(15))
    print(cod.GetDO(0))
    print(cod.GetDO(16))
    print(cod.GetAI(0))
    print(cod.GetAO(0))

# 2.2.12.1 获取寄存器值
if 0:
    cod.GetRegisterValue([41004,41005])

if 0:
    cod.GetBaseRegisterValue(BaseRegister.majorVersion)
    cod.GetBaseRegisterValue(BaseRegister.minorVersion)
    cod.GetBaseRegisterValue(BaseRegister.seconds)
    cod.GetBaseRegisterValue(BaseRegister.milliSeconds)
    cod.GetBaseRegisterValue(BaseRegister.heartBeatToMaster)
    cod.GetBaseRegisterValue(BaseRegister.heartBeatFromMaster)

if 0:
    cod.GetControlRegisterValue(ControlRegister.changeToAuto)
    cod.GetControlRegisterValue(ControlRegister.setAutoMoveRateValue)
    cod.GetControlRegisterValue(ControlRegister.clearWarning)

if 0:
    cod.GetStatusRegisterValue(StatusRegister.isSimulation)

if 0:
    cod.GetMotionInfoRegisterValue(MotionInfoRegister.endPositionA)
    cod.GetMotionInfoRegisterValue(MotionInfoRegister.endPositionZ)

if 0:
    cod.GetIORegisterValue(IORegister.readDIStartPort1)

if 0:
    cod.GetBoolRegisterValue(9000)

if 0:
    cod.GetIntRegisterValue(49000)

if 0:
    cod.GetRealVariableRegister(49200)

# 2.2.12.2 设置寄存器值(无效)
if 0:
    cod.SetRegisterValue(
        [
            {"address":49102, "value":123},
            {"address":49330, "value":12.345}
        ]
    )

if 0:
    cod.SetBoolRegisterValue(9431, 1)

# 2.4.1 工程状态
if 0:
    cod.RunProject(test_project_ID)
    time.sleep(1)
    print(1)
    cod.GetProjectState()
    time.sleep(2)
    print(1)
    cod.PauseProject()
    time.sleep(2)
    print(1)
    cod.GetProjectState()
    time.sleep(3)
    print(1)
    cod.StopProject()
    time.sleep(2)
    print(1)
    cod.GetProjectState()
    time.sleep(2)

# 2.4.2 变量数据
if 0:
    # cod.GetVarUpdate()
    time.sleep(1)
    cod.RunScript(mainProgram="a = a+b \nprint(a)", vars={"a":10,"b":20})
    time.sleep(1)
    cod.GetVarUpdate()
    time.sleep(1)

# 2.4.3 机器人状态
# 2.4.4 机器人位姿
# 2.4.5 机器人坐标系
if 0:
    cod.DEBUG = False
    def robot_state_thread():
        while True:
            res = cod.GetRobotStates()
            cod.PrintSub(res)
            res2 = cod.GetRobotPosture()
            cod.PrintSub(res2)
            time.sleep(0.5)

    t = threading.Thread(target=robot_state_thread, daemon=True)
    t.start()

    cod.RunProject(test_project_ID)

    t.join( )


# 2.4.6 系统日志
if 0:
    cod.DEBUG = False

    def robot_state_thread():
        while True:
            res = cod.GetLog()
            cod.PrintLog(res)
            time.sleep(0.5)

    t = threading.Thread(target=robot_state_thread, daemon=True)
    t.start()
    cod.RunScript(mainProgram="wait(2)\na = a+b \nprint(a)\nwait(2)", vars={"a": 10, "b": 20})
    time.sleep(2)
    cod.RunScript(mainProgram="wait(2)\na = a+b \nprint(a)\nwait(2)", vars={"a": 10, "b": 20})
    time.sleep(2)

# 2.4.7 警告信息

cod.Disconnect()
