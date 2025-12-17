"""
Embedding Model Router
Handle embedding model operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.embedding_model_handler import (
    get_embedding_handler,
    is_embedding_model,
    cleanup_handler
)

router = APIRouter()


class EmbedRequest(BaseModel):
    """Request for text embedding"""
    model_name: str
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "text": "This is a sample sentence"
            }
        }


class EmbedBatchRequest(BaseModel):
    """Request for batch text embedding"""
    model_name: str
    texts: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "texts": ["First sentence", "Second sentence"]
            }
        }


class EmbedResponse(BaseModel):
    """Response with embedding vector"""
    embedding: List[float]
    dimension: int
    model: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "embedding": [0.123, -0.456, 0.789],
                "dimension": 384,
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }


class EmbedBatchResponse(BaseModel):
    """Response with multiple embedding vectors"""
    embeddings: List[List[float]]
    dimension: int
    model: str
    count: int


@router.post("/embed", response_model=EmbedResponse)
async def embed_text(request: EmbedRequest):
    """
    Get embedding vector for text.
    Returns a list of floats representing the text features.
    
    Example:
        Input: "this is a cat"
        Output: [0.123, -0.456, 0.789, ...] (384 dimensions)
    """
    try:
        # Get or create handler
        handler = get_embedding_handler(request.model_name)
        
        # Load model if not loaded
        if not handler.is_loaded:
            await handler.load_model()
        
        # Get embedding
        embedding = await handler.encode(request.text)
        
        return EmbedResponse(
            embedding=embedding,
            dimension=len(embedding),
            model=request.model_name
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"sentence-transformers not installed. Run: pip install sentence-transformers"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")


@router.post("/embed/batch", response_model=EmbedBatchResponse)
async def embed_texts_batch(request: EmbedBatchRequest):
    """
    Get embedding vectors for multiple texts.
    More efficient than calling /embed multiple times.
    """
    try:
        handler = get_embedding_handler(request.model_name)
        
        if not handler.is_loaded:
            await handler.load_model()
        
        embeddings = await handler.encode_batch(request.texts)
        
        return EmbedBatchResponse(
            embeddings=embeddings,
            dimension=len(embeddings[0]) if embeddings else 0,
            model=request.model_name,
            count=len(embeddings)
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=400,
            detail=f"sentence-transformers not installed. Run: pip install sentence-transformers"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")


@router.get("/models/recommended")
async def get_recommended_embedding_models():
    """
    Get list of recommended small embedding models.
    These are optimized for 8GB RAM systems.
    """
    handler = get_embedding_handler("dummy")  # Just to get recommendations
    
    return {
        "recommended": handler.recommended_models,
        "note": "These models are lightweight and work well on 8GB RAM"
    }


@router.post("/models/{model_name}/load")
async def load_embedding_model(model_name: str):
    """
    Pre-load an embedding model.
    Useful for warming up the model before use.
    """
    try:
        handler = get_embedding_handler(model_name)
        
        if handler.is_loaded:
            return {
                "status": "already_loaded",
                "model": model_name,
                "info": handler.get_model_info()
            }
        
        await handler.load_model()
        
        return {
            "status": "loaded",
            "model": model_name,
            "info": handler.get_model_info()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.delete("/models/{model_name}")
async def unload_embedding_model(model_name: str):
    """
    Unload an embedding model from memory.
    """
    try:
        cleanup_handler(model_name)
        return {"status": "unloaded", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unload: {str(e)}")


@router.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """
    Get information about an embedding model.
    """
    handler = get_embedding_handler(model_name)
    
    if not handler.is_loaded:
        return {
            "model": model_name,
            "status": "not_loaded",
            "is_embedding_model": is_embedding_model(model_name)
        }
    
    return handler.get_model_info()


