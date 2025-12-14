"""
对话路由（代理到 vLLM）
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from typing import AsyncGenerator

from app.models.schemas import ChatRequest
from app.services.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()


@router.post("/completions")
async def chat_completions(request: ChatRequest):
    """
    聊天补全（代理到对应的 vLLM 实例）
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
    
    # 构建 vLLM API 地址
    vllm_url = f"http://localhost:{model_info.port}/v1/chat/completions"
    
    # 转换为 OpenAI 格式
    payload = {
        "model": model_info.model_name,
        "messages": [msg.dict() for msg in request.messages],
        "stream": request.stream,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }
    
    try:
        if request.stream:
            # 流式响应 - 创建独立的生成器和客户端
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
            # 非流式响应
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(vllm_url, json=payload)
                return response.json()
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"请求 vLLM 失败: {str(e)}"
        )

