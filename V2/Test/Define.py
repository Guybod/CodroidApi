from enum import Enum

class MoveType(Enum):
    Home = 0        # Home位
    Safety = 1      # 安全位
    Candle = 2      # 蜡烛位
    Package = 3     # 打包位
    MovJ = 4        # 关节移动
    MovL = 5        # 直线移动
    faulty = 6      # 恢复故障点

class BaseRegister(Enum):
        majorVersion = 41000,
        minorVersion = 41001,
        seconds = 41004,
        milliSeconds = 41006,
        heartBeatToMaster = 41008,
        heartBeatFromMaster = 41010,

class ControlRegister(Enum):
    startProject = 1000,
    stopProject = 1001,
    pauseProject = 1002,
    switchOn = 1003,
    switchOff = 1004,
    clearWarning = 1005,
    startDrag = 1006,
    stopDrag = 1007,
    changeToAuto = 1008,
    changeToManual = 1009,
    setAutoMoveRate = 1010,
    startProjectNumber = 42000,
    setAutoMoveRateValue = 42001,
    setDOPort = 42002,
    setDOValue = 42003,

class Typecode:
   typecode = {
    '程序输出': 3,
    '警告信息': 4,
   }

   @classmethod
   def getTypeName(cls, value):
       """根据数值返回对应的类型名称"""
       if value == 3:
           return "程序输出"
       elif value == 4:
           return "警告信息"
       else:
           return None



