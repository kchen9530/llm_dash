"""
Text to JSON Transformation Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.processor import (
    process_text_to_json,
    ProcessorFactory,
    RuleBasedTextProcessor,
    LLMBasedTextProcessor
)

router = APIRouter()


class TransformRequest(BaseModel):
    """Request model for text transformation"""
    text: str
    schema_hint: Optional[str] = None
    prefer_llm: bool = False
    model1_id: Optional[str] = None  # LLM for category generation
    model2_id: Optional[str] = None  # LLM for detail generation
    embed_model_id: Optional[str] = None  # Embedding model
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "this is a cat",
                "schema_hint": None,
                "prefer_llm": False,
                "model1_id": "gpt2-221744",
                "model2_id": "gpt2-221744",
                "embed_model_id": "all-MiniLM-L6-v2-221750"
            }
        }


class TransformResponse(BaseModel):
    """Response model for text transformation"""
    success: bool
    result: Dict[str, Any]
    method: str  # "llm" or "rule-based"
    model_used: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "result": {"pet": {"category": "cat"}},
                "method": "llm",
                "model_used": "gpt2-8000"
            }
        }


@router.post("/text-to-json", response_model=TransformResponse)
async def transform_text(request: TransformRequest):
    """
    Transform natural language text to structured JSON.
    
    Supports two modes:
    - Rule-based: Fast, deterministic pattern matching
    - LLM-based: 3-step pipeline using deployed models
      1. Model1: Generate category JSON
      2. Model2: Generate detailed JSON
      3. EmbedModel: Add embedding information
    
    Examples:
        - "this is a cat" → {"pet": {"category": "cat"}}
        - "I have a red car" → {"item": {"color": "red", "type": "car"}}
    """
    try:
        # Create processor using factory
        processor = ProcessorFactory.create_processor(
            prefer_llm=request.prefer_llm,
            model1_id=request.model1_id,
            model2_id=request.model2_id,
            embed_model_id=request.embed_model_id
        )
        
        # Determine method from processor type
        method = "llm" if isinstance(processor, LLMBasedTextProcessor) else "rule-based"
        
        # Get model info if using LLM
        model_used = None
        if method == "llm":
            model_used = {
                "model1": request.model1_id,
                "model2": request.model2_id,
                "embed": request.embed_model_id
            }
        
        # Perform transformation using processor
        result = await process_text_to_json(
            text=request.text,
            schema_hint=request.schema_hint,
            processor=processor
        )
        
        return TransformResponse(
            success=True,
            result=result,
            method=method,
            model_used=model_used
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")


@router.get("/methods")
async def get_available_methods():
    """
    Get information about available transformation methods and models.
    """
    from app.services.lightweight_model_manager import LightweightModelManager
    
    manager = LightweightModelManager()
    
    # Get chat models (for LLM processing)
    chat_models = manager.list_chat_models()
    running_chat = [m for m in chat_models if m.status == "RUNNING"]
    
    # Get embedding models
    embed_models = manager.list_embedding_models()
    running_embed = [m for m in embed_models if m.status == "RUNNING"]
    
    # Check if LLM-based is available (need at least 1 chat + 1 embed)
    llm_available = len(running_chat) >= 1 and len(running_embed) >= 1
    
    return {
        "rule_based_available": True,
        "llm_available": llm_available,
        "llm_models": [
            {"id": m.id, "name": m.model_name, "status": m.status} 
            for m in running_chat
        ],
        "embed_models": [
            {"id": m.id, "name": m.model_name, "status": m.status}
            for m in running_embed
        ],
        "recommendation": "llm" if llm_available else "rule-based",
        "requirements": {
            "llm": "Requires at least 1 running LLM model and 1 embedding model",
            "rule_based": "Always available"
        }
    }


