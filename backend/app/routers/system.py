"""
系统监控路由
"""
from fastapi import APIRouter

from app.models.schemas import SystemStatus
from app.services.system_monitor import system_monitor
from app.core.config import settings

router = APIRouter()


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    获取系统状态（CPU、内存、GPU）
    """
    return system_monitor.get_system_status()


@router.get("/gpu")
async def get_gpu_info():
    """
    获取 GPU 详细信息
    """
    return system_monitor.get_gpu_info()


@router.get("/compute-mode")
async def get_compute_mode():
    """
    获取当前计算模式（GPU/CPU）
    """
    return {
        "use_gpu": settings.USE_GPU,
        "force_cpu_mode": settings.FORCE_CPU_MODE,
        "mode": "GPU" if settings.USE_GPU else "CPU",
        "description": "GPU acceleration enabled" if settings.USE_GPU else "CPU mode - testing only, use small models"
    }

