"""
Lightweight CPU Model Runner for Mac (8GB RAM)
Alternative to vLLM for testing with tiny models
"""
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CPUModelRunner:
    """
    Lightweight model runner for CPU inference with tiny models
    Suitable for 8GB RAM Macs - only for testing/demo purposes
    """
    
    def __init__(self, model_name: str, max_length: int = 512):
        self.model_name = model_name
        self.max_length = max_length
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.device = "cpu"
        self.is_loaded = False
        
        # Recommended tiny models for 8GB RAM
        self.recommended_models = [
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # ~2GB RAM
            "Qwen/Qwen2-0.5B-Instruct",             # ~1GB RAM
            "facebook/opt-125m",                     # ~500MB RAM
            "gpt2",                                  # ~500MB RAM
        ]
    
    async def load_model(self):
        """Load model in CPU mode with minimal memory"""
        try:
            # Set cache to chat models directory
            import os
            from app.core.model_config import CHAT_MODELS_DIR
            os.environ['HF_HOME'] = str(CHAT_MODELS_DIR)
            os.environ['TRANSFORMERS_CACHE'] = str(CHAT_MODELS_DIR)
            os.environ['HF_HUB_CACHE'] = str(CHAT_MODELS_DIR)
            
            logger.info(f"Loading {self.model_name} on CPU (this may take a few minutes)...")
            logger.info(f"📦 Using cache: {CHAT_MODELS_DIR}")
            
            # Load with minimal settings for 8GB RAM
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=str(CHAT_MODELS_DIR)
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use FP32 for CPU
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="cpu",
                cache_dir=str(CHAT_MODELS_DIR)
            )
            
            self.model.eval()  # Set to evaluation mode
            self.is_loaded = True
            
            logger.info(f"✅ Model {self.model_name} loaded successfully on CPU")
            
            # Estimate memory usage
            param_count = sum(p.numel() for p in self.model.parameters())
            memory_mb = (param_count * 4) / (1024 ** 2)  # 4 bytes per float32
            logger.info(f"📊 Estimated model size: {memory_mb:.0f} MB")
            
            if memory_mb > 3000:
                logger.warning(f"⚠️  Model is large ({memory_mb:.0f}MB). May be slow on CPU with 8GB RAM.")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    async def generate(
        self, 
        prompt: str, 
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        stream: bool = False
    ):
        """Generate text from prompt"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            if stream:
                # Streaming generation
                streamer = TextIteratorStreamer(
                    self.tokenizer, 
                    skip_prompt=True,
                    skip_special_tokens=True
                )
                
                generation_kwargs = dict(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    streamer=streamer,
                )
                
                # Run generation in thread
                thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
                thread.start()
                
                # Yield tokens as they come
                for text in streamer:
                    yield text
                
                thread.join()
            else:
                # Non-streaming generation
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        do_sample=temperature > 0,
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remove the prompt from response
                response = response[len(prompt):].strip()
                yield response
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def unload_model(self):
        """Free memory"""
        if self.model:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            self.is_loaded = False
            logger.info("Model unloaded from memory")


# Singleton instance
_runner_instance: Optional[CPUModelRunner] = None


def get_model_runner(model_name: str = "gpt2") -> CPUModelRunner:
    """Get or create model runner instance"""
    global _runner_instance
    if _runner_instance is None or _runner_instance.model_name != model_name:
        _runner_instance = CPUModelRunner(model_name)
    return _runner_instance

