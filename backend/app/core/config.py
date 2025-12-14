"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import subprocess


def detect_gpu() -> bool:
    """检测是否有可用的 NVIDIA GPU"""
    try:
        result = subprocess.run(
            ["nvidia-smi"], 
            capture_output=True, 
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "LLM Local Ops Center"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # 模型存储路径
    MODEL_CACHE_DIR: str = "/root/.cache/huggingface/hub"
    
    # vLLM 配置
    VLLM_BASE_PORT: int = 8000
    VLLM_MAX_INSTANCES: int = 5
    
    # GPU/CPU 模式配置
    # 🔧 FEATURE SWITCH: Set FORCE_CPU_MODE=False when GPU is available
    FORCE_CPU_MODE: bool = True  # Set to False to enable GPU when available
    USE_GPU: bool = False  # Auto-detected, don't set manually
    
    # WebSocket 配置
    WS_HEARTBEAT_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-detect GPU unless forced to CPU mode
        if not self.FORCE_CPU_MODE:
            self.USE_GPU = detect_gpu()
            if self.USE_GPU:
                print("✅ GPU detected and enabled")
            else:
                print("⚠️  No GPU detected, using CPU mode")
        else:
            self.USE_GPU = False
            print("ℹ️  CPU mode forced via config (FORCE_CPU_MODE=True)")


settings = Settings()

