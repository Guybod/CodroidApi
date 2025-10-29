from turtledemo.paint import switchupdown
from Codroid import Codroid
import threading
import time

test_project_ID = "mha5llws0pre1ca6"

cod = Codroid("192.168.1.136",9001)
cod.Connect()
time.sleep(1)
cod.DEBUG = True

projectID = "mha5llws0pre1ca6"
# 2.2.1.1 运行脚本
if 0:
    cod.RunScript(mainProgram="a = a+b \nprint(a)", vars={"a":10,"b":20})

# 2.2.1.2 进入远程脚本模式
if 0:
    cod.EnterRemoteScriptMode()

#2.2.1.3 运行工程
if 0:
    cod.RunProject(projectID)

# 2.2.1.4 单步运行
if 0:
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)
    time.sleep(2)
    cod.RunStep(projectID)

# 2.2.1.5 暂停工程
# 2.2.1.6 恢复运行工程
# 2.2.1.7 停止运行工程
if 0:
    cod.StopProject()
    time.sleep(2)
    cod.RunProject(projectID)
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
    cod.SetBreakpoint(projectID, [5])
    cod.AddBreakpoint(projectID, [6])
    cod.RemoveBreakpoint(projectID,[5])
    cod.ClearBreakpoint()

# 2.2.1.12 设置启动行
if 0:
    cod.StopProject()
    cod.SetStartLine(5)
    cod.RunProject(projectID)
    time.sleep(2)
    cod.StopProject()
    time.sleep(2)
    cod.ClearStartLine()
    cod.RunProject(projectID)
    time.sleep(2)
    cod.StopProject()

# 2.2.2.3 获取全局变量
if 0:
    cod.GetGlobalVars()

# 2.2.2.4 保存全局变量(目前不支持bool变量直接发送)
if 0:
    cod.SetGlobalVar("v990", "100"," ")
    cod.SetGlobalVar("v991", 100," ")
    cod.SetGlobalVar("v992", 90.4," ")
    cod.SetGlobalVar("v993", [1,2,3,4,5]," ")
    cod.SetGlobalVar("v994", {"aaa":100}," ")
    # cod.SetGlobalVar("v995", True," ")

# 2.2.2.5 删除全局变量
if 0:
    cod.RemoveGlobalVars(["v99"])

# 2.2.3.1 获取当前所有工程变量值
if 0:
    cod.GetProjectVars()

if 0:
    cod.SetDO()

cod.Disconnect()