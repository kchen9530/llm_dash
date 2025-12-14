"""
Photo Search Router
Semantic image search using text queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.photo_search_service import get_photo_search_service

router = APIRouter()


class SearchRequest(BaseModel):
    """Photo search request"""
    query: str
    top_k: int = 5
    model_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "a black dog",
                "top_k": 5,
                "model_name": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }


class SearchResult(BaseModel):
    """Single search result"""
    photo_id: str
    filename: str
    description: str
    tags: List[str]
    similarity: float
    similarity_percent: float


class SearchResponse(BaseModel):
    """Photo search response"""
    query: str
    results: List[SearchResult]
    total_results: int


@router.post("/search", response_model=SearchResponse)
async def search_photos(request: SearchRequest):
    """
    Search photos using semantic text query.
    
    Examples:
        - "a black dog"
        - "cat playing"
        - "dog running on beach"
        - "sleeping cat"
    
    Returns photos ranked by semantic similarity to the query.
    """
    try:
        service = get_photo_search_service()
        
        # Perform search
        results = await service.search(
            query=request.query,
            top_k=request.top_k,
            model_name=request.model_name
        )
        
        # Format results
        formatted_results = [
            SearchResult(
                photo_id=r['photo']['id'],
                filename=r['photo']['filename'],
                description=r['photo']['description'],
                tags=r['photo']['tags'],
                similarity=r['similarity'],
                similarity_percent=r['similarity_percent']
            )
            for r in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/initialize")
async def initialize_photo_search(
    model_name: Optional[str] = None,
    use_deployed: bool = True
):
    """
    Initialize photo search service and pre-compute embeddings.
    
    If use_deployed=True (default), will use already deployed embedding models.
    Otherwise, specify model_name to load a specific model.
    """
    try:
        service = get_photo_search_service()
        await service.initialize_embeddings(model_name, use_deployed)
        
        stats = service.get_stats()
        
        return {
            "status": "initialized",
            "model": stats.get('embedding_model', 'unknown'),
            "stats": stats,
            "note": "Using deployed embedding model" if use_deployed else "Loaded new model"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.get("/photos")
async def get_all_photos():
    """
    Get all photos in the database with their metadata.
    """
    service = get_photo_search_service()
    photos = service.get_all_photos()
    
    return {
        "photos": photos,
        "total": len(photos)
    }


@router.get("/photos/{photo_id}")
async def get_photo_by_id(photo_id: str):
    """
    Get specific photo metadata by ID.
    """
    service = get_photo_search_service()
    photo = service.get_photo_by_id(photo_id)
    
    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo {photo_id} not found")
    
    return photo


@router.get("/stats")
async def get_search_stats():
    """
    Get photo search service statistics.
    """
    service = get_photo_search_service()
    return service.get_stats()

