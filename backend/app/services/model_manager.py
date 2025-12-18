"""
模型进程管理器 - 核心组件
"""
import asyncio
import subprocess
import time
from datetime import datetime
from typing import Dict, Optional, List
import psutil
import signal
from pathlib import Path

from app.types.schemas import ModelInfo, ModelStatus, DeployRequest
from app.core.config import settings


class ModelInstance:
    """模型实例"""
    
    def __init__(
        self,
        model_id: str,
        model_name: str,
        port: int,
        parameters: Dict,
    ):
        self.model_id = model_id
        self.model_name = model_name
        self.port = port
        self.parameters = parameters
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.status = ModelStatus.INITIALIZING
        self.start_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.log_buffer: List[str] = []
        
    def to_model_info(self) -> ModelInfo:
        """转换为 ModelInfo"""
        return ModelInfo(
            id=self.model_id,
            model_name=self.model_name,
            status=self.status,
            pid=self.pid,
            port=self.port,
            start_time=self.start_time,
            error_message=self.error_message,
            parameters=self.parameters,
        )


class ModelManager:
    """模型管理器（单例模式）"""
    
    _instance = None
    _instances: Dict[str, ModelInstance] = {}
    _used_ports: set = set()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._instances = {}
            self._used_ports = set()
            self._next_port = settings.VLLM_BASE_PORT
    
    def _allocate_port(self, preferred_port: Optional[int] = None) -> int:
        """分配可用端口"""
        if preferred_port and preferred_port not in self._used_ports:
            self._used_ports.add(preferred_port)
            return preferred_port
        
        # 自动分配
        while self._next_port in self._used_ports:
            self._next_port += 1
        
        port = self._next_port
        self._used_ports.add(port)
        self._next_port += 1
        return port
    
    def _generate_model_id(self, model_name: str, port: int) -> str:
        """生成模型实例 ID"""
        model_short_name = model_name.split("/")[-1]
        return f"{model_short_name}-{port}"
    
    async def deploy_model(self, request: DeployRequest) -> ModelInfo:
        """
        部署模型
        """
        # 检查实例数量限制
        if len(self._instances) >= settings.VLLM_MAX_INSTANCES:
            raise ValueError(f"已达到最大实例数量限制: {settings.VLLM_MAX_INSTANCES}")
        
        # 分配端口
        port = self._allocate_port(request.port)
        
        # 生成实例 ID
        model_id = self._generate_model_id(request.model_name, port)
        
        # 检查是否已存在
        if model_id in self._instances:
            raise ValueError(f"模型实例 {model_id} 已存在")
        
        # 创建实例对象
        instance = ModelInstance(
            model_id=model_id,
            model_name=request.model_name,
            port=port,
            parameters=request.parameters or {},
        )
        
        self._instances[model_id] = instance
        
        # 异步启动进程
        asyncio.create_task(self._start_vllm_process(instance, request))
        
        return instance.to_model_info()
    
    async def _start_vllm_process(self, instance: ModelInstance, request: DeployRequest):
        """
        启动 vLLM 进程
        """
        try:
            instance.status = ModelStatus.STARTING
            instance.start_time = datetime.now()
            
            # 构建 vLLM 命令
            model_path = request.local_path or request.model_name
            
            cmd = [
                "python", "-m", "vllm.entrypoints.openai.api_server",
                "--model", model_path,
                "--port", str(instance.port),
                "--host", "0.0.0.0",
            ]
            
            # 🔧 GPU/CPU Mode Configuration
            if settings.USE_GPU:
                print(f"🚀 Deploying {model_path} on GPU")
                # GPU-specific parameters
                params = instance.parameters
                if "dtype" in params:
                    cmd.extend(["--dtype", params["dtype"]])
                if "gpu_memory_utilization" in params:
                    cmd.extend(["--gpu-memory-utilization", str(params["gpu_memory_utilization"])])
            else:
                print(f"🖥️  Deploying {model_path} on CPU (testing mode - minimal memory)")
                # CPU-specific parameters with minimal memory usage
                cmd.extend([
                    "--device", "cpu",
                    "--dtype", "float32",
                    "--swap-space", "0",  # Disable swap space
                    "--max-num-seqs", "1",  # Process one request at a time
                    "--enforce-eager",  # Disable CUDA graphs
                ])
                # Note: GPU memory utilization is ignored in CPU mode
            
            # Common parameters
            params = instance.parameters
            # For CPU mode, override max_model_len to a smaller value if not specified
            max_len = params.get("max_model_len", 4096)
            if not settings.USE_GPU and max_len > 2048:
                max_len = 2048  # Limit context length in CPU mode to save memory
                print(f"⚠️  Reduced max_model_len to {max_len} for CPU mode")
            cmd.extend(["--max-model-len", str(max_len)])
            
            if params.get("trust_remote_code"):
                cmd.append("--trust-remote-code")
            
            # 启动进程
            instance.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            
            instance.pid = instance.process.pid
            instance.status = ModelStatus.RUNNING
            
            # 异步读取日志
            asyncio.create_task(self._read_process_logs(instance))
            
        except Exception as e:
            instance.status = ModelStatus.FAILED
            instance.error_message = str(e)
            print(f"❌ 启动模型失败: {e}")
    
    async def _read_process_logs(self, instance: ModelInstance):
        """读取进程日志"""
        try:
            if not instance.process or not instance.process.stdout:
                return
            
            loop = asyncio.get_event_loop()
            
            while True:
                line = await loop.run_in_executor(
                    None, instance.process.stdout.readline
                )
                
                if not line:
                    # 进程结束
                    if instance.process.poll() is not None:
                        instance.status = ModelStatus.STOPPED
                        break
                    await asyncio.sleep(0.1)
                    continue
                
                # 保存日志
                instance.log_buffer.append(line.strip())
                
                # 限制日志缓冲区大小
                if len(instance.log_buffer) > 1000:
                    instance.log_buffer = instance.log_buffer[-1000:]
                
                # 检测启动完成
                if "Application startup complete" in line or "Uvicorn running" in line:
                    instance.status = ModelStatus.RUNNING
                
                # 检测错误
                if "error" in line.lower() and instance.status == ModelStatus.STARTING:
                    instance.status = ModelStatus.ERROR
                    instance.error_message = line.strip()
        
        except Exception as e:
            print(f"读取日志出错: {e}")
    
    async def stop_model(self, model_id: str) -> bool:
        """停止模型"""
        instance = self._instances.get(model_id)
        if not instance:
            raise ValueError(f"模型实例 {model_id} 不存在")
        
        if not instance.process or not instance.pid:
            # 已经停止
            instance.status = ModelStatus.STOPPED
            return True
        
        try:
            instance.status = ModelStatus.STOPPING
            
            # 尝试优雅关闭
            process = psutil.Process(instance.pid)
            process.terminate()
            
            # 等待最多 10 秒
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # 强制杀死
                process.kill()
                process.wait(timeout=5)
            
            instance.status = ModelStatus.STOPPED
            instance.pid = None
            
            # 释放端口
            self._used_ports.discard(instance.port)
            
            return True
        
        except Exception as e:
            instance.error_message = f"停止失败: {str(e)}"
            return False
    
    async def remove_model(self, model_id: str) -> bool:
        """移除模型实例"""
        if model_id in self._instances:
            # 先停止
            await self.stop_model(model_id)
            # 从字典中移除
            del self._instances[model_id]
            return True
        return False
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        instance = self._instances.get(model_id)
        return instance.to_model_info() if instance else None
    
    def list_models(self) -> List[ModelInfo]:
        """列出所有模型"""
        return [inst.to_model_info() for inst in self._instances.values()]
    
    def get_logs(self, model_id: str, lines: int = 100) -> List[str]:
        """获取模型日志"""
        instance = self._instances.get(model_id)
        if not instance:
            return []
        return instance.log_buffer[-lines:]
    
    async def cleanup_all(self):
        """清理所有实例"""
        for model_id in list(self._instances.keys()):
            await self.stop_model(model_id)

