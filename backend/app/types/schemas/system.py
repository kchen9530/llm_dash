"""
System monitoring and resource tracking schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class SystemStatus(BaseModel):
    """系统状态"""
    cpu_percent: float = Field(..., description="CPU 使用率 (%)")
    memory_percent: float = Field(..., description="内存使用率 (%)")
    memory_used_gb: float = Field(..., description="已使用内存 (GB)")
    memory_total_gb: float = Field(..., description="总内存 (GB)")
    gpu_info: List[Dict[str, Any]] = Field(default_factory=list, description="GPU 信息")


class GPUInfo(BaseModel):
    """GPU 信息"""
    id: int
    name: str
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    utilization_percent: float
    temperature: Optional[float] = None
