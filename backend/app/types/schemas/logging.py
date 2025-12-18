"""
Application logging schemas
"""
from pydantic import BaseModel
from datetime import datetime


class LogMessage(BaseModel):
    """日志消息"""
    model_id: str
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR
    message: str
