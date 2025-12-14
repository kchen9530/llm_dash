"""
Photo Search Service using Semantic Embeddings
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PhotoSearchService:
    """
    Semantic photo search using embeddings and cosine similarity
    """
    
    def __init__(self):
        self.photos: List[Dict[str, Any]] = []
        self.photo_embeddings: Dict[str, np.ndarray] = {}
        self.is_initialized = False
        self.embedding_model_name: Optional[str] = None
        
    def load_photo_database(self) -> bool:
        """Load photo database from JSON"""
        try:
            db_path = Path(__file__).parent.parent / "data" / "photo_database.json"
            
            if not db_path.exists():
                logger.error(f"Photo database not found at {db_path}")
                return False
            
            with open(db_path, 'r') as f:
                data = json.load(f)
                self.photos = data.get('photos', [])
            
            logger.info(f"✅ Loaded {len(self.photos)} photos from database")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load photo database: {e}")
            return False
    
    async def initialize_embeddings(self, model_name: Optional[str] = None, use_deployed: bool = True):
        """
        Initialize photo embeddings using the specified embedding model.
        Can use either a deployed model or load a new one.
        
        Args:
            model_name: Model name (if None and use_deployed=True, uses first deployed embedding model)
            use_deployed: If True, tries to use already deployed embedding models
        """
        try:
            # Load photo database if not loaded
            if not self.photos:
                if not self.load_photo_database():
                    raise ValueError("Failed to load photo database")
            
            # Try to find deployed embedding model first
            if use_deployed:
                # Import here to avoid circular dependency
                import os
                USE_LIGHTWEIGHT = os.getenv("USE_LIGHTWEIGHT_MANAGER", "true").lower() == "true"
                
                if USE_LIGHTWEIGHT:
                    from app.services.lightweight_model_manager import LightweightModelManager
                    manager = LightweightModelManager()
                    deployed_embeddings = manager.list_embedding_models()
                    
                    if deployed_embeddings and deployed_embeddings[0].status == "RUNNING":
                        # Use first deployed embedding model
                        model_info = deployed_embeddings[0]
                        model_name = model_info.model_name
                        logger.info(f"✅ Using deployed embedding model: {model_name}")
            
            # Fallback to specified model or default
            if not model_name:
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            # Get embedding handler
            from app.services.embedding_model_handler import get_embedding_handler
            handler = get_embedding_handler(model_name)
            
            # Load model if not loaded
            if not handler.is_loaded:
                logger.info(f"Loading embedding model: {model_name}")
                await handler.load_model()
            
            # Generate embeddings for all photo descriptions
            logger.info("Generating embeddings for photo descriptions...")
            descriptions = [photo['description'] for photo in self.photos]
            embeddings = await handler.encode_batch(descriptions)
            
            # Store embeddings
            for photo, embedding in zip(self.photos, embeddings):
                self.photo_embeddings[photo['id']] = np.array(embedding)
            
            self.embedding_model_name = model_name
            self.is_initialized = True
            
            logger.info(f"✅ Initialized {len(self.photo_embeddings)} photo embeddings")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Returns value between -1 and 1, where:
        1 = identical vectors
        0 = orthogonal vectors
        -1 = opposite vectors
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5,
        model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search photos using semantic similarity
        
        Args:
            query: Search query (e.g., "a black dog")
            top_k: Number of results to return
            model_name: Embedding model to use (if different from initialized)
            
        Returns:
            List of photo results with similarity scores
        """
        try:
            # Initialize if not done
            if not self.is_initialized:
                await self.initialize_embeddings(
                    model_name or "sentence-transformers/all-MiniLM-L6-v2"
                )
            
            # Get query embedding
            from app.services.embedding_model_handler import get_embedding_handler
            
            handler = get_embedding_handler(
                model_name or self.embedding_model_name
            )
            
            if not handler.is_loaded:
                await handler.load_model()
            
            query_embedding = await handler.encode(query)
            query_vec = np.array(query_embedding)
            
            # Calculate similarities
            similarities = []
            for photo in self.photos:
                photo_vec = self.photo_embeddings[photo['id']]
                similarity = self.cosine_similarity(query_vec, photo_vec)
                
                similarities.append({
                    'photo': photo,
                    'similarity': float(similarity),
                    'similarity_percent': float(similarity * 100)
                })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top K results
            results = similarities[:top_k]
            
            logger.info(f"Search query: '{query}' - Found {len(results)} results")
            
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_photo_by_id(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """Get photo metadata by ID"""
        for photo in self.photos:
            if photo['id'] == photo_id:
                return photo
        return None
    
    def get_all_photos(self) -> List[Dict[str, Any]]:
        """Get all photos in database"""
        if not self.photos:
            self.load_photo_database()
        return self.photos
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'total_photos': len(self.photos),
            'embeddings_initialized': self.is_initialized,
            'embedding_model': self.embedding_model_name,
            'embedding_dimension': len(next(iter(self.photo_embeddings.values()))) if self.photo_embeddings else 0
        }


# Singleton instance
_photo_search_service: Optional[PhotoSearchService] = None


def get_photo_search_service() -> PhotoSearchService:
    """Get or create the photo search service singleton"""
    global _photo_search_service
    if _photo_search_service is None:
        _photo_search_service = PhotoSearchService()
    return _photo_search_service

