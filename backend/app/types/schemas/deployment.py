"""
LLM model deployment schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from .base import ModelStatus


class DeployRequest(BaseModel):
    """部署模型请求"""
    model_name: str = Field(..., description="HuggingFace 模型 ID 或本地路径")
    local_path: Optional[str] = Field(None, description="本地模型路径（可选）")
    port: Optional[int] = Field(None, description="服务端口（不指定则自动分配）")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "dtype": "auto",
            "gpu_memory_utilization": 0.85,
            "max_model_len": 4096,
            "trust_remote_code": True,
        },
        description="vLLM 启动参数"
    )


class ModelInfo(BaseModel):
    """模型信息"""
    id: str = Field(..., description="模型实例 ID")
    model_name: str = Field(..., description="模型名称")
    status: ModelStatus = Field(..., description="运行状态")
    pid: Optional[int] = Field(None, description="进程 ID")
    port: int = Field(..., description="服务端口")
    start_time: Optional[datetime] = Field(None, description="启动时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="启动参数")
