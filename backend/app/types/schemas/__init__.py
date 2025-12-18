"""
Type definitions for API requests, responses, and data structures.
Organized by domain for better maintainability.
"""
from .base import ModelStatus
from .deployment import DeployRequest, ModelInfo
from .chat import ChatMessage, ChatRequest
from .system import SystemStatus, GPUInfo
from .logging import LogMessage

__all__ = [
    # Base
    "ModelStatus",
    # Deployment
    "DeployRequest", 
    "ModelInfo",
    # Chat
    "ChatMessage",
    "ChatRequest",
    # System
    "SystemStatus",
    "GPUInfo",
    # Logging
    "LogMessage",
]
