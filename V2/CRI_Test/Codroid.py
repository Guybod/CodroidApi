# codroidSDK

# 导入所需的标准库和自定义模块
import json, math, time
from TcpClient import TCPClient
from json import JSONDecodeError, JSONDecoder
from typing import Union
from Define import *

class Codroid:
    """
    Codroid机器人控制类
    提供与Codroid机器人通信和控制的接口
    """
    # 保留字
    reserved_words = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if", "in",
                      "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while", "table",
                      "math",
                      "DO", "DOGroup", "DIO", "DIOGroup", "AO", "AIO", "ModbusTCP", "setSpeedJ", "setAccJ",
                      "setSpeedL", "setAccL", "setBlender",
                      "setMoveRate", "getCoor", "getTool", "setCoor", "editCoor", "setTool", "editTool",
                      "setPayload", "enableVibrationSuppression", "disableVibrationSuppression",
                      "setCollisionDetectionSensitivity", "initComplianceControl", "enableComplianceControl",
                      "disableComplianceControl", "forceControlZeroCalibrate", "setFilterPeriod",
                      "searchSuccessed", "getJoint", "getTCP", "getCoor", "getTool", "aposToCpos", "cposToApos",
                      "cposToCpos", "posOffset", "posTrans", "coorRel", "toolRel", "getJointTorque",
                      "getJointExternalTorque", "createTray", "getTrayPos", "posInverse", "distance", "interPos",
                      "planeTrans", "getTrajStart", "getTrajEnd", "arrayAdd", "arraySub",
                      "coorTrans", "movJ", "movL", "movC", "movCircle", "movLW", "movCW", "movTraj", "setWeave",
                      "weaveStart", "weaveEnd", "setDO", "getDI", "getDO", "setDOGroup", "getDIGroup",
                      "getDOGroup", "setAO", "getAI", "getAO", "getRegisterBool", "setRegisterBool",
                      "getRegisterInt", "setRegisterInt", "getRegisterFloat", "setRegisterFloat", "RS485init",
                      "RS485flush", "RS485write", "RS485read",
                      "readCoils", "readDiscreteInputs", "readHoldingRegisters", "readInputRegisters",
                      "writeSingleCoil", "writeSingleRegister", "writeMultipleCoils",
                      "writeMultipleRegisters", "createSocketClient", "connectSocketClient", "writeSocketClient",
                      "readSocketClient", "closeSocketClient", "wait", "waitCondition", "systemTime", "stopProject",
                      "pauseProject", "runScript", "pauseScript", "resumeScript", "stopScript", "callModule",
                      "print", "setInterruptInterval", "setInterruptCondition", "clearInterrupt", "strcmp",
                      "strToNumberArray", "arrayToStr",
                      "enableMultiWeld", "getCurSeam", "isMultiWeldFinished", "setMultiWeldOffset", "weldNextSeam",
                      "resetMultiWeld", "searchStart", "setMasterFlag", "getOffsetValue", "search", "searchEnd",
                      "searchOffset", "searchOffsetEnd", "searchError"}

    def __init__(self, ip, port):
        """
        初始化Codroid对象
        
        参数:
            ip (str): 机器人控制器的IP地址
            port (int): 机器人控制器的端口号
        """
        self.heartbeat_thread = None
        self.ip = ip
        self.port = port
        self.client = TCPClient(ip,port)
        self.DEBUG = False
        self.isConnected = False
        self.default_timeout = 5.0 # 默认超时时间（秒）

    def Connect(self):
        """建立与Codroid机器人的连接"""
        try:
            self.client.connect()
            self.isConnected = True
        except Exception as e:
            print(e)

    def Disconnect(self):
        """断开与Codroid的连接"""
        try:
            self.client.disconnect()
            self.isConnected = False
        except Exception as e:
            print(e)

    @staticmethod
    def __convert_to_db_format(variables):
        """
        将变量字典列表转换为db格式
        
        参数:
            variables: 包含name、val和nm字段的字典列表
            
        返回值:
            dict: 转换后的db格式字典
        """
        db_format = {}
        for var in variables:
            name = var["name"]
            db_format[name] = {
                "val": var.get("value", ""),
                "nm": var.get("nm", "")
            }
        return db_format

    @staticmethod
    def PrintResponse(response: json):
        """
        打印完整的响应信息
        
        参数:
            response (json): 从机器人接收到的JSON响应
        """
        if response is None:
            print("response is None")
            return
        if "id" in response:
            print(f'id : {response["id"]}')
        else:
            print(f"id : None")
        if "ty" in response:
            print(f'ty : {response["ty"]}')
        else:
            print(f"ty : None")
        if "db" in response:
            print(f'db : {response["db"]}')
        else:
            print(f"db : None")
        if "err" in response:
            print(f'err : {response["err"]}')
        else:
            print(f"err : None")

    @staticmethod
    def PrintSub(response: json):
        """
        打印子响应信息（不包含id和err字段）
        
        参数:
            response (json): 从机器人接收到的JSON响应
        """
        if response is None:
            print("response is None")
            return
        if "ty" in response:
            print(f'ty : {response["ty"]}')
        else:
            print(f"ty : None")
        if "db" in response:
            print(f'db : {response["db"]}')
        else:
            print(f"db : None")

    @staticmethod
    def PrintLog(response: json):
        """
        打印日志信息
        
        参数:
            response (json): 从机器人接收到的JSON响应
        """
        if response is None:
            print("response is None")
            return
        if "ty" in response:
            print(f'ty : {response["ty"]}')
        else:
            print(f"ty : None")
        if "db" in response:
            try:
                time_tuple = time.localtime(int(response["db"][0][2]))
                time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
                typecode = response["db"][0][0]
                errcode = response["db"][0][1]
                msg = response["db"][0][3]
                print(f"时间: {time_formatted}, 消息类型: {Typecode.getTypeName(typecode)}, 错误码: {errcode}, 消息: {msg} ")
            except Exception as e:
                print(f"time: {e}")
        else:
            print(f"db : None")

    @staticmethod
    # 检查JSON数据中嵌套键是否存在
    def __has_deviceName(json_data:json, devicename:str)-> bool:
        """
        检查JSON数据中嵌套键是否存在

        参数:
            json_data: JSON数据（字符串或字典）
            devicename: 设备名

        返回:
            bool: 如果父子键都存在返回True，否则返回False
        """
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                return False
        else:
            data = json_data

        # 检查父键存在且是字典，然后检查子键[6](@ref)
        return ("db" in data and
                isinstance(data["db"], dict) and
                devicename in data["db"])

    @staticmethod
    # 验证变量名
    def __is_valid_variable_name(name: str) -> bool:
        """验证变量名格式"""
        if not name or not isinstance(name, str):
            return False

        # 变量名必须以字母或下划线开头[3](@ref)
        if not name[0].isalpha() and name[0] != '_':
            return False

        # 变量名只能包含字母、数字、下划线[3](@ref)
        if not all(c.isalnum() or c == '_' for c in name):
            return False

        return name not in Codroid.reserved_words

    @staticmethod
    # 处理全局变量输入值
    def __process_value_based_on_type(value):
        """根据值类型进行特定处理"""
        if isinstance(value, str):
            # 字符串类型处理
            return f"\"{value}\""
        elif isinstance(value, (int, float)):
            # 数值类型处理
            return str(value)# 统一转为float
        # elif isinstance(value, bool):
        #     # 布尔类型处理
        #     if value:
        #         return 'true'
        #     else:
        #         return 'false'
        elif isinstance(value, dict):
            # 复杂类型处理
            return json.dumps(value)
        elif isinstance(value, list):
            # 列表类型处理
            return str(value)
        else:
            raise TypeError(f"不支持的值类型: {type(value)}")

    @staticmethod
    def __has_tableName(json_data: json, devicename:str,tableName: str) -> bool:
        """
        检查JSON数据中是否存在指定的键

        参数:
            json_data: JSON数据（可以是字符串或字典）
            target_key: 要查找的键名（如"a"或"b"）

        返回:
            bool: 如果键存在返回True，否则返回False
        """
        # 检查db键是否存在且是字典
        db_data = json_data.get("db")
        if not isinstance(db_data, dict):
            return False
        # 检查dd键是否存在且是字典
        dd_data = db_data.get(devicename)
        if not isinstance(dd_data, dict):
            return False

        # 检查tables键是否存在且是字典
        tables_data = dd_data.get("tables")
        if not isinstance(tables_data, dict):
            return False

        # 检查目标键是否存在于tables中
        return tableName in tables_data

    def _safe_parse_response(self,response: str):
        """
        尝试安全解析 response:
        1) 先用 self._safe_parse_response 解析全部
        2) 失败时用 JSONDecoder.raw_decode 解析第一个 JSON 对象并返回
        """
        if response is None:
            return None
        try:
            return json.loads(response)
        except JSONDecodeError:
            try:
                decoder = JSONDecoder()
                obj, idx = decoder.raw_decode(response)
                return obj
            except JSONDecodeError:
                # 最后回退：取首行再尝试解析（若返回中带有日志等）
                first = response.splitlines()[0].strip()
                return json.loads(first)
    
    
    # 2.2.1.1 运行脚本
    def RunScript(self, mainProgram: str, subThreadsName: str = None, subThreads: str = None,
                  subProgramsName: str = None, subPrograms: str = None, interruptsName: str = None, 
                  interrupts: str = None, vars: dict = None, id :int = 1) -> json:
        """
        运行脚本函数
        
        参数:
            mainProgram (str): 主程序代码，不能为空
            subThreadsName (str, optional): 子线程名称
            subThreads (str, optional): 子线程程序代码
            subProgramsName (str, optional): 子程序名称
            subPrograms (str, optional): 子程序代码
            interruptsName (str, optional): 中断处理程序名称
            interrupts (str, optional): 中断处理程序代码
            vars (dict, optional): 脚本运行时变量字典
            id (int, optional): 请求ID，默认为1
            
        返回值:
            json: 脚本执行结果的JSON响应
        """
        if mainProgram is None:
            raise Exception("主程序不能为空")
        if vars is None:
            vars = {}
        
        # 构建消息字典，包含脚本信息和变量
        message_dict = {
            "id": id,
            "ty": "project/runScript",
            "db": {
                "scripts": {
                    "main": mainProgram,
                },
                "vars": vars
            }
        }
        
        # 添加子线程脚本（如果提供）
        if subThreadsName is not None and subThreads is not None:
            message_dict["db"]["scripts"]["subThreads"] = {
                subThreadsName: subThreads
            }
            
        # 添加子程序脚本（如果提供）
        if subProgramsName is not None and subPrograms is not None:
            message_dict["db"]["scripts"]["subPrograms"] = {
                subProgramsName: subPrograms
            }
            
        # 添加中断处理脚本（如果提供）
        if interruptsName is not None and interrupts is not None:
            message_dict["db"]["scripts"]["interrupts"] = {
                interruptsName: interrupts
            }

        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.2 进入远程脚本模式
    def EnterRemoteScriptMode(self, id :int = 1) -> json:
        """
        进入远程脚本模式
        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 模式切换命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/enterRemoteScriptMode"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.3 运行工程
    def RunProject(self, project_id: str, id :int = 1) -> json:
        """
        运行指定项目

        参数:
            id (int, optional): 请求ID，默认为1
            project_id (str): 项目ID

        返回值:
            json: 运行命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/run",
            "db": {
                "id": project_id
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4 通过工程映射启动程序
    def RunProjectByIndex(self, index:int ,id :int = 1) -> json:
        """
        运行指定项目

        参数:
            id (int, optional): 请求ID，默认为1
            index (int): 索引号

        返回值:
            json: 运行命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/runByIndex",
            "db": index
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.4 单步运行
    def RunStep(self, project_id: str ,id :int = 1) -> json:
        """
        单步运行指定项目

        参数:
            id (int, optional): 请求ID，默认为1
            project_id (str): 项目ID

        返回值:
            json: 单步运行命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/runStep",
            "db": {
                "id": project_id
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.5 暂停工程
    def PauseProject(self, id :int = 1) -> json:
        """
        暂停项目执行
        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 暂停命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/pause"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.6 恢复运行工程
    def ResumeProject(self, id :int = 1) -> json:
        """
        恢复项目执行
        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 恢复命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/resume"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.7 停止运行工程
    def StopProject(self, id :int = 1) -> json:
        """
        停止项目执行
        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 停止命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/stop"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.8 设置断点
    def SetBreakpoint(self, project_id: str, line_number: list, id :int = 1):
        """
        设置断点

        参数:
            id (int, optional): 请求ID，默认为1
            project_id (str): 项目ID
            line_number (list): 断点行号列表

        返回值:
            json: 设置断点命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/setBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.9 添加断点
    def AddBreakpoint(self, project_id: str, line_number: list[int], id :int = 1):
        """
        添加断点

        参数:
            id (int, optional): 请求ID，默认为1
            project_id (str): 项目ID
            line_number (list): 要添加的断点行号列表

        返回值:
            json: 添加断点命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/addBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.10 删除断点
    def RemoveBreakpoint(self, project_id: str, line_number: list[int], id :int = 1):
        """
        移除断点

        参数:
            id (int, optional): 请求ID，默认为1
            project_id (str): 项目ID
            line_number (list): 要移除的断点行号列表

        返回值:
            json: 移除断点命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/removeBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.11 清除所有断点
    def ClearBreakpoint(self, id :int = 1):
        """
        清除所有断点
        参数:
             id (int, optional): 请求ID，默认为1
        返回值:
            json: 清除断点命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/clearBreakpoint",
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.12 设置启动行
    def SetStartLine(self, start_line: int, id :int = 1):
        """
        设置起始行

        参数:
            id (int, optional): 请求ID，默认为1
            start_line (int): 起始行号

        返回值:
            json: 设置起始行命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/setStartLine",
            "db": start_line
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.1.13 清除从指定行运行
    def ClearStartLine(self, id :int = 1):
        """
        清除起始行设置

        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 清除起始行命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "project/clearStartLine"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.2.3 获取全局变量
    def GetGlobalVars(self, id :int = 1) -> json:
        """
        获取全局变量
        参数:
            id (int, optional): 请求ID，默认为1
        返回值:
            json: 全局变量信息
        """
        message_dict = {
            "id": id,
            "ty": "globalVar/getVars"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.2.4 保存全局变量
    def SetGlobalVar(self, name: str, value: Union[str, float, dict, list], note: str = " ",id :int = 1) -> dict:
        """
        设置单个全局变量 - 统一实现

        参数:
            id (int, optional): 请求ID，默认为1
            name (str): 变量名
            value: 变量值（支持多种类型）
            note (str): 变量备注

        返回值:
            dict: 设置命令的响应结果
        """
        # 验证变量名格式
        if not self.__is_valid_variable_name(name):
            raise ValueError(f"无效的变量名: {name}")

        # 根据类型进行特定处理
        processed_value = self.__process_value_based_on_type(value)

        message_dict = {
            "id": id,
            "ty": "globalVar/saveVars",
            "db": {
                name: {
                    "val": processed_value,
                    "nm": note
                }
            }
        }

        message_str = json.dumps(message_dict, ensure_ascii=False)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.2.4 保存全局变量
    def __SetGlobalVars(self, value: list, id: int = 1) -> json:
        """
        批量设置全局变量

        参数:
            id (int, optional): 请求ID，默认为1
            value: 变量名和值的列表，每个元素是包含name和value的字典
            {变量名1": {"nm": "变量备注1", "val": "变量值1"},变量名2": {"nm": "变量备注2", "val": "变量值2"}}
        返回值:
            json: 批量设置命令的响应结果
        """
        format_value = self.__convert_to_db_format(value)
        message_dict = {
            "id": id,
            "ty": "globalVar/saveVars",
            "db": format_value
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.2.5 删除全局变量
    def RemoveGlobalVars(self, value_name: list, id: int = 1) -> json:
        """
        批量删除全局变量

        参数:
            value_name: 要删除的变量名列表
            ["变量名 1", "变量名 2"]
        返回值:
            json: 删除命令的响应结果
        """
        message_dict = {
            "id": id,
            "ty": "globalVar/removeVars",
            "db": value_name
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.3.1 获取当前所有工程变量值
    def GetProjectVars(self) -> json:
        """
        获取项目变量

        返回值:
            json: 项目变量信息
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "globalVar/GetProjectVarUpdate"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.4.1 485初始化
    def RS485Init(self, baud_rate: int = 115200, stop_bit: int = 1, data_bit: int = 8, parity: int = 0):
        """
        初始化RS485通信参数

        参数:
            baud_rate (int): 波特率，默认115200
            stop_bit (int): 停止位，默认1
            data_bit (int): 数据位，默认8
            parity (int): 校验位，0-无校验，1-奇校验，2-偶校验 默认0

        返回值:
            json: 初始化命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/init",
            "db": {
                "baudrate": baud_rate,
                "stopBit": stop_bit,
                "dataBit": data_bit,
                "parity": parity
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.4.2 485清空缓存
    def RS485FlushReadBuffer(self):
        """
        清空RS485读缓冲区

        返回值:
            json: 清空缓冲区命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/flushReadBuffer"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.4.3 485读取数据
    def RS485Read(self, length: int, timeout: int = 3000):
        """
        从RS485读取数据

        参数:
            length (int): 要读取的数据长度
            timeout (int): 超时时间（毫秒），默认3000

        返回值:
            json: 读取数据命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/read",
            "db": {
                "length": length,
                "timeout": timeout
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str)
        return json.loads(response)

    # 2.2.4.4 485发送数据
    def RS485Write(self, data: list[int] ):
        """
        向RS485写入数据

        参数:
            data (list[int]): 要写入的数据列表

        返回值:
            json: 写入数据命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/write",
            "db": data
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.1 ModbusTcp创建设备连接
    def SetModbusTcpDevice(self,devicename: str, ip: str, port: int,slavedId: int = 1,endian:int = 1):
        """
            创建Tcp设备

            参数:
                devicename (str): 设备名称,唯一值
                ip (str): 设备IP地址
                port (int): 设备端口号
                slavedId (int): 从机地址
                endian (int): 字节序：1-大端，2-小端，默认1

            返回值:
                json: 写入数据命令的响应结果
        """
        if self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备名称已存在: {devicename},修改请使用Reset")

        if not self.__is_valid_variable_name(devicename):
            raise ValueError(f"无效的变量名: {devicename}")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setDevice",
            "db": {
                "name": devicename,
                "ip": ip,
                "port": port,
                "slaveId": slavedId,
                "endian": endian
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.1 ModbusTcp创建设备连接
    def ResetModbusTcpDevice(self,devicename: str, ip: str, port: int,slavedId: int = 1,endian:int = 1):
        """
            创建Tcp设备

            参数:
                devicename (str): 设备名称,唯一值
                ip (str): 设备IP地址
                port (int): 设备端口号
                slavedId (int): 从机地址
                endian (int): 字节序：1-大端，2-小端，默认1

            返回值:
                json: 写入数据命令的响应结果
        """
        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备名称不存在: {devicename},请使用Set")

        if not self.__is_valid_variable_name(devicename):
            raise ValueError(f"无效的变量名: {devicename}")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setDevice",
            "db": {
                "name": devicename,
                "ip": ip,
                "port": port,
                "slaveId": slavedId,
                "endian": endian
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.2 ModbusTcp删除连接设备
    def RemoveModbusTcpDevice(self,devicename: str):
        """
            创建Tcp设备

            参数:
                devicename (str): 设备名称,唯一值

            返回值:
                json: 写入数据命令的响应结果
        """
        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/removeDevice",
            "db": {
                "name": devicename
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.3 创建/修改通信表
    def SetModbusTcpTable(self,devicename: str,tablename:str,functionCode: ModbusTcpFunctionCodeType,address: int,length: int,period: int = 1000):
        """
        设置Modbus TCP通信表配置

        该函数用于配置Modbus TCP设备的通信参数表，定义数据采集的寄存器地址、长度和采集周期等信息。

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            functionCode (int): Modbus功能码，支持0x01，0x02，0x03，0x04，0x05，0x06，0x0F，0x10
            address (int): 寄存器起始地址
            length (int):  读写地址数量
            period (int, optional): 采集周期，单位为毫秒，默认值为1000ms

        返回值:
             json: 写入数据命令的响应结果
            
        """
        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if self.__has_tableName( self.GetModbusTcpConfig(),devicename,tablename):
            raise ValueError(f"表名已存在: {tablename},修改请使用Reset")

        if not self.__is_valid_variable_name(tablename):
            raise ValueError(f"无效的变量名: {tablename}")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setTable",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "functionCode": functionCode.value,
                "addr": address,
                "count": length,
                "period": period
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.3 创建/修改通信表
    def ResetModbusTcpTable(self, devicename: str, tablename: str, functionCode: ModbusTcpFunctionCodeType, address: int, length: int,
                          period: int = 1000):
        """
        设置Modbus TCP通信表配置

        该函数用于配置Modbus TCP设备的通信参数表，定义数据采集的寄存器地址、长度和采集周期等信息。

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            functionCode (int): Modbus功能码，支持0x01，0x02，0x03，0x04，0x05，0x06，0x0F，0x10
            address (int): 寄存器起始地址
            length (int):  读写地址数量
            period (int, optional): 采集周期，单位为毫秒，默认值为1000ms

        返回值:
             json: 写入数据命令的响应结果

        """

        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName( self.GetModbusTcpConfig(),devicename,tablename):
            raise ValueError(f"表不存在: {tablename},请使用Set")

        if not self.__is_valid_variable_name(tablename):
            raise ValueError(f"无效的变量名: {tablename}")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setTable",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "functionCode": functionCode.value,
                "addr": address,
                "count": length,
                "period": period
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.4 删除通信表
    def RemoveModbusTcpTable(self, devicename: str, tablename: str):
        """
        删除Modbus TCP通信表

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一

        返回值:
             json: 写入数据命令的响应结果

        """
        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName( self.GetModbusTcpConfig(),devicename,tablename):
            raise ValueError(f"表不存在: {tablename}")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/removeTable",
            "db": {
                "name": devicename,
                "tableName": tablename
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.5 修改表的通信周期
    def SetModbusTcpPeriod(self, devicename: str, tablename: str, period: int):
        """
        修改Modbus TCP通信表的通信周期

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            period (int): 周期，单位为毫秒

        返回值:
             json: 写入数据命令的响应结果

        """

        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName( self.GetModbusTcpConfig(),devicename,tablename):
            raise ValueError(f"表不存在: {tablename}")


        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setPeriod",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "period": period
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.6 给地址设置别名
    def SetModbusTcpTableName(self, devicename: str, tablename: str,address: int,aliasname: str):
        """
        给Modbus Tcp地址设置别名

        该别名可以脚本指令中通过ModbusTCP[“别名”]的方式进行读写

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            address(int):地址
            aliasname(str):别名

        返回值:
             json: 写入数据命令的响应结果

        """
        if not self.__has_deviceName( self.GetModbusTcpConfig(),devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName( self.GetModbusTcpConfig(),devicename,tablename):
            raise ValueError(f"表不存在: {tablename}")

        if not self.__is_valid_variable_name(aliasname):
            raise ValueError(f"无效的变量名: {aliasname}")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setName",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "addr": address,
                "alias": aliasname
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.7 给地址段设置数据类型
    def SetModbusTcpTableType(self, devicename: str, tablename: str,address: int,datatype: ModbusTcpTableType,length: int):
        """
        只对保持和输入寄存器有效，对应功能码0x03,0x04,0x06,0x10。

        默认数据类型是U16。

        注意：0x06功能码只有一个地址，所以只能设置为I16或U16

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            address(int):地址
            type(enum): 数据类型 ModbusTcpTableType
            length(int): 地址数量，该数量应与对应的数据类型长度一致，可连续设置多组，例如将4个地址设置为两个U32类型数据

        返回值:
             json: 写入数据命令的响应结果

        """

        if not self.__has_deviceName(self.GetModbusTcpConfig(), devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName(self.GetModbusTcpConfig(), devicename, tablename):
            raise ValueError(f"表不存在: {tablename}")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setType",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "type": datatype.value,
                "addr": address,
                "count": length
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.8 修改地址的值
    def SetModbusTcpValue(self, devicename: str, tablename: str,address: int,value: int):
        """
        只有写表的数据值可修改

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一
            address(int):地址，如果设置过数据类型，该地址须是该类型数据的首地址
            value(int):该数据类型对应的值，线圈寄存器的值为0或1

        返回值:
             json: 写入数据命令的响应结果

        """

        if not self.__has_deviceName(self.GetModbusTcpConfig(), devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName(self.GetModbusTcpConfig(), devicename, tablename):
            raise ValueError(f"表不存在: {tablename}")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/setVal",
            "db": {
                "name": devicename,
                "tableName": tablename,
                "addr": address,
                "val": value
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.9 获取所有设备配置
    def GetModbusTcpConfig(self):
        """
        获取所有设备配置

        返回值:
             json: 写入数据命令的响应结果

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/getConfig"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.10 获取所有设备状态
    def GetModbusTcpState(self):
        """
        获取所有设备状态

        返回值:
            json: 写入数据命令的响应结果

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "ModbusTcp/getState"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.5.11 获取表的值
    def GetModbusTcpValue(self, devicename: str, tablename: str) -> list:
        """
        获取表值

        参数:
            devicename (str): 设备
            tablename (str): 表名，该设备下唯一

        返回值:
            json: 写入数据命令的响应结果

        """
        if not self.__has_deviceName(self.GetModbusTcpConfig(), devicename):
            raise ValueError(f"设备不存在: {devicename}")

        if not self.__has_tableName(self.GetModbusTcpConfig(), devicename, tablename):
            raise ValueError(f"表不存在: {tablename}")

        res = self.GetModbusTcpState()
        return res["db"][devicename]["tables"][tablename]["val"]

    # 2.2.6.1 负载辨识 是否在给定采样位置
    def PayloadIsOnGivenSamplePosition(self,jntTargetPos: list[float],jntActualPos: list[float]) -> bool:
        """
        是否在给定采样位置

        参数：
            jntTargetPos(list[float]): Float64, Unit:degree, 数组长度为机器人的自由度
            jntActualPos(list[float]): Float64, Unit:degree, 数组长度为机器人的自由度

        返回值:
            true:机器人在给定的采样位置,
            false:机器人不在给定的采样位

        """
        if len(jntTargetPos) != 6:
            raise Exception("jntTargetPos变量至少为6位")
        if len(jntActualPos) != 6:
            raise Exception("jntTargetPos变量至少为6位")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/IsOnGivenSamplePosition",
            "db":{
                "jntTargetPos": jntTargetPos,
                "jntActualPos": jntActualPos
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return bool(self._safe_parse_response(response)["db"])

    # 2.2.6.2传感器数据采样
    def PayloadLoadIdenJSSample(self):
        """
        传感器数据采样

        返回值:
             json: 写入数据命令的响应结果

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/LoadIdenJSSample"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.6.3负载辨识计算接口
    def PayloadIdentificationJS(self,payload:PayloadList):
        """
        负载辨识计算接口

        参数：payload(PayloadList)4个采样点的数据

        返回值:
             json: 写入数据命令的响应结果

        """
        if len(payload.list) != 4:
            raise Exception("payload变量至少为4位")

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/PayloadIdentificationJS",
            "db":[{
                "jntPos": payload[0].jntPos,
                "jntTrqWithoutLoad": payload[0].jntTrqWithoutLoad,
                "jntTrqWithLoad": payload[0].jntTrqWithLoad,
            },
             {
                "jntPos": payload[1].jntPos,
                "jntTrqWithoutLoad": payload[1].jntTrqWithoutLoad,
                "jntTrqWithLoad": payload[1].jntTrqWithLoad,
            },
             {
                "jntPos": payload[2].jntPos,
                "jntTrqWithoutLoad": payload[2].jntTrqWithoutLoad,
                "jntTrqWithLoad": payload[2].jntTrqWithLoad,
             },
                {
                "jntPos": payload[3].jntPos,
                "jntTrqWithoutLoad": payload[3].jntTrqWithoutLoad,
                "jntTrqWithLoad": payload[3].jntTrqWithLoad,
             }
             ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.7.1初始化拖动参数
    def SetDefaultDragParam(self):
        """
        初始化拖动参数

        返回值:
             json: 写入数据命令的响应结果

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/SetDefaultServoDragParam"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.7.2获取拖动灵敏度
    def GetDragSensitivity(self) -> int:
        """
        获取拖动灵敏度

        返回值:
             int:拖动灵敏度 0-100

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/GetDragSensitivity"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return int(self._safe_parse_response(response)["db"]["sensitivity"])

    # 2.2.7.3获取拖动模式
    def GetDragMode(self) -> int:
        """
        获取拖动模式

        返回值:
             int: 拖动模式 0->老版拖动, 2->新版拖动

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/GetDragMode"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return int(self._safe_parse_response(response)["db"])

    # 2.2.7.4开启/关闭拖动姿态锁
    def SetCartOriLock(self, enable: bool) -> bool:
        """
        开启/关闭拖动姿态锁

        参数:
            enable (bool): True-开启, False-关闭

        返回值:
             bool: 是否开启成功

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/SetCartOriLock",
            "db": {
                "cartOriLock": enable
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return bool(self._safe_parse_response(response)["db"])

    # 2.2.7.5获取拖动姿态锁的状态
    def GetCartOriLockState(self) -> bool:
        """
        获取拖动姿态锁的状态

        返回值:
             bool: 拖动姿态锁的状态

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/GetCartOriLockState"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return bool(self._safe_parse_response(response)["db"])

    # 2.2.8.1获取编码器计数
    def GetEncoderCount(self,index:int) -> int:
        """
        获取编码器计数

        参数：index(int):传送带编号

        返回值:
             int: 传送带当前编码器计数

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/getEncoderCount",
            "db": {
                "index": index
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)["db"]

    # 2.2.8.2使能传送带
    def EnableConveyor(self, index:int):
        """
        使能传送带

        使能后，控制器通过高速IO来同步传送带编码器位置

        参数：index(int):传送带编号

        返回值:
             json: 写入数据命令的响应结果

        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/enableConveyor",
            "db": {
                "index": index
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.8.3取消使能传送带
    def DisableConveyor(self, index: int):
        """
        取消使能传送带

        参数：index(int):传送带编号

        返回值:
              json: 写入数据命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/disableConveyor",
            "db": {
                "index": index
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.8.4传送带当量标定
    def CalibrateConveyor(self, index: int, startpoint: list[float], startcount: int, endpoint: list[float], endcount: int) -> int:
        """
        传送带当量标定

        参数：index(int):传送带编号
            startpoint(list[float]):起点处机器人示教的笛卡尔坐标
            startcount(int):起点处编码器计数
            endpoint(list[float]):终点处机器人示教的笛卡尔坐标
            endcount(int):终点处编码器计数

        返回值:
              int:传送带当量标定结果
        """
        if len(startpoint) != 6 or len(endpoint) != 6:
            raise "起始点参数错误"
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/calibrateConveyor",
            "db": {
                "index": index,
                "start":{
                    "point":startpoint,
                    "count":startcount
                },
                "end":{
                    "point":endpoint,
                    "count":endcount
                }
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return int(self._safe_parse_response(response)["db"])

    # 2.2.8.5设置传送带配置参数
    def SetConveyorConfig(self, config: ConveyorConfig):
        """
        传送带当量标定

        参数：config(ConveyorConfig):传送带配置类

        返回值:
              json: 写入数据命令的响应结果
        """
        config_dict = config.to_dict()
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/setConfig",
            "db": config_dict
        }

        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.8.6获取传送带配置参数
    def GetConveyorConfig(self, index: int) -> dict:
        """
        传送带当量标定

        参数：index(int):传送带编号

        返回值:
              json: 写入数据命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/getConfig",
            "db": {
                "index": index,
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return ConveyorConfig.to_dict(self._safe_parse_response(response)["db"].tostring())

    #  2.2.8.7 使用TCP连接相机
    def ConveyorConnectCamera(self,index:int):
        """
       使用TCP连接相机

       参数：index(int):传送带编号

       返回值:
             json: 写入数据命令的响应结果
       """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/connectCamera",
            "db": {
                "index": index,
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    #  2.2.8.8 断开相机连接
    def ConveyorDisconnectCamera(self, index: int):
        """
       断开相机连接

       参数：index(int):传送带编号

       返回值:
             json: 写入数据命令的响应结果
       """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/disconnectCamera",
            "db": {
                "index": index,
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    #  2.2.8.9 获取相机状态
    def ConveyorGetCameraState(self, index: int):
        """
       获取相机状态

       参数：index(int):传送带编号

       返回值:
             json: 写入数据命令的响应结果
             "state":相机状态 0：未连接 1：已连接
       """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/getCameraState",
            "db": {
                "index": index,
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    #  2.2.8.10 发送消息到相机
    def ConveyorSendMsgToCamera(self, index: int,msg: str):
        """
       发送消息到相机

       参数：index(int):传送带编号
            msg(str):发送的消息

       返回值:
             json: 写入数据命令的响应结果
       """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/sendMsgToCamera",
            "db": {
                "index": index,
                "msg": msg
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    #  2.2.8.11 获取上次触发DI时的编码器计数
    def ConveyorGetDItriggerEncoderCount(self, index: int) ->int:
        """
        获取上次触发DI时的编码器计数

        参数：index(int):传送带编号

        返回值:
            int: 上一次触发DI时的编码器计数
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/getDItriggerEncoderCount",
            "db": {
                "index": index
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return int(self._safe_parse_response(response)["db"])

    # 2.2.8.12 标定DI信号触发位置
    def ConveyorCalibrateDItriggerPos(self,index:int,x:float,startcount:int,endcount:int) -> float:
        """
        标定DI信号触发位置

        参数：index(int):传送带编号
            x(float):示教工件的X坐标
            startcount(int):DI信号触发时的编码器计数
            endcount(int):示教工件时的编码器计数

        返回值:
            float: DI信号触发时的x坐标
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Conveyor/calibrateDItriggerPos",
            "db": {
                "index": index,
                "x": x,
                "startcount": startcount,
                "endcount": endcount
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return float(self._safe_parse_response(response)["db"])

    # 2.2.9.0 正解
    def Apos2Cpos(self, apos: list[float], coor: list[float] = None, tool: list[float] = None):
        """
        将关节坐标转换为笛卡尔坐标（毫米/度单位）

        参数:
            apos (list[float]): 笛卡尔坐标 [x, y, z, rx, ry, rz]
            coor (list[float]): 用户坐标系 [x, y, z, rx, ry, rz]
            tool (list[float]): 工具坐标系 [x, y, z, rx, ry, rz]

        返回值:
            json: 坐标转换命令的响应结果
        """
        if len(apos) != 6:
            raise ValueError("cpos参数长度必须为6")
        if coor is None:
            coor = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if tool is None:
            tool = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/apostocpos",
            "db": {
                "jp": apos,
                "coor": coor,
                "tool": tool,
                "ep": []
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.9.0 逆解
    def Cpos2Apos(self, cpos: list[float], reference_joint=None):
        """
        将笛卡尔坐标转换为关节坐标（毫米/度单位）

        参数:
            cpos (list[float]): 笛卡尔坐标 [x, y, z, rx, ry, rz]
            reference_joint: 参考关节坐标

        返回值:
            json: 坐标转换命令的响应结果
        """
        if len(cpos) != 6:
            raise ValueError("cpos参数长度必须为6")
        if reference_joint is None:
            reference_joint = [20,20,20,20,20,20]
        if len(reference_joint) != 6:
            raise ValueError("reference_joint参数长度必须为6")
        else:
            reference_joint = [math.radians(reference_joint[0]), math.radians(reference_joint[1]),
                               math.radians(reference_joint[2]), math.radians(reference_joint[3]),
                               math.radians(reference_joint[4]), math.radians(reference_joint[5])]

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/cpostoapos",
            "db": {
                "cp": [cpos[0], cpos[1], cpos[2], cpos[3], cpos[4], cpos[5]],
                "rj": [reference_joint[0], reference_joint[1], reference_joint[2], reference_joint[3],
                       reference_joint[4], reference_joint[5]],
                "ep": []
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.0 点动
    def Jog(self, mode: JogMode, speed: float, index: int,coorid: int):
        """
        控制机器人点动移动
        需要每 500ms 调用点动心跳接口维持点动 JogHeartbeat
        参数:
            mode (JogMode): 枚举类型，
            speed (float): 点动速度
            index (int): 轴序号，如果是关节点动，范围1-6分别对应joint1-6；如果是笛卡尔点动，范围1-6分别对应X、Y、Z、RX、RY、RZ
            coorType (int):
            coorid (int):

        返回值:
            json: 点动命令的响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/jog",
            "db": {
                "mode": mode.value,
                "speed": speed,
                "index": index,
                "coorId": coorid,
                }
            }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.0 点动
    def StopJog(self):
        """
        控制机器人停止点动移动

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/stopJog",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.0 点动心跳
    def JogHeartbeat(self):
        """
        控制机器人点动心跳

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/jogHeartbeat",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)


    # 2.2.10.1 MoveTo
    def __MoveTo(self, movType:MoveType, cpos:list[float] = None, apos:list[float] = None):
        """
        控制机器人移动到指定位置
        
        参数:
            movType (MoveType): 移动类型枚举值，当moveType.value == MovJ 或者 MovL spos和apos才有效
            cpos(list[float]):笛卡尔坐标
            apos(list[float]):关节角度

        返回值:
            json: 移动命令的响应结果
        """

        # 初始化 message_dict 以避免未定义引用
        message_dict = None
        if movType in {MoveType.Home, MoveType.Candle, MoveType.Faulty, MoveType.Package, MoveType.Safety}:
            message_dict = {
                "id": "m8y21rn20ws8a974",
                "ty": "Robot/moveTo",
                "db": {
                    "type": movType.value
                }
            }
        elif movType == MoveType.MovL:
            if cpos is None:
                raise ValueError("cpos不能为空")
            message_dict = {
                "id": "m8y21rn20ws8a974",
                "ty": "Robot/moveTo",
                "db": {
                    "type": movType.value,
                    "target": {
                        "cp": cpos,
                        "jp": [],
                        "ep": []
                    }
                }
        }
        elif movType == MoveType.MovJ:
            if apos is None:
                raise ValueError("apos不能为空")
            message_dict = {
                "id": "m8y21rn20ws8a974",
                "ty": "Robot/moveTo",
                "db": {
                    "type": movType.value,
                    "target": {
                        "cp": [],
                        "jp": apos,
                        "ep": []
                    }
                }
            }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.2 MoveTo心跳
    def __MoveToHeartbeatOnce(self):
        """
        发送一次移动心跳信号,配合MoveTo使用，需要在MoveTo调用后每0.5s调用一次

        参数:
            time (float): 发送间隔时间（秒）

        返回值:
            json: 心跳信号的响应结果
        """
        message_dict = {
            "id": "m8y21rn20ws74",
            "ty": "Robot/moveToHeartbeat"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.2 MoveTo心跳
    def __MoveToHeartbeatAlways(self, _time: float = 0.5):
        """
        循环发送心跳信号，配合MoveTo使用，需要在MoveTo调用后
        
        参数:
            time (float): 发送间隔时间（秒）

        返回值:
            json: 心跳信号的响应结果
        """
        if _time <= 0 or _time >= 1:
            raise ValueError("time参数必须小于1")
        while True:
            try:
                message_dict = {
                    "id": "m8y21rn20ws74",
                    "ty": "Robot/moveToHeartbeat"
                }
                message_str = json.dumps(message_dict)
                self.client.send(message_str, self.DEBUG)
            except Exception as e:
                print(f"心跳发送失败: {e}")
            time.sleep(_time)  # 每0.5秒发送一次

    def MovJ(self, apos: list[float]):
        """
        控制机器人关节运动到指定位置
        阻塞式函数，直到运动完成才返回
        参数:
            apos(list[float]):关节角度Float类型的列表，单位为度

        返回值:
        """
        self.__MoveTo(MoveType.MovJ, apos=apos)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovL(self, cpos: list[float]):
        """
        控制机器人直线运动到指定位置

        参数:
            cpos(list[float]):笛卡尔坐标Float类型的列表，单位为度

        返回值:
        """
        self.__MoveTo(MoveType.MovL, cpos=cpos)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovHome(self):
        """
        控制机器人回到Home位置

        参数:
        返回值:
        """
        self.__MoveTo(MoveType.Home)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovCandle(self):
        """
        控制机器人回到Candle位置

        参数:
        返回值:
        """
        self.__MoveTo(MoveType.Candle)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovFaulty(self):
        """
        控制机器人回到Faulty位置

        参数:
        返回值:
        """
        self.__MoveTo(MoveType.Faulty)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovPackage(self):
        """
        控制机器人回到Package位置

        参数:
        返回值:
        """
        self.__MoveTo(MoveType.Package)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    def MovSafety(self):
        """
        控制机器人回到Safety位置

        参数:
        返回值:
        """
        self.__MoveTo(MoveType.Safety)
        self.__MoveToHeartbeatOnce()
        signal = True
        while signal:
            res = self.GetRobotStates()
            if res["db"]["state"] == 4:
                self.__MoveToHeartbeatOnce()
            else:
                signal = False
        return

    # 2.2.10.3 上使能
    def SwitchOn(self):
        """
        控制机器人上使能

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/switchOn",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.3 下使能
    def SwitchOff(self):
        """
        控制机器人下使能

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/switchOff",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.3 手动模式
    def ToManual(self):
        """
        控制机器人切换到手动模式

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/toManual",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.3 自动模式
    def ToAuto(self):
        """
        控制机器人切换到手动模式

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/toAuto",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.10.3 自动模式
    def ToRemote(self):
        """
        控制机器人切换到远程模式

        参数:
        返回值:
            json: 响应结果
        """

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/toRemote",
            "db": ""
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)



    # 2.2.11.1获取IO值
    def GetIOValue(self, data: list[dict]):
        """
        获取IO值

        参数:
            data (list[dict]): IO数据列表
            由字典组成{"type": "DI", "port": 0},

        返回值:
            json: IO值的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": data
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def GetDI(self, port: int) -> int:
        """
        获取数字输入端口值

        参数:
            port (int): 端口号（0-15）

        返回值:
            int: 端口值（0或1）
        """
        if port < 0 or port > 15:
            raise ValueError("端口号必须在0-15之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [{
                "type": "DI", "port": port
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = self._safe_parse_response(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def GetAI(self, port: int) -> float:
        """
        获取模拟输入端口值

        参数:
            port (int): 端口号（0-3）

        返回值:
            float: 端口值
        """
        if port < 0 or port > 3:
            raise ValueError("端口号必须在0-3之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [{
                "type": "AI", "port": port
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = self._safe_parse_response(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def GetDO(self, port: int):
        """
        获取数字输出端口值

        参数:
            port (int): 端口号

        返回值:
            端口值（0或1）
        """
        if port < 0 or port > 15:
            raise ValueError("端口号必须在0-15之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [
                {"type": "DO", "port": port}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = self._safe_parse_response(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def GetAO(self, port: int):
        """
        获取模拟输出端口值

        参数:
            port (int): 端口号

        返回值:
            端口值
        """
        if port < 0 or port > 3:
            raise ValueError("端口号必须在0-3之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [
                {"type": "AO", "port": port}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = self._safe_parse_response(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    #  2.2.11.2 写入IO值
    def SetIOValue(self, data: dict):
        """
        写入IO值

        参数:
            data (list[dict]): IO数据列表
            由字典组成{"type": "DI", "port": 0,"value": 1}},

        返回值:
            json: IO值的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/SetIOValue",
            "db": data
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def SetDO(self, port: int, value: int):
        """
        设置数字输出端口值

        参数:
            port (int): 端口号
            value (int): 要设置的值（0或1）

        返回值:
            json: 设置命令的响应结果
        """
        if value != 0 and value != 1:
            raise ValueError("值必须为0或1")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/SetIOValue",
            "db": [
                {"type": "DO", "port": port, "value": value}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def SetAO(self, port: int, value: float):
        """
        设置模拟输出端口值

        参数:
            port (int): 端口号
            value (float): 要设置的值

        返回值:
            json: 设置命令的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/SetIOValue",
            "db": [{
                "type": "AO", "port": port, "value": value
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.2.12.1 获取寄存器值
    def GetRegisterValue(self,addrlist:list[int]):
        """
        获取寄存器值

        参数:
            addr (list[int]): 寄存器地址列表

        返回值:
            json: 寄存器的响应结果
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/GetRegisterValue",
            "db": addrlist
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def GetBaseRegisterValue(self, name: BaseRegister) -> int | None:
        """
        获取基础寄存器值

        参数:
            name (BaseRegister): 寄存器名称枚举值

        返回值:
            int | None: 寄存器值
        """
        if name in {BaseRegister.majorVersion, BaseRegister.minorVersion}:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

        if name in {BaseRegister.seconds, BaseRegister.milliSeconds,BaseRegister.heartBeatFromMaster,BaseRegister.heartBeatToMaster}:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def GetControlRegisterValue(self, name: ControlRegister):
        """
       获取控制寄存器值

       参数:
           name (ControlRegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值
       """
        if name in ControlRegister:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def GetStatusRegisterValue(self, name: StatusRegister):
        """
       获取状态寄存器值

       参数:
           name (StatusRegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值
       """
        if name in StatusRegister:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def GetMotionInfoRegisterValue(self, name: MotionInfoRegister):
        """
       获取位置信息寄存器值

       参数:
           name (MotionInfoRegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值,单位：米(m)，弧度(deg)
       """
        if name in MotionInfoRegister:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def GetIORegisterValue(self, name: IORegister):
        """
       获取IO寄存器值

       参数:
           name (IORegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值
       """
        if name in IORegister:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": [name.value]
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(self._safe_parse_response(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def GetBoolRegisterValue(self, address: int) -> int:
        """
        获取布尔寄存器值

        参数:
            address (int): 寄存器地址（9000-9431）

        返回值:
            int: 寄存器值（0或1）
        """
        if address < 9000 or address > 9431:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/GetRegisterValue",
            "db": [address]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = int(self._safe_parse_response(response)['db'][0]['value'])
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def GetIntRegisterValue(self, address: int) -> int:
        """
        获取整型寄存器值

        参数:
            address (int): 寄存器地址（49000-49130，且为偶数）

        返回值:
            int: 寄存器值
        """
        if address < 49000 or address > 49130 or address % 2 != 0:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/GetRegisterValue",
            "db": [address]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = int(self._safe_parse_response(response)['db'][0]['value'])
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def GetRealVariableRegister(self,address:int) ->float:
        """
        获取整型寄存器值

        参数:
            address (int): 寄存器地址（49200-49330，且为偶数）

        返回值:
            int: 寄存器值
        """
        if address < 49200 or address > 49330 or address % 2 != 0:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/GetRegisterValue",
            "db": [address]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = int(self._safe_parse_response(response)['db'][0]['value'])
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    # 2.2.12.2 写入寄存器值
    def SetRegisterValue(self,addrlist:dict):
        """
        获取寄存器值

        参数:
           addrlist(list[dict]): 寄存器地址和值的字典列表
                {"address": 10000, "value": 0},

        返回值:
            json: 寄存器的响应结果
        """
        message_dict = {
            "id":"m912rb1b0wsc2742",
            "ty":"RegisterManager/SetRegisterValue",
            "db":addrlist
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def SetControlRegisterValue(self, name: ControlRegister, value: int):
        """
       设置控制寄存器值

       参数:
           name (ControlRegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值
       """
        if name in ControlRegister:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/SetRegisterValue",
                "db":{"address": name, "value": value}
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            return self._safe_parse_response(response)

    def SetIORegisterValue(self,name:IORegister,value:int):
        """
       设置IO寄存器值

       参数:
           name (IORegister): 寄存器名称枚举值

       返回值:
           int | Uint16 |None: 寄存器值
       """
        if name in {IORegister.readDIStartPort0,IORegister.readDIStartPort1,IORegister.readDIStartPort2,IORegister.readDIStartPort3}:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/SetRegisterValue",
                "db": {"address": name, "value": value}
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            return self._safe_parse_response(response)

    def SetBoolRegisterValue(self, address: int, value: int):
        """
        设置布尔寄存器值

        参数:
            address (int): 寄存器地址(9032~9431)
            value (int): 要设置的值（0或1）

        返回值:
            json: 设置命令的响应结果
        """
        if address < 9032 or address > 9431:
            raise ValueError("无效的寄存器名称")
        if value != 0 and value != 1:
            raise ValueError("值必须为0或1")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/SetRegisterValue",
            "db":{"address": address, "value": value}
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def SetIntRegisterValue(self, address: int, value: int):
        """
        设置整型寄存器值

        参数:
            address (int): 寄存器地址 (49100~49130)且为偶数
            value (int): 要设置的值

        返回值:
            json: 设置命令的响应结果
        """
        if address < 49100 or address > 49130 or address % 2 != 0:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/SetRegisterValue",
            "db":
                {"address": address, "value": value}
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def SetRealRegisterValue(self, address: int, value: float):
        """
        设置浮点型寄存器值

        参数:
            address (int): 寄存器地址 (49100~49130)且为偶数
            value (float): 要设置的值

        返回值:
            json: 设置命令的响应结果
        """
        if address < 49300 or address > 49330 or address % 2 != 0:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/SetRegisterValue",
            "db":
                {"address": address, "value": value}
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.1 工程状态
    def GetProjectState(self, recvTime: int = 200):
        """
        获取工程状态

        参数:
            recvTime (int): 接收超时时间（毫秒）

        返回值:
            json: 项目状态信息

        """
        message_dict = {
            "ty": "publish/ProjectState",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.2 变量数据更新
    def GetVarUpdate(self, recvTime: int = 200):
        """
        获取变量更新信息

        参数:
            recvTime (int): 接收超时时间（毫秒）

        返回值:
            json: 变量更新信息
        """
        message_dict = {
            "ty": "publish/VarUpdate",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.3 机器人状态
    def GetRobotStates(self, recvTime: int = 200):
        """
        获取机器人状态信息
        
        参数:
            recvTime (int): 接收超时时间（毫秒）
            
        返回值:
            json: 机器人状态信息
        """
        message_dict = {
            "ty": "publish/RobotStatus",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.4 机器人姿态
    def GetRobotPosture(self, recvTime: int = 200):
        """
        获取机器人姿态信息
        
        参数:
            recvTime (int): 接收超时时间（毫秒）
            
        返回值:
            json: 机器人姿态信息
        """
        message_dict = {
            "ty": "publish/RobotPosture",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.5 机器人坐标系
    def GetRobotCoordinate(self, recvTime: int = 200):
        """
        获取机器人坐标信息
        
        参数:
            recvTime (int): 接收超时时间（毫秒）
            
        返回值:
            json: 机器人坐标信息
        """
        message_dict = {
            "ty": "publish/obotCoordinate",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.6 系统日志
    def GetLog(self, recvTime: int = 200):
        """
        获取日志信息
        
        参数:
            recvTime (int): 接收超时时间（毫秒）
            
        返回值:
            json: 日志信息
        """
        message_dict = {
            "ty": "publish/Log",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    # 2.4.7 错误信息
    def GetError(self, recvTime: int = 200):
        """
        获取错误信息
        
        参数:
            recvTime (int): 接收超时时间（毫秒）
            
        返回值:
            json: 错误信息
        """
        message_dict = {
            "ty": "publish/Error",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def CRIStartDataPush(self,ip: str, port: int, duration: int):
        """
        开始CRI数据推送

        参数:
            ip (str): 推送目标地址
            port (int): 推送目标端口，合法范围为1000-65534
            duration (int): 数据推送间隔, 单位: ms, 范围 >=1整数
        返回值:
            json: 响应结果
        """
        if port < 1000 or port > 65534:
            raise ValueError("端口号必须在1000-65534之间")
        if duration < 1:
            raise ValueError("duration必须大于等于1")
        message_dict = {
            "id": 1,
            "ty": "CRI/StartDataPush",
            "db": {
                "ip": ip,
                "port": port,
                "duration": duration
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def CRIStopDataPush(self):
        """
        关闭CRI数据推送

        参数:
        返回值:
            json: 响应结果
        """
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "CRI/StopDataPush"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def CRIStartControl(self,filterType:int,duration:int,startBuffer:int):
        """
        关闭CRI数据推送

        参数:
            filterType (int): 滤波类型 0 - 关闭滤波 1 - 平均滤波值 2 - 二阶低通滤波 3 - 椭圆滤波
            duration (int): 指令间隔, 单位: ms, 范围:
            startBuffer (int): 启动缓冲点数量, 范围: [1 - 100] 整数, 当接受到至少该数量的点位时, 机器人才会开始运动
        返回值:
            json: 响应结果
        """
        if filterType < 0 or filterType > 3:
            raise ValueError("filterType必须在0-3之间")
        if duration < 1:
            raise ValueError("duration必须大于等于1")
        if startBuffer < 1 or startBuffer > 100:
            raise ValueError("startBuffer必须在1-100之间")

        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "CRI/StartControl",
            "db": {
                "filterType": filterType,
                "duration": duration,
                "startBuffer": startBuffer
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)

    def CRIStopControl(self):
        """
        关闭CRI数据推送

        参数:
        返回值:
            json: 响应结果
        """
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "CRI/StopControl"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return self._safe_parse_response(response)