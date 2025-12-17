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
    prefer_llm: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "this is a cat",
                "schema_hint": None,
                "prefer_llm": True
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
    
    Uses LLM if available, falls back to rule-based transformation.
    
    Examples:
        - "this is a cat" → {"pet": {"category": "cat"}}
        - "I have a red car" → {"item": {"color": "red", "type": "car"}}
        - "dog named Max" → {"dog": {"name": "Max"}}
    """
    try:
        # Create processor using factory
        processor = ProcessorFactory.create_processor(prefer_llm=request.prefer_llm)
        
        # Determine method from processor type
        method = "llm" if isinstance(processor, LLMBasedTextProcessor) else "rule-based"
        
        # Get model info if using LLM (future enhancement)
        model_used = None
        if method == "llm":
            # TODO: Extract model info from LLMBasedTextProcessor once implemented
            pass
        
        # Perform transformation using new processor
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
    
    except NotImplementedError as e:
        # LLMBasedTextProcessor not yet implemented
        raise HTTPException(status_code=501, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")


@router.get("/methods")
async def get_available_methods():
    """
    Get information about available transformation methods.
    """
    from app.services.model_manager import ModelManager
    
    manager = ModelManager()
    models = manager.list_models()
    running_models = [m for m in models if m.status == "RUNNING"]
    
    return {
        "llm_available": len(running_models) > 0,
        "llm_models": [{"id": m.id, "name": m.model_name} for m in running_models],
        "rule_based_available": True,
        "recommendation": "llm" if running_models else "rule-based"
    }


