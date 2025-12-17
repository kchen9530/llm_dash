"""
Lightweight CPU Model Runner for Mac (8GB RAM)
Alternative to vLLM for testing with tiny models
"""
import asyncio
import torch
import queue
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
    
    def _load_tokenizer_sync(self, chat_models_dir):
        """Synchronous tokenizer loading - runs in thread pool"""
        return AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            cache_dir=str(chat_models_dir)
        )
    
    def _load_model_sync(self, chat_models_dir):
        """Synchronous model loading - runs in thread pool"""
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,  # Use FP32 for CPU
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            cache_dir=str(chat_models_dir)
        )
        # Move to CPU explicitly
        return model.to(self.device)
    
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
            
            # Run blocking operations in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            
            # Load tokenizer in thread pool (non-blocking)
            logger.info("📥 Downloading/loading tokenizer...")
            self.tokenizer = await loop.run_in_executor(
                None,  # Use default thread pool
                self._load_tokenizer_sync,
                CHAT_MODELS_DIR
            )
            
            # Load model in thread pool (non-blocking)
            logger.info("📥 Downloading/loading model weights (this takes longest)...")
            self.model = await loop.run_in_executor(
                None,  # Use default thread pool
                self._load_model_sync,
                CHAT_MODELS_DIR
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
            
        except asyncio.CancelledError:
            logger.info(f"⚠️  Model loading cancelled: {self.model_name}")
            # Clean up any partially loaded resources
            if self.model:
                del self.model
            if self.tokenizer:
                del self.tokenizer
            self.is_loaded = False
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def _generate_sync(self, inputs, safe_max_new_tokens, model_max_length, temperature, pad_token_id):
        """Synchronous generation - runs in thread pool"""
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=safe_max_new_tokens,
                max_length=model_max_length,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=pad_token_id,
            )
        return outputs
    
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
            # Get model's maximum length (default to 1024 for safety)
            model_max_length = getattr(self.model.config, 'max_position_embeddings', 1024)
            if hasattr(self.model.config, 'n_positions'):
                model_max_length = self.model.config.n_positions
            
            # Tokenize and truncate input to leave room for generation
            max_input_length = model_max_length - max_new_tokens - 10  # 10 token buffer
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt",
                max_length=max_input_length,
                truncation=True
            )
            
            input_length = inputs['input_ids'].shape[1]
            logger.info(f"Input tokens: {input_length}, Max new tokens: {max_new_tokens}, Model max: {model_max_length}")
            
            # Ensure we don't exceed model's maximum length
            safe_max_new_tokens = min(max_new_tokens, model_max_length - input_length - 1)
            if safe_max_new_tokens < max_new_tokens:
                logger.warning(f"⚠️  Reduced max_new_tokens from {max_new_tokens} to {safe_max_new_tokens} to fit model's context")
            
            if stream:
                # Streaming generation
                streamer = TextIteratorStreamer(
                    self.tokenizer, 
                    skip_prompt=True,
                    skip_special_tokens=True
                )
                
                generation_kwargs = dict(
                    **inputs,
                    max_new_tokens=safe_max_new_tokens,
                    max_length=model_max_length,  # Enforce hard limit
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.eos_token_id,  # Set pad token
                    streamer=streamer,
                )
                
                # Run generation in a separate thread (non-blocking)
                thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
                thread.start()
                
                # Yield tokens as they come (with small delays to avoid blocking)
                # Access the internal queue with timeout to make it non-blocking
                while True:
                    try:
                        # Use a timeout to periodically yield control to event loop
                        text = streamer.text_queue.get(timeout=0.01)
                        if text is None:  # End of generation signal
                            break
                        yield text
                        await asyncio.sleep(0)  # Yield control to event loop
                    except queue.Empty:
                        # No text yet, yield control and continue waiting
                        await asyncio.sleep(0.01)
                        continue
                    except Exception as e:
                        logger.error(f"Streaming error: {e}")
                        break
                
                # Make sure thread completes
                thread.join(timeout=1.0)
            else:
                # Non-streaming generation - run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                outputs = await loop.run_in_executor(
                    None,  # Use default thread pool
                    self._generate_sync,
                    inputs,
                    safe_max_new_tokens,
                    model_max_length,
                    temperature,
                    self.tokenizer.eos_token_id
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

