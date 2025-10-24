import json
import time
import threading
from Codroid import Codroid
from Define import BaseRegister

test_project_ID = "mh4iixxj0pr135b8"
# test_project_ID = "mh07j4zf0pr8c7e7"

cod = Codroid("192.168.1.136",9001)
cod.connect()
cod.DEBUG = False

# 2.2.1.1运行脚本
if 0:
    cod.runScript("a = a+1 \n print(a)",vars={"a":1,"b":2})

# 2.2.1.2进入远程脚本模式
if 0:
    cod.enterRemoteScriptMode()
# 2.2.1.3运行工程
if 0:
    cod.runProject(test_project_ID)

# 2.2.1.4单步运行
if 0:
    cod.runStep(test_project_ID)

# 2.2.1.5暂停工程
if 0:
    cod.pauseProject()

# 2.2.1.6恢复运行工程
if 0:
    cod.resumeProject()

# 2.2.1.7停止运行工程
if 0:
    od.stopProject()

# 2.2.1.8设置断点(没有效果)
if 0:
    cod.setBreakpoint(test_project_ID,[4,7,10,13,16,19])
    cod.runProject(test_project_ID)

# 2.2.1.9添加断点(没有效果)
if 0:
    cod.addBreakpoint(test_project_ID,[4,7,10,13,16,19])
    cod.runProject(test_project_ID)

# 2.2.1.10删除断点(没有效果)
if 0:
    cod.removeBreakpoint(test_project_ID,[4,7,10,13,16,19])
    cod.runProject(test_project_ID)


# 2.2.1.11清除所有断点(没有效果)
if 0:
    cod.clearBreakpoint()

# 2.2.1.12设置启动行
if 0:
    cod.setStartLine(4)
    cod.runProject(test_project_ID)


# 2.2.1.13清除从指定行运行
if 0:
    cod.clearStartLine()
    cod.runProject(test_project_ID)

# 2.2.2.3获取全局变量
if 0:
    cod.getGlobalVars()

# 2.2.2.4保存全局变量
if 0:
    cod.setGlobalVar("v990",'"test1"')

# 2.2.2.4批量保存全局变量
if 0:
    cod.setGlobalVars([{"name":"v990","value":'"test"'},
                        {"name":"v991","value":'"test2"'}])

# 2.2.2.5删除全局变量
if 0:
    cod.removeGlobalVars(["v","vv"])

# 2.2.3.1获取当前所有工程变量值
if 0:
    cod.runProject(test_project_ID)
    cod.GetProjectVars()

# 2.2.4.1末端485接口初始化
if 0:
    cod.rs485Init()

# 2.2.4.2末端485接口清空缓存
if 0:
    cod.rs485FlushReadBuffer()

# 2.2.4.3末端485接口读取数据
if 0:
    cod.rs485Read(10)

# 2.2.4.4末端485接口写入数据
if 0:
    cod.rs485Write([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a])

# 机器人计算接口
# 2.2.9.1逆解
if 0:
    cod.cpos2apos_mm_deg([-59.835,-666.387,543.916,-143.562,-17.39,-133.945],[0,0,90,0,90,0])

# 2.2.10.1RunTo
# 2.2.10.1.1 goHome
if 0:
    cod.goHome()
    time.sleep(5)

# 2.2.10.1.2 goSafety
if 0:
    cod.goSafety()

# 2.2.10.1.3 goCandle
if 0:
    cod.goCandle()

# 2.2.10.1.4 goPackage
if 0:
    cod.goPackage()

# 2.2.10.1.5 goFaulty
if 0:
   cod.goFaulty()

# 2.2.11.1获取IO值
if 0:
    cod.getDI(0)

if 0:
    cod.getAI(0)

if 0:
    cod.getDO(0)
    cod.setDO(0,1)
    cod.getDO(0)

if 0:
    cod.setAO(0,4.44)

# 2.2.12.1获取寄存器值
if 0:
    cod.getBaseRegisterValue(BaseRegister.majorVersion)

if 0:
    cod.getBoolRegisterValue(9000)
    cod.getBoolRegisterValue(9045)
    cod.setBoolRegisterValue(9045,1)
    cod.getBoolRegisterValue(9045)

if 0:
    cod.getIntRegisterValue(49000)
    # cod.getIntRegisterValue(9045,1)
    # cod.getIntRegisterValue(9045)

# 2.3.1主题订阅接口
if 1:
    def getProjectState_task():
        while True:
            # res = cod.getRobotStates(500)
            # print("RobotStates:=====================================================")
            # Codroid.printSub(res)
            # res = cod.getRobotPosture(500)
            # print("RobotPosture:=====================================================")
            # Codroid.printSub(res)
            # res = cod.getRobotCoordinate(500)
            # print("RobotCoordinate:=====================================================")
            # Codroid.printSub(res)
            res = cod.getLog(500)
            print("Log:=====================================================")
            Codroid.printLog(res)

    timer_thread = threading.Thread(target=getProjectState_task)
    timer_thread.daemon = True  # 设置为守护线程
    timer_thread.start()

    # response = cod.runProject(test_project_ID)
    time.sleep(60)

cod.disConnect()