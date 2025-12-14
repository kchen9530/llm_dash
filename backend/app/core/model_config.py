"""
Model Configuration and Recommendations
"""
from pathlib import Path
import os

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Local model storage (under project root)
MODELS_DIR = PROJECT_ROOT / "models"
CHAT_MODELS_DIR = MODELS_DIR / "chat"
EMBEDDING_MODELS_DIR = MODELS_DIR / "embeddings"

# Create directories if they don't exist
CHAT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDING_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Set HuggingFace cache to local directory - MUST be done early!
# Default to chat models directory (will be overridden for embeddings)
os.environ['HF_HOME'] = str(CHAT_MODELS_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(CHAT_MODELS_DIR)
os.environ['HF_DATASETS_CACHE'] = str(CHAT_MODELS_DIR)
os.environ['HF_HUB_CACHE'] = str(CHAT_MODELS_DIR)

print(f"🔧 HuggingFace cache (chat models): {CHAT_MODELS_DIR}")
print(f"🔧 HuggingFace cache (embeddings): {EMBEDDING_MODELS_DIR}")


# Recommended Chat Models for 8GB RAM
RECOMMENDED_CHAT_MODELS = {
    "Qwen/Qwen2-0.5B-Instruct": {
        "type": "chat",
        "size": "0.5B",
        "display_name": "Qwen2 0.5B",
        "label": "Smallest Qwen - Perfect for 8GB RAM",
        "size_mb": 950,
        "ram_mb": 1500,
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐",
        "description": "Tiny Qwen model, very fast",
        "recommended_for": "Best for 8GB RAM",
        "family": "Qwen"
    },
    "Qwen/Qwen2-1.5B-Instruct": {
        "type": "chat",
        "size": "1.5B",
        "display_name": "Qwen2 1.5B",
        "label": "Small Qwen - Good quality for 8GB",
        "size_mb": 2800,
        "ram_mb": 4000,
        "speed": "⚡⚡",
        "quality": "⭐⭐⭐",
        "description": "Small Qwen, good quality",
        "recommended_for": "8GB RAM (close other apps)",
        "family": "Qwen"
    },
    "Qwen/Qwen1.5-4B-Chat": {
        "type": "chat",
        "size": "4B",
        "display_name": "Qwen 4B",
        "label": "Medium Qwen - Better responses",
        "size_mb": 8000,
        "ram_mb": 10000,
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐",
        "description": "Medium Qwen, excellent quality",
        "recommended_for": "GPU or 16GB+ RAM",
        "family": "Qwen",
        "requires_gpu": True
    },
    "Qwen/Qwen2-7B-Instruct": {
        "type": "chat",
        "size": "7B",
        "display_name": "Qwen2 7B",
        "label": "Large Qwen - Production quality",
        "size_mb": 14000,
        "ram_mb": 16000,
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Large Qwen, production quality",
        "recommended_for": "GPU server only",
        "family": "Qwen",
        "requires_gpu": True
    },
    "distilgpt2": {
        "type": "chat",
        "size": "82M",
        "display_name": "DistilGPT2",
        "label": "Minimal model for quick testing",
        "size_mb": 350,
        "ram_mb": 600,
        "speed": "⚡⚡⚡",
        "quality": "⭐",
        "description": "Smallest GPT-2, very basic",
        "recommended_for": "Quick testing only",
        "family": "GPT-2"
    },
    "gpt2": {
        "type": "chat",
        "size": "124M",
        "display_name": "GPT-2",
        "label": "Basic GPT-2 for demos",
        "size_mb": 500,
        "ram_mb": 800,
        "speed": "⚡⚡",
        "quality": "⭐⭐",
        "description": "Basic GPT-2 model",
        "recommended_for": "Testing and demos",
        "family": "GPT-2"
    },
}


# Recommended Embedding Models for 8GB RAM
RECOMMENDED_EMBEDDING_MODELS = {
    "sentence-transformers/paraphrase-MiniLM-L3-v2": {
        "type": "embedding",
        "size": "61MB",
        "size_mb": 61,
        "ram_mb": 200,
        "dimensions": 384,
        "speed": "⚡⚡⚡",
        "description": "Smallest, very fast",
        "recommended_for": "Quick testing",
        "family": "MiniLM"
    },
    "sentence-transformers/all-MiniLM-L6-v2": {
        "type": "embedding",
        "size": "80MB",
        "size_mb": 80,
        "ram_mb": 250,
        "dimensions": 384,
        "speed": "⚡⚡",
        "description": "Best balance (RECOMMENDED)",
        "recommended_for": "Photo search, semantic search",
        "family": "MiniLM"
    },
    "sentence-transformers/all-MiniLM-L12-v2": {
        "type": "embedding",
        "size": "120MB",
        "size_mb": 120,
        "ram_mb": 300,
        "dimensions": 384,
        "speed": "⚡",
        "description": "Better quality",
        "recommended_for": "High-quality embeddings",
        "family": "MiniLM"
    },
    "BAAI/bge-small-en-v1.5": {
        "type": "embedding",
        "size": "134MB",
        "size_mb": 134,
        "ram_mb": 350,
        "dimensions": 384,
        "speed": "⚡",
        "description": "Highest quality for English",
        "recommended_for": "Production embeddings",
        "family": "BGE"
    },
    "BAAI/bge-base-en-v1.5": {
        "type": "embedding",
        "size": "438MB",
        "size_mb": 438,
        "ram_mb": 800,
        "dimensions": 768,
        "speed": "⚡",
        "description": "Larger, better quality",
        "recommended_for": "High-quality production use",
        "family": "BGE"
    },
}


def is_embedding_model(model_name: str) -> bool:
    """
    Detect if a model is an embedding model
    """
    # Check if in recommended embedding models
    if model_name in RECOMMENDED_EMBEDDING_MODELS:
        return True
    
    # Check by name patterns
    embedding_indicators = [
        'sentence-transformers',
        'bge-',
        'gte-',
        'e5-',
        'embed',
        'embedding',
        'mpnet',
        'minilm',
        'retrieval',
    ]
    
    model_lower = model_name.lower()
    return any(indicator in model_lower for indicator in embedding_indicators)


def is_chat_model(model_name: str) -> bool:
    """
    Detect if a model is a chat/LLM model
    """
    return not is_embedding_model(model_name)


def get_all_recommended_models():
    """
    Get all recommended models with download status.
    Merges recommendations with what's actually downloaded.
    """
    downloaded = get_downloaded_models()
    
    # Create sets of downloaded model names for quick lookup
    downloaded_chat_names = {m["name"] for m in downloaded["chat"]}
    downloaded_embed_names = {m["name"] for m in downloaded["embedding"]}
    
    # Add download status to chat models
    chat_models_with_status = {}
    for name, info in RECOMMENDED_CHAT_MODELS.items():
        chat_models_with_status[name] = {
            **info,
            "downloaded": name in downloaded_chat_names,
            "download_size": next((m["size"] for m in downloaded["chat"] if m["name"] == name), None)
        }
    
    # Add download status to embedding models
    embedding_models_with_status = {}
    for name, info in RECOMMENDED_EMBEDDING_MODELS.items():
        embedding_models_with_status[name] = {
            **info,
            "downloaded": name in downloaded_embed_names,
            "download_size": next((m["size"] for m in downloaded["embedding"] if m["name"] == name), None)
        }
    
    return {
        "chat_models": chat_models_with_status,
        "embedding_models": embedding_models_with_status,
        "note": "Models sorted by size (small to large)",
        "downloaded_count": {
            "chat": len(downloaded_chat_names),
            "embedding": len(downloaded_embed_names)
        }
    }


def get_downloaded_models():
    """
    Scan models/chat and models/embeddings directories to find downloaded models.
    Returns dict with 'chat' and 'embedding' lists of model names.
    """
    import re
    
    downloaded = {
        "chat": [],
        "embedding": []
    }
    
    # Scan chat models directory
    if CHAT_MODELS_DIR.exists():
        for model_dir in CHAT_MODELS_DIR.iterdir():
            if model_dir.is_dir() and model_dir.name.startswith("models--"):
                # Extract model name from directory (e.g., models--gpt2 -> gpt2)
                # or models--Qwen--Qwen2-0.5B-Instruct -> Qwen/Qwen2-0.5B-Instruct
                model_name = model_dir.name.replace("models--", "").replace("--", "/")
                
                # Check if it's actually downloaded (has snapshots)
                snapshots_dir = model_dir / "snapshots"
                if snapshots_dir.exists() and any(snapshots_dir.iterdir()):
                    downloaded["chat"].append({
                        "name": model_name,
                        "path": str(model_dir),
                        "size": _get_dir_size(model_dir)
                    })
    
    # Scan embedding models directory
    if EMBEDDING_MODELS_DIR.exists():
        for model_dir in EMBEDDING_MODELS_DIR.iterdir():
            if model_dir.is_dir() and model_dir.name.startswith("models--"):
                model_name = model_dir.name.replace("models--", "").replace("--", "/")
                
                snapshots_dir = model_dir / "snapshots"
                if snapshots_dir.exists() and any(snapshots_dir.iterdir()):
                    downloaded["embedding"].append({
                        "name": model_name,
                        "path": str(model_dir),
                        "size": _get_dir_size(model_dir)
                    })
    
    return downloaded


def _get_dir_size(path: Path) -> str:
    """Get human-readable directory size"""
    try:
        import subprocess
        result = subprocess.run(
            ["du", "-sh", str(path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception:
        pass
    return "?"

