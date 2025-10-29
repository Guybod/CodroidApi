from enum import Enum
from typing import  Dict, Any

class MoveType(Enum):
    """移动类型枚举类，定义机器人的各种移动方式"""
    Home = 0        # Home位
    Safety = 1      # 安全位
    Candle = 2      # 蜡烛位
    Package = 3     # 打包位
    MovJ = 4        # 关节移动
    MovL = 5        # 直线移动
    Faulty = 6      # 恢复故障点

class BaseRegister(Enum):
    """基础寄存器枚举类，定义机器人系统的基础寄存器地址"""
    majorVersion = 41000    # 主版本号寄存器
    minorVersion = 41001    # 次版本号寄存器
    seconds = 41004         # 秒寄存器
    milliSeconds = 41006    # 毫秒寄存器
    heartBeatToMaster = 41008    # 发送到主站的心跳寄存器
    heartBeatFromMaster = 41010  # 来自主站的心跳寄存器

class ControlRegister(Enum):
    """控制寄存器枚举类，定义机器人控制相关的寄存器地址"""
    startProject = 1000          # 启动项目寄存器
    stopProject = 1001           # 停止项目寄存器
    pauseProject = 1002          # 暂停项目寄存器
    switchOn = 1003              # 开启开关寄存器
    switchOff = 1004             # 关闭开关寄存器
    clearWarning = 1005          # 清除警告寄存器
    startDrag = 1006             # 开始拖拽寄存器
    stopDrag = 1007              # 停止拖拽寄存器
    changeToAuto = 1008          # 切换到自动模式寄存器
    changeToManual = 1009        # 切换到手动模式寄存器
    setAutoMoveRate = 1010       # 设置自动移动速率寄存器
    startProjectNumber = 42000   # 启动项目编号寄存器
    setAutoMoveRateValue = 42001 # 设置自动移动速率值寄存器
    setDOPort = 42002            # 设置DO端口寄存器
    setDOValue = 42003           # 设置DO值寄存器

class Typecode:
    """类型码类，用于解析和获取消息类型名称"""
    typecode = {
        '程序输出': 3,
        '警告信息': 4,
    }

    @classmethod
    def getTypeName(cls, value):
        """
        根据数值返回对应的类型名称

        形参:
            value (int): 类型码数值

        Returns:
            str: 对应的类型名称，如果未找到则返回None
        """
        if value == 3:
            return "程序输出"
        elif value == 4:
            return "警告信息"
        else:
            return None

class ModbusTcpTableType(Enum):
    """Modbus TCP表类型枚举类，定义支持的数据类型"""
    int16 = "I16"    # 16位有符号整数
    uint16 = "U16"   # 16位无符号整数
    int32 = "I32"    # 32位有符号整数
    uint32 = "U32"   # 32位无符号整数
    int64 = "I64"    # 64位有符号整数
    uint64 = "U64"   # 64位无符号整数
    float32 = "F32"  # 32位浮点数
    float64 = "F64"   # 64位浮点数

class PayloadDict:
    """
    负载数据字典类，用于存储关节位置和扭矩信息

    形参:
        jntPos (list[float]): 关节位置列表
        jntTrqWithoutLoad (list[float]): 无负载时的关节扭矩列表
        jntTrqWithLoad (list[float]): 有负载时的关节扭矩列表
    """
    def __init__(self, jntPos: list[float], jntTrqWithoutLoad: list[float], jntTrqWithLoad: list[float]):
        self.jntPos = jntPos                    # 关节位置
        self.jntTrqWithoutLoad = jntTrqWithoutLoad  # 无负载时的关节扭矩
        self.jntTrqWithLoad = jntTrqWithLoad    # 有负载时的关节扭矩

class PayloadList:
    """
    负载数据列表类，用于管理多个PayloadDict对象

    形参:
        items (list): PayloadDict对象列表
    """
    def __init__(self, items):
        self.list = items  # PayloadDict对象列表

    def __getitem__(self, index):
        """
        支持索引访问列表元素

        形参:
            index (int): 索引位置

        Returns:
            PayloadDict: 指定索引位置的PayloadDict对象
        """
        return self.list[index]

    def __len__(self):
        """
        返回列表长度

        Returns:
            int: 列表中元素的数量
        """
        return len(self.list)

    def add(self, jntPos: PayloadDict):
        """
        向列表中添加PayloadDict对象

        形参:
            jntPos (PayloadDict): 要添加的PayloadDict对象

        Raises:
            Exception: 当列表已满时抛出异常
        """
        if len(self.list) <= 4:
            self.list.append(jntPos)
        else:
            raise Exception("列表已满")

class DIConfig:
    """
    DI触发配置类，用于配置数字输入触发参数

    形参:
        port (int): DI端口号，默认为0
        trigger_pos (float): DI触发位置，单位mm，默认为0.0
    """

    def __init__(self, port: int = 0, trigger_pos: float = 0.0):
        self.port = port              # DI端口号
        self.trigger_pos = trigger_pos  # 设置DI触发位置，单位mm

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 包含配置信息的字典
        """
        return {
            "port": self.port,
            "triggerPos": self.trigger_pos
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DIConfig':
        return cls(
            port=data.get("port", 0),
            trigger_pos=data.get("triggerPos", 0.0)
        )

class CameraConfig:
    """
    相机触发配置类，用于配置相机触发参数

    形参:
        ip (str): 相机IP地址，默认为空字符串
        port (int): 相机端口号，默认为8080
        camera_type (int): 相机类型，0表示2D，1表示3D，默认为0
        duplicate_dis (float): 相机去重距离，单位mm，默认为0.0
        is_do_trigger (bool): 是否使用DO触发相机拍照，默认为False
        do_port (int): DO端口号，默认为0
        retent_time (int): DO高电平持续时间，单位ms，默认为0
        interval (int): 相机拍照触发间隔，单位ms，默认为0
    """

    def __init__(self,
                 ip: str = "",
                 port: int = 8080,
                 camera_type: int = 0,
                 duplicate_dis: float = 0.0,
                 is_do_trigger: bool = False,
                 do_port: int = 0,
                 retent_time: int = 0,
                 interval: int = 0):
        self.ip = ip                      # 相机IP地址
        self.port = port                  # 相机端口号
        self.type = camera_type           # 相机类型 0：2D 1：3D
        self.duplicate_dis = duplicate_dis  # 相机去重距离，单位mm
        self.is_do_trigger = is_do_trigger  # 是否使用DO触发相机拍照
        self.do_port = do_port            # DO端口号
        self.retent_time = retent_time    # DO高电平持续时间，单位ms
        self.interval = interval          # 相机拍照触发间隔，单位ms

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 包含配置信息的字典
        """
        return {
            "ip": self.ip,
            "port": self.port,
            "type": self.type,
            "duplicateDis": self.duplicate_dis,
            "isDOTrigger": self.is_do_trigger,
            "DOPort": self.do_port,
            "retentTime": self.retent_time,
            "interval": self.interval
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraConfig':
        return cls(
            ip=data.get("ip", ""),
            port=data.get("port", 8080),
            camera_type=data.get("type", 0),
            duplicate_dis=data.get("duplicateDis", 0.0),
            is_do_trigger=data.get("isDOTrigger", False),
            do_port=data.get("DOPort", 0),
            retent_time=data.get("retentTime", 0),
            interval=data.get("interval", 0)
        )

class SheildConfig:
    """
    屏蔽配置类，用于配置屏蔽参数

    形参:
        time (int): 屏蔽时间，单位ms，默认为0
        distance (float): 屏蔽距离，单位mm，默认为0.0
    """

    def __init__(self, time: int = 0, distance: float = 0.0):
        self.time = time              # 屏蔽时间，单位ms
        self.distance = distance      # 屏蔽距离，单位mm

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 包含配置信息的字典
        """
        return {
            "time": self.time,
            "distance": self.distance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SheildConfig':
        return cls(
            time=data.get("time", 0),
            distance=data.get("distance", 0.0)
        )

class OffsetConfig:
    """
    偏移配置类，用于配置坐标偏移参数

    形参:
        x (float): x方向偏移，单位mm，默认为0.0
        y (float): y方向偏移，单位mm，默认为0.0
        z (float): z方向偏移，单位mm，默认为0.0
        a (float): 绕x轴旋转补偿角度，单位°，默认为0.0
        b (float): 绕y轴旋转补偿角度，单位°，默认为0.0
        c (float): 绕z轴旋转补偿角度，单位°，默认为0.0
    """

    def __init__(self,
                 x: float = 0.0,
                 y: float = 0.0,
                 z: float = 0.0,
                 a: float = 0.0,
                 b: float = 0.0,
                 c: float = 0.0):
        self.x = x  # x方向偏移，单位mm
        self.y = y  # y方向偏移，单位mm
        self.z = z  # z方向偏移，单位mm
        self.a = a  # 绕x轴旋转补偿角度，单位°
        self.b = b  # 绕y轴旋转补偿角度，单位°
        self.c = c  # 绕z轴旋转补偿角度，单位°

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 包含配置信息的字典
        """
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "a": self.a,
            "b": self.b,
            "c": self.c
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OffsetConfig':
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0),
            a=data.get("a", 0.0),
            b=data.get("b", 0.0),
            c=data.get("c", 0.0)
        )

class ConveyorConfig:
    """
    传送带配置主类，用于配置传送带相关参数

    形参:
        index (int): 传送带编号，默认为1
        type (int): 传送带类型，1表示直线传送带，2表示圆盘传送带，默认为1
        trigger_type (int): 触发方式，0表示无触发，1表示DI触发，2表示相机触发，默认为0
        conveyor_coor_id (int): 传送带坐标系编号，默认为1
        encoder_resolution (float): 编码器分辨率，默认为0.00002
        encoder_channel (int): 编码器通道号，1表示HDI1&HDI2，2表示HDI3&HDI4，默认为1
        sync_deviation (float): 跟随允差，单位mm，默认为10.002
        min_boundary (float): 最小边界，单位mm，默认为10.01
        latest_sync_start (float): 最晚启动点，单位mm，默认为40.04
        latest_sync_end (float): 最晚同步点，单位mm，默认为80.08
        max_boundary (float): 最大边界，单位mm，默认为110.02
        di_config (DIConfig): DI触发配置对象，默认为DIConfig()
        camera_config (CameraConfig): 相机触发配置对象，默认为CameraConfig()
        shield_config (ShieldConfig): 屏蔽配置对象，默认为ShieldConfig()
        offset_config (OffsetConfig): 偏移配置对象，默认为OffsetConfig()

    """

    def __init__(self,
                index: int = 1,
                type: int = 1,
                trigger_type: int = 0,
                conveyor_coor_id: int = 1,
                encoder_resolution: float = 0.00002,
                encoder_channel: int = 1,
                sync_deviation: float = 10.002,
                min_boundary: float = 10.01,
                latest_sync_start: float = 40.04,
                latest_sync_end: float = 80.08,
                max_boundary: float = 110.02,
                di_config: DIConfig = DIConfig(),
                camera_config: CameraConfig = CameraConfig(),
                shield_config: SheildConfig = SheildConfig(),
                offset_config: OffsetConfig = OffsetConfig()
                 ):
        self.index = 1                    # 传送带编号
        self.type = 1                     # 传送带类型 1：直线传送带 2：圆盘传送带
        self.trigger_type = 0             # 触发方式 0：无 1：DI触发 2: 相机触发
        self.conveyor_coor_id = 1         # 传送带坐标系编号
        self.encoder_resolution = 0.00002  # 编码器分辨率
        self.encoder_channel = 1          # 编码器通道号 1: HDI1&HDI2 2: HDI3&HDI4
        self.sync_deviation = 10.002      # 跟随允差，单位mm
        self.min_boundary = 10.01         # 最小边界，单位mm
        self.latest_sync_start = 40.04    # 最晚启动点，单位mm
        self.latest_sync_end = 80.08      # 最晚同步点，单位mm
        self.max_boundary = 110.02        # 最大边界，单位mm

        # 嵌套配置对象
        self.di_config = DIConfig()       # DI配置
        self.camera_config = CameraConfig()  # 相机配置
        self.shield_config = SheildConfig()  # 屏蔽配置
        self.offset_config = OffsetConfig()  # 偏移配置

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为与JSON结构对应的字典

        Returns:
            Dict[str, Any]: 包含所有配置信息的字典
        """
        return {
            "index": self.index,
            "type": self.type,
            "triggerType": self.trigger_type,
            "conveyorCoorId": self.conveyor_coor_id,
            "encoderResolution": self.encoder_resolution,
            "encoderChannel": self.encoder_channel,
            "syncDeviation": self.sync_deviation,
            "minBoundary": self.min_boundary,
            "latestSyncStart": self.latest_sync_start,
            "latestSyncEnd": self.latest_sync_end,
            "maxBoundary": self.max_boundary,
            "DI": self.di_config.to_dict(),
            "camera": self.camera_config.to_dict(),
            "sheild": self.shield_config.to_dict(),
            "offset": self.offset_config.to_dict()
        }

    @classmethod
    def from_dict(cls, db_data: Dict[str, Any]) -> 'ConveyorConfig':
        """
        直接从字典创建ConveyorConfig实例
        """
        config = cls()

        # 设置基本属性（index使用默认值1）
        config.type = db_data.get("type", 1)
        config.trigger_type = db_data.get("triggerType", 0)
        config.conveyor_coor_id = db_data.get("conveyorCoorId", 1)
        config.conveyor_enable = db_data.get("conveyorEnable", True)
        config.encoder_resolution = db_data.get("encoderResolution", 0.00002)
        config.encoder_channel = db_data.get("encoderChannel", 1)
        config.sync_deviation = db_data.get("syncDeviation", 10.002)
        config.min_boundary = db_data.get("minBoundary", 10.01)
        config.latest_sync_start = db_data.get("latestSyncStart", 40.04)
        config.latest_sync_end = db_data.get("latestSyncEnd", 80.08)
        config.max_boundary = db_data.get("maxBoundary", 110.02)

        # 设置嵌套配置
        if "DI" in db_data:
            config.di_config = DIConfig.from_dict(db_data["DI"])

        if "camera" in db_data:
            config.camera_config = CameraConfig.from_dict(db_data["camera"])

        if "sheild" in db_data:
            config.shield_config = SheildConfig.from_dict(db_data["sheild"])

        if "offset" in db_data:
            config.offset_config = OffsetConfig.from_dict(db_data["offset"])

        return config