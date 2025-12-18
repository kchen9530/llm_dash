"""
Chat and conversation schemas
"""
from pydantic import BaseModel, Field
from typing import List


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    model_id: str = Field(..., description="模型实例 ID")
    messages: List[ChatMessage] = Field(..., description="消息历史")
    stream: bool = Field(default=True, description="是否流式返回")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1)
