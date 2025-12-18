"""
Common base types and enums
"""
from enum import Enum


class ModelStatus(str, Enum):
    """模型状态枚举"""
    INITIALIZING = "INITIALIZING"  # 初始化中
    DOWNLOADING = "DOWNLOADING"     # 下载中
    STARTING = "STARTING"           # 启动中
    RUNNING = "RUNNING"             # 运行中
    STOPPING = "STOPPING"           # 停止中
    STOPPED = "STOPPED"             # 已停止
    ERROR = "ERROR"                 # 错误
    FAILED = "FAILED"               # 失败
