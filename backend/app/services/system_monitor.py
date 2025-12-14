"""
系统监控服务
"""
import psutil
from typing import List, Dict, Any

try:
    import pynvml
    HAS_NVIDIA = True
except ImportError:
    HAS_NVIDIA = False

from app.models.schemas import SystemStatus, GPUInfo


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self._nvml_initialized = False
        if HAS_NVIDIA:
            try:
                pynvml.nvmlInit()
                self._nvml_initialized = True
            except Exception as e:
                print(f"⚠️ NVML 初始化失败: {e}")
    
    def get_system_status(self) -> SystemStatus:
        """获取系统状态"""
        # CPU 和内存
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU 信息
        gpu_info = self.get_gpu_info()
        
        return SystemStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_total_gb=memory.total / (1024**3),
            gpu_info=gpu_info,
        )
    
    def get_gpu_info(self) -> List[Dict[str, Any]]:
        """获取 GPU 信息"""
        if not self._nvml_initialized:
            return []
        
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            gpu_list = []
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                name = pynvml.nvmlDeviceGetName(handle)
                
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(
                        handle, pynvml.NVML_TEMPERATURE_GPU
                    )
                except:
                    temperature = None
                
                gpu_list.append({
                    "id": i,
                    "name": name if isinstance(name, str) else name.decode('utf-8'),
                    "memory_used_mb": info.used / (1024**2),
                    "memory_total_mb": info.total / (1024**2),
                    "memory_percent": (info.used / info.total) * 100,
                    "utilization_percent": utilization.gpu,
                    "temperature": temperature,
                })
            
            return gpu_list
        
        except Exception as e:
            print(f"获取 GPU 信息失败: {e}")
            return []
    
    def __del__(self):
        """清理"""
        if self._nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# 单例
system_monitor = SystemMonitor()

