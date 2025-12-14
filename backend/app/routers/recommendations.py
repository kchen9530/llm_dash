"""
Model Recommendations Router
"""
from fastapi import APIRouter
from app.core.model_config import get_all_recommended_models, get_downloaded_models

router = APIRouter()


@router.get("/models")
async def get_recommended_models():
    """
    Get recommended models for 8GB RAM systems.
    Returns both chat models and embedding models.
    """
    return get_all_recommended_models()


@router.get("/downloaded")
async def get_downloaded_models_list():
    """
    Get list of models already downloaded to local storage.
    Returns models found in models/chat/ and models/embeddings/.
    """
    return get_downloaded_models()

