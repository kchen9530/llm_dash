"""
LLM Local Ops Center - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import models, system, chat
from app.core.config import settings
from app.services.model_manager import ModelManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 LLM Local Ops Center Starting...")
    yield
    # 关闭时清理
    print("🛑 Shutting down...")
    model_manager = ModelManager()
    await model_manager.cleanup_all()


app = FastAPI(
    title="LLM Local Ops Center",
    description="本地 LLM 模型部署与管理中心",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(system.router, prefix="/api/system", tags=["系统监控"])
app.include_router(models.router, prefix="/api/models", tags=["模型管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])


@app.get("/")
async def root():
    return {
        "message": "LLM Local Ops Center API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

