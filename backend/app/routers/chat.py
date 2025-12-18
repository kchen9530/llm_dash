"""
对话路由（支持轻量级和 vLLM 模式）
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from typing import AsyncGenerator
import os
import json

from app.types.schemas import ChatRequest

# Use lightweight manager for 8GB RAM systems
USE_LIGHTWEIGHT = os.getenv("USE_LIGHTWEIGHT_MANAGER", "true").lower() == "true"

if USE_LIGHTWEIGHT:
    from app.services.lightweight_model_manager import LightweightModelManager as ModelManager
else:
    from app.services.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()


@router.post("/completions")
async def chat_completions(request: ChatRequest):
    """
    聊天补全（支持轻量级模式和 vLLM）
    """
    # 获取模型实例
    model_info = model_manager.get_model(request.model_id)
    if not model_info:
        raise HTTPException(status_code=404, detail=f"模型 {request.model_id} 不存在")
    
    if model_info.status != "RUNNING":
        raise HTTPException(
            status_code=400,
            detail=f"模型状态异常: {model_info.status}"
        )
    
    try:
        if USE_LIGHTWEIGHT:
            # Use lightweight direct inference
            # Build prompt from messages
            prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
            prompt += "\nassistant: "
            
            # For small CPU models, limit max_tokens to something reasonable
            # Most small models like GPT-2 only have 1024 token context
            safe_max_tokens = min(request.max_tokens, 256)  # Cap at 256 for CPU models
            
            if request.stream:
                # Streaming response
                async def stream_generator() -> AsyncGenerator[str, None]:
                    try:
                        async for chunk in model_manager.generate_stream(
                            model_id=request.model_id,
                            prompt=prompt,
                            max_tokens=safe_max_tokens,
                            temperature=request.temperature
                        ):
                            # Format as SSE
                            data = {
                                "choices": [{
                                    "delta": {"content": chunk},
                                    "index": 0
                                }]
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                        yield "data: [DONE]\n\n"
                    except Exception as e:
                        error_data = {"error": str(e)}
                        yield f"data: {json.dumps(error_data)}\n\n"
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream"
                )
            else:
                # Non-streaming response
                response_text = await model_manager.generate(
                    model_id=request.model_id,
                    prompt=prompt,
                    max_tokens=safe_max_tokens,
                    temperature=request.temperature
                )
                
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "index": 0
                    }]
                }
        else:
            # Use vLLM proxy (original code)
            vllm_url = f"http://localhost:{model_info.port}/v1/chat/completions"
            
            payload = {
                "model": model_info.model_name,
                "messages": [msg.dict() for msg in request.messages],
                "stream": request.stream,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }
            
            if request.stream:
                async def stream_generator() -> AsyncGenerator[str, None]:
                    async with httpx.AsyncClient(timeout=300.0) as client:
                        async with client.stream("POST", vllm_url, json=payload) as response:
                            async for line in response.aiter_lines():
                                if line.strip():
                                    yield f"{line}\n"
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream"
                )
            else:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(vllm_url, json=payload)
                    return response.json()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )

