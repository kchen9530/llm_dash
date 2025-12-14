"""
Embedding Model Handler
Handles sentence embedding models (e.g., sentence-transformers)
"""
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingModelHandler:
    """
    Handler for embedding models that convert text to vectors.
    These models output lists of floats representing the text features.
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_loaded = False
        self.embedding_dim = None
        
        # Recommended small embedding models
        self.recommended_models = {
            "sentence-transformers/all-MiniLM-L6-v2": {
                "size": "80MB",
                "dimensions": 384,
                "description": "Fast and efficient, good for general use"
            },
            "sentence-transformers/paraphrase-MiniLM-L3-v2": {
                "size": "61MB", 
                "dimensions": 384,
                "description": "Smallest, very fast"
            },
            "BAAI/bge-small-en-v1.5": {
                "size": "134MB",
                "dimensions": 384,
                "description": "High quality, English"
            },
            "sentence-transformers/all-MiniLM-L12-v2": {
                "size": "120MB",
                "dimensions": 384,
                "description": "Balanced quality and speed"
            }
        }
    
    async def load_model(self):
        """Load the embedding model"""
        try:
            # Set cache to embeddings directory
            import os
            from app.core.model_config import EMBEDDING_MODELS_DIR
            os.environ['HF_HOME'] = str(EMBEDDING_MODELS_DIR)
            os.environ['TRANSFORMERS_CACHE'] = str(EMBEDDING_MODELS_DIR)
            os.environ['HF_HUB_CACHE'] = str(EMBEDDING_MODELS_DIR)
            
            logger.info(f"Loading embedding model: {self.model_name}")
            logger.info(f"📦 Using cache: {EMBEDDING_MODELS_DIR}")
            
            # Import sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
            
            # Load model with custom cache directory
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(EMBEDDING_MODELS_DIR)
            )
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.is_loaded = True
            
            logger.info(f"✅ Embedding model loaded: {self.model_name}")
            logger.info(f"📊 Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    async def encode(self, text: str) -> List[float]:
        """
        Encode text to embedding vector
        
        Args:
            text: Input text to encode
            
        Returns:
            List of floats representing the embedding
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Get embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Convert to list of floats
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Encoding error: {e}")
            raise
    
    async def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts to embeddings
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        
        except Exception as e:
            logger.error(f"Batch encoding error: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "name": self.model_name,
            "type": "embedding",
            "is_loaded": self.is_loaded,
            "embedding_dimension": self.embedding_dim,
            "max_seq_length": self.model.max_seq_length if self.is_loaded else None,
        }
    
    def unload(self):
        """Unload model from memory"""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("Embedding model unloaded")


# Model type detection
def is_embedding_model(model_name: str) -> bool:
    """
    Detect if a model is an embedding model based on name
    """
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


# Singleton handler registry
_embedding_handlers: Dict[str, EmbeddingModelHandler] = {}


def get_embedding_handler(model_name: str) -> EmbeddingModelHandler:
    """Get or create an embedding handler"""
    if model_name not in _embedding_handlers:
        _embedding_handlers[model_name] = EmbeddingModelHandler(model_name)
    return _embedding_handlers[model_name]


def cleanup_handler(model_name: str):
    """Cleanup an embedding handler"""
    if model_name in _embedding_handlers:
        _embedding_handlers[model_name].unload()
        del _embedding_handlers[model_name]

