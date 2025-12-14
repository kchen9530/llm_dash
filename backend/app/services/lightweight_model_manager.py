"""
Lightweight Model Manager for 8GB RAM Macs
Uses transformers directly instead of vLLM
Supports both chat models and embedding models
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
import logging

from app.models.schemas import ModelInfo, ModelStatus, DeployRequest
from app.services.cpu_model_runner import CPUModelRunner
from app.services.model_logger import model_logger
from app.core.model_config import (
    is_embedding_model, 
    is_chat_model,
    CHAT_MODELS_DIR,
    EMBEDDING_MODELS_DIR
)

logger = logging.getLogger(__name__)


class LightweightModelInstance:
    """Lightweight model instance using transformers"""
    
    def __init__(self, model_id: str, model_name: str, port: int, parameters: Dict):
        self.model_id = model_id
        self.model_name = model_name
        self.port = port  # Not actually used for direct inference
        self.parameters = parameters
        self.status = ModelStatus.INITIALIZING
        self.start_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.runner: Optional[CPUModelRunner] = None
        self.model_type = "embedding" if is_embedding_model(model_name) else "chat"
        self.embedding_handler = None  # For embedding models
        
    def to_model_info(self) -> ModelInfo:
        """Convert to ModelInfo schema"""
        return ModelInfo(
            id=self.model_id,
            model_name=self.model_name,
            status=self.status,
            pid=None,  # No subprocess
            port=self.port,
            start_time=self.start_time,
            error_message=self.error_message,
            parameters=self.parameters,
        )


class LightweightModelManager:
    """
    Simplified model manager for 8GB RAM systems.
    Loads models directly with transformers instead of spawning vLLM processes.
    """
    
    _instance = None
    _instances: Dict[str, LightweightModelInstance] = {}
    _next_port = 8000
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._instances = {}
            self._next_port = 8000
    
    def _generate_model_id(self, model_name: str) -> str:
        """Generate unique model ID"""
        model_short_name = model_name.split("/")[-1]
        timestamp = datetime.now().strftime("%H%M%S")
        return f"{model_short_name}-{timestamp}"
    
    async def deploy_model(self, request: DeployRequest) -> ModelInfo:
        """
        Deploy a model (load into memory)
        
        Recommended tiny models for 8GB RAM:
        - gpt2 (124M, ~500MB)
        - distilgpt2 (82M, ~350MB)  
        - gpt2-medium (355M, ~1.5GB) - if nothing else running
        """
        try:
            # Check if too many models loaded
            if len(self._instances) >= 3:
                raise ValueError("Maximum 3 models on 8GB RAM. Please delete some first.")
            
            # Generate model ID
            model_id = self._generate_model_id(request.model_name)
            
            # Allocate port (not used but kept for compatibility)
            port = self._next_port
            self._next_port += 1
            
            # Create instance
            instance = LightweightModelInstance(
                model_id=model_id,
                model_name=request.model_name,
                port=port,
                parameters=request.parameters or {}
            )
            
            self._instances[model_id] = instance
            
            # Add initial log
            model_logger.add_log(model_id, f"Deployment started for {request.model_name}", "INFO")
            
            # Load model asynchronously
            asyncio.create_task(self._load_model(instance))
            
            logger.info(f"📦 Started loading model: {model_id}")
            model_logger.add_log(model_id, f"📦 Started loading model: {model_id}", "INFO")
            
            return instance.to_model_info()
        
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
    
    async def _load_model(self, instance: LightweightModelInstance):
        """Load model into memory (chat or embedding)"""
        try:
            instance.status = ModelStatus.STARTING
            instance.start_time = datetime.now()
            
            logger.info(f"⏳ Loading {instance.model_name} ({instance.model_type})...")
            model_logger.add_log(instance.model_id, f"⏳ Loading {instance.model_name} ({instance.model_type})...", "INFO")
            
            logger.info(f"   This may take 1-3 minutes on first download")
            model_logger.add_log(instance.model_id, "This may take 1-3 minutes on first download", "INFO")
            
            if instance.model_type == "embedding":
                # Load embedding model
                from app.services.embedding_model_handler import get_embedding_handler
                
                model_logger.add_log(instance.model_id, "Loading embedding model...", "INFO")
                handler = get_embedding_handler(instance.model_name)
                await handler.load_model()
                instance.embedding_handler = handler
                
                logger.info(f"✅ Embedding model {instance.model_id} is ready!")
                model_logger.add_log(instance.model_id, f"✅ Embedding model ready! Dimensions: {handler.embedding_dim}", "INFO")
                logger.info(f"   Dimensions: {handler.embedding_dim}")
            else:
                # Load chat model
                max_length = instance.parameters.get("max_model_len", 512)
                model_logger.add_log(instance.model_id, f"Creating model runner (max_length: {min(max_length, 512)})", "INFO")
                
                instance.runner = CPUModelRunner(
                    model_name=instance.model_name,
                    max_length=min(max_length, 512)  # Limit for 8GB RAM
                )
                
                # Load model
                model_logger.add_log(instance.model_id, "Downloading/loading model weights...", "INFO")
                await instance.runner.load_model()
                
                logger.info(f"✅ Chat model {instance.model_id} is ready!")
                model_logger.add_log(instance.model_id, f"✅ Chat model ready! Model loaded successfully.", "INFO")
            
            instance.status = ModelStatus.RUNNING
            model_logger.add_log(instance.model_id, f"🚀 Model {instance.model_id} is now RUNNING", "INFO")
            
        except Exception as e:
            instance.status = ModelStatus.FAILED
            instance.error_message = str(e)
            logger.error(f"❌ Failed to load {instance.model_id}: {e}")
            model_logger.add_log(instance.model_id, f"❌ Failed to load model: {str(e)}", "ERROR")
    
    async def generate(
        self, 
        model_id: str, 
        prompt: str, 
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text from a loaded model
        """
        instance = self._instances.get(model_id)
        if not instance:
            raise ValueError(f"Model {model_id} not found")
        
        if instance.status != ModelStatus.RUNNING:
            raise ValueError(f"Model {model_id} is not running (status: {instance.status})")
        
        if not instance.runner:
            raise ValueError(f"Model {model_id} has no runner")
        
        # Generate text
        result = []
        async for chunk in instance.runner.generate(
            prompt=prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            stream=False
        ):
            result.append(chunk)
        
        return "".join(result)
    
    async def generate_stream(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7
    ):
        """
        Generate text with streaming
        """
        instance = self._instances.get(model_id)
        if not instance:
            raise ValueError(f"Model {model_id} not found")
        
        if instance.status != ModelStatus.RUNNING:
            raise ValueError(f"Model {model_id} is not running")
        
        if not instance.runner:
            raise ValueError(f"Model {model_id} has no runner")
        
        # Stream generation
        async for chunk in instance.runner.generate(
            prompt=prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            stream=True
        ):
            yield chunk
    
    async def stop_model(self, model_id: str) -> bool:
        """Stop/unload a model"""
        instance = self._instances.get(model_id)
        if not instance:
            raise ValueError(f"Model {model_id} not found")
        
        try:
            instance.status = ModelStatus.STOPPING
            
            if instance.runner:
                instance.runner.unload_model()
            
            if instance.embedding_handler:
                instance.embedding_handler.unload()
            
            instance.status = ModelStatus.STOPPED
            logger.info(f"🛑 Model {model_id} stopped")
            
            return True
        
        except Exception as e:
            instance.error_message = f"Stop failed: {str(e)}"
            logger.error(f"❌ Failed to stop {model_id}: {e}")
            return False
    
    async def remove_model(self, model_id: str) -> bool:
        """Remove model instance"""
        if model_id in self._instances:
            await self.stop_model(model_id)
            del self._instances[model_id]
            logger.info(f"🗑️  Model {model_id} removed")
            return True
        return False
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info"""
        instance = self._instances.get(model_id)
        return instance.to_model_info() if instance else None
    
    def list_models(self) -> List[ModelInfo]:
        """List all models"""
        return [inst.to_model_info() for inst in self._instances.values()]
    
    def list_chat_models(self) -> List[ModelInfo]:
        """List only chat models (exclude embeddings)"""
        return [
            inst.to_model_info() 
            for inst in self._instances.values() 
            if inst.model_type == "chat"
        ]
    
    def list_embedding_models(self) -> List[ModelInfo]:
        """List only embedding models"""
        return [
            inst.to_model_info()
            for inst in self._instances.values()
            if inst.model_type == "embedding"
        ]
    
    def get_model_logs(self, model_id: str) -> List[str]:
        """Get logs for a specific model"""
        return model_logger.get_logs(model_id)
    
    def get_logs(self, model_id: str, lines: int = 100) -> List[str]:
        """Get model logs (simplified - returns status info)"""
        instance = self._instances.get(model_id)
        if not instance:
            return []
        
        logs = [
            f"Model ID: {instance.model_id}",
            f"Model Name: {instance.model_name}",
            f"Status: {instance.status}",
            f"Start Time: {instance.start_time}",
        ]
        
        if instance.error_message:
            logs.append(f"Error: {instance.error_message}")
        
        if instance.status == ModelStatus.RUNNING:
            logs.append("✅ Model is loaded and ready for inference")
            logs.append("⚠️  Note: CPU inference is slow (~2-5 sec per response)")
        
        return logs
    
    async def cleanup_all(self):
        """Cleanup all instances"""
        for model_id in list(self._instances.keys()):
            await self.stop_model(model_id)


# Recommended tiny models for 8GB RAM
RECOMMENDED_TINY_MODELS = {
    "gpt2": {
        "size": "124M parameters (~500MB)",
        "speed": "⚡⚡ Fast",
        "quality": "⭐⭐ Basic",
        "description": "Smallest GPT-2, good for testing"
    },
    "distilgpt2": {
        "size": "82M parameters (~350MB)",
        "speed": "⚡⚡⚡ Very Fast",
        "quality": "⭐ Basic",
        "description": "Distilled GPT-2, fastest option"
    },
    "gpt2-medium": {
        "size": "355M parameters (~1.5GB)",
        "speed": "⚡ Medium",
        "quality": "⭐⭐⭐ Better",
        "description": "Better quality, needs more RAM"
    },
}

