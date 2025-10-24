import json,math,time,TcpClient
from functools import singledispatchmethod
from Define import MoveType,BaseRegister,Typecode


class Codroid:
    """
    Codroid类

    """
    def __init__(self,ip,port):
        self.heartbeat_thread = None
        self.ip = ip
        self.port = port
        self.client = TcpClient.TCPClient()
        self.DEBUG = False
        self.isConnceted = False

    def connect(self):
        try:
            self.client.connect(self.ip,self.port)
            self.isConnceted = True
        except Exception as e:
            print(e)

    def disConnect(self):
        """断开与Codroid的连接"""
        try:
            self.client.disconnect()
            self.isConnceted = False
        except Exception as e:
            print(e)

    @staticmethod
    def __convert_to_db_format(variables):
        """将变量字典列表转换为db格式

        Args:
            variables: 包含name、val和nm字段的字典列表

        Returns:
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
    def printResponse(response: json):
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
    def printSub(response: json):
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
    def printLog(response: json):
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

    def runScript(self,mainProgram:str,subThreadsName:str=None,subThreads:str=None,subProgramsName:str=None,subPrograms:str=None,interruptsName:str=None,interrupts:str=None,_vars:dict=None) -> json:
        """运行指定脚本"""
        if mainProgram is None:
            raise Exception("主程序不能为空")
        if _vars is None:
            _vars = {}
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "project/runScript",
            "db": {
                "scripts": {
                    "main": mainProgram,

                },
            "vars": _vars
            }
        }
        if subThreadsName is not None and subThreads is not None:
            message_dict["db"]["scripts"]["subThreads"] = {
                subThreadsName: subThreads
            }
        if subProgramsName is not None and subPrograms is not None:
            message_dict["db"]["scripts"]["subPrograms"] = {
                subProgramsName: subPrograms
            }
        if interruptsName is not None and interrupts is not None:
            message_dict["db"]["scripts"]["interrupts"] = {
                interruptsName: interrupts
            }

        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def moveTo(self, movType:MoveType):
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "Robot/moveTo",
            "db": {
                "type": movType.value,
                "target": {
                    "cp": [],
                    "jp": [],
                    "ep": []
                }
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def moveToHeartbeatOnce(self):
        message_dict = {
            "id": "m8y21rn20ws74",
            "ty": "Robot/moveToHeartbeat"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def moveToHeartbeatAlways(self,_time:float = 0.5):
        """循环发送心跳信号"""
        while True:
            try:
                message_dict = {
                    "id": "m8y21rn20ws74",
                    "ty": "Robot/moveToHeartbeat"
                }
                message_str = json.dumps(message_dict)
                response = self.client.send(message_str, self.DEBUG)
                return json.loads(response)
            except Exception as e:
                print(f"心跳发送失败: {e}")
            time.sleep(_time)  # 每0.5秒发送一次

    def runProject(self,project_id:str) -> json:
        """运行指定项目"""
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "project/run",
            "db": {
                "id": project_id
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def runStep(self,project_id:str) -> json:
        """运行指定项目"""
        message_dict = {
            "id": "m8y21rn20ws8a974",
            "ty": "project/runStep",
            "db": {
                "id": project_id
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def enterRemoteScriptMode (self) -> json:
        message_dict = {
        "ty": "project/enterRemoteScriptMode",
        "id": "mdo8zdy30wscc06e"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def GetProjectVars (self) -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "globalVar/GetProjectVarUpdate"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def getGlobalVars (self) -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "globalVar/getVars"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def setGlobalVar (self,name:str,value:str,note:str = "") -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "globalVar/saveVars",
        "db": {
            name: {
                "val": value,
                "nm": note
            }
        }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def setGlobalVars(self, value: list) -> json:
        """批量设置全局变量
        Args:
            value: 变量名和值的列表，每个元素是包含name和value的字典
        Returns:
            json格式的响应
        """
        format_value = self.__convert_to_db_format(value)
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "globalVar/saveVars",
            "db": format_value
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def removeGlobalVars(self, value_name: list) -> json:
        """批量设置全局变量
        Args:
            value_name: 变量名列表
        Returns:
            json格式的响应
        """
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "globalVar/removeVars",
            "db": value_name
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def pauseProject (self) -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "project/pause"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def resumeProject (self) -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "project/resume"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def stopProject (self) -> json:
        message_dict = {
        "id": "m912rb1b0wsc2742",
        "ty": "project/stop"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def setBreakpoint(self,project_id:str,line_number:list):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/setBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def addBreakpoint(self,project_id:str,line_number:list):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/addBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def removeBreakpoint(self,project_id:str,line_number:list):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/removeBreakpoint",
            "db": {
                project_id: line_number
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def clearBreakpoint(self):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/clearBreakpoint",
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def setStartLine(self,start_line:int):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/setStartLine",
            "db": start_line
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def clearStartLine(self):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "project/clearStartLine"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def rs485Init(self,baud_rate:int=115200,stop_bit:int=1,data_bit:int=8,parity:int=0):
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
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def rs485FlushReadBuffer(self):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/flushReadBuffer"
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def rs485Read(self,length:int,timeout:int = 3000):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/read",
            "db": {
                "length":length,
                "timeout": timeout
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str)
        return json.loads(response)

    def rs485Write(self,data:list[ int]):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "EC2RS485/write",
            "db": data
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str,self.DEBUG)
        return json.loads(response)

    def cpos2apos_mm_deg(self,cpos:list[float], reference_joint=None):
        if len(cpos) != 6:
            raise ValueError("cpos参数长度必须为6")
        if reference_joint is None:
            reference_joint = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if len(reference_joint) != 6:
            raise ValueError("reference_joint参数长度必须为6")
        else:
            reference_joint = [math.radians(reference_joint[0]), math.radians(reference_joint[1]),
                               math.radians(reference_joint[2]), math.radians(reference_joint[3]),
                               math.radians(reference_joint[4]), math.radians(reference_joint[5])]

        local1:float = cpos[0]/1000.0
        local2:float = cpos[1]/1000.0
        local3:float = cpos[2]/1000.0
        local4:float = math.radians(cpos[3])
        local5:float = math.radians(cpos[4])
        local6:float = math.radians(cpos[5])

        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/cpostoapos",
            "db": {
                "cp": [local1, local2, local3, local4, local5, local6],
                "rj": [reference_joint[0], reference_joint[1], reference_joint[2], reference_joint[3], reference_joint[4], reference_joint[5]],
                "ep": []
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def cpos2apos_m_rad(self, cpos: list[float], reference_joint=None):

        if len(cpos) != 6:
            raise ValueError("cpos参数长度必须为6")
        if reference_joint is None:
            reference_joint = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if len(reference_joint) != 6:
            raise ValueError("reference_joint参数长度必须为6")
        else:
            reference_joint = [math.radians(reference_joint[0]), math.radians(reference_joint[1]), math.radians(reference_joint[2]), math.radians(reference_joint[3]), math.radians(reference_joint[4]), math.radians(reference_joint[5])]
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "Robot/cpostoapos",
            "db": {
                "cp": [cpos[0], cpos[1], cpos[2], cpos[3], cpos[4], cpos[5]],
                "rj": [reference_joint[0], reference_joint[1], reference_joint[2], reference_joint[3], reference_joint[4], reference_joint[5]],
                "ep": []
            }
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def goHome(self):
        self.moveTo(MoveType.Home)
        return None

    def goSafety(self):
        self.moveTo(MoveType.Safety)
        return None

    def goCandle(self):
        self.moveTo(MoveType.Candle)
        return None

    def goPackage(self):
        self.moveTo(MoveType.Package)
        return None

    def goFaulty(self):
        self.moveTo(MoveType.faulty)
        return None


    @singledispatchmethod
    def movL(self, arg):
        raise NotImplementedError(f"不支持的类型: {type(arg)}")

    @movL.register(list)
    def _(self,arg:list[float]):
        return self.movL(MoveType.MovL,arg)

    def getProjectState(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/getProjectState",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getVarUpdate(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/VarUpdate",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getRobotStates(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/RobotStatus",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getRobotPosture(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/RobotPosture",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getRobotCoordinate(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/obotCoordinate",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getLog(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/Log",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getError(self, recvTime:int = 200):
        message_dict = {
            "ty": "publish/Error",
            "tc": recvTime
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getDI(self,port:int) -> int:
        if port < 0 or port > 15:
            raise ValueError("端口号必须在0-15之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [{
                "type": "DI","port": port
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = json.loads(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def getAI(self,port:int) -> float:
        if port < 0 or port > 3:
            raise ValueError("端口号必须在0-3之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [{
                "type": "AI","port": port
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = json.loads(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def getDO(self,port:int):
        # if port < 0 or port > 15:
        #     raise ValueError("端口号必须在0-15之间")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [
                {"type": "DO","port": port}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = json.loads(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def getAO(self,port:int):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/GetIOValue",
            "db": [
                {"type": "AO","port": port}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = json.loads(response)['db'][0]['value']
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def setDO(self,port:int,value:int):
        # if port < 0 or port > 15:
        #     raise ValueError("端口号必须在0-15之间")
        if value != 0 and value != 1:
            raise ValueError("值必须为0或1")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/SetIOValues",
            "db": [
                {"type": "DO","port": port,"value": value}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def setAO(self,port:int,value:float):
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "IOManager/SetIOValues",
            "db": [{
                "type": "AO","port": port,"value": value
            }]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getBaseRegisterValue(self,name:BaseRegister) -> int | None:
        if name not in BaseRegister:
            raise ValueError("无效的寄存器名称")
        if name == BaseRegister.majorVersion or name == BaseRegister.minorVersion:
            message_dict = {
                "id": "m912rb1b0wsc2742",
                "ty": "RegisterManager/GetRegisterValue",
                "db": name.value
            }
            message_str = json.dumps(message_dict)
            response = self.client.send(message_str, self.DEBUG)
            try:
                value = int(json.loads(response)['db'][0]['value'])
                return value
            except (KeyError, IndexError):
                print("在访问过程中，某个键或索引不存在")
                return -1

    def getBoolRegisterValue(self,address:int) -> int :
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
            value = int(json.loads(response)['db'][0]['value'])
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def setBoolRegisterValue(self,address:int,value:int):
        if address < 9032 or address > 9431:
            raise ValueError("无效的寄存器名称")
        if value != 0 and value != 1:
            raise ValueError("值必须为0或1")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/SetRegisterValues",
            "db": [
                {"address": address, "value": value}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)

    def getIntRegisterValue(self,address:int) -> int :
        if address < 49000 or address > 49130 or address%2 != 0:
            raise ValueError("无效的寄存器名称")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/GetRegisterValue",
            "db": [address,address+1]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        try:
            value = int(json.loads(response)['db'][0]['value'])
            return value
        except (KeyError, IndexError):
            print("在访问过程中，某个键或索引不存在")
            return -1

    def setIntRegisterValue(self,address:int,value:int):
        if address < 9032 or address > 9431:
            raise ValueError("无效的寄存器名称")
        if value != 0 and value != 1:
            raise ValueError("值必须为0或1")
        message_dict = {
            "id": "m912rb1b0wsc2742",
            "ty": "RegisterManager/SetRegisterValues",
            "db": [
                {"address": address, "value": value}
            ]
        }
        message_str = json.dumps(message_dict)
        response = self.client.send(message_str, self.DEBUG)
        return json.loads(response)