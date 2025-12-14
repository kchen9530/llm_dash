"""
模型管理路由
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
import os

from app.models.schemas import DeployRequest, ModelInfo

# Use lightweight manager for 8GB RAM systems
USE_LIGHTWEIGHT = os.getenv("USE_LIGHTWEIGHT_MANAGER", "true").lower() == "true"

if USE_LIGHTWEIGHT:
    from app.services.lightweight_model_manager import LightweightModelManager as ModelManager
else:
    from app.services.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()


@router.post("/deploy", response_model=ModelInfo)
async def deploy_model(request: DeployRequest):
    """
    部署新模型
    """
    try:
        model_info = await model_manager.deploy_model(request)
        return model_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=List[ModelInfo])
async def list_models():
    """
    列出所有模型实例
    """
    return model_manager.list_models()


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """
    获取特定模型信息
    """
    model_info = model_manager.get_model(model_id)
    if not model_info:
        raise HTTPException(status_code=404, detail=f"模型 {model_id} 不存在")
    return model_info


@router.post("/{model_id}/stop")
async def stop_model(model_id: str):
    """
    停止模型
    """
    try:
        success = await model_manager.stop_model(model_id)
        if success:
            return {"message": f"模型 {model_id} 已停止"}
        else:
            raise HTTPException(status_code=500, detail="停止失败")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{model_id}")
async def remove_model(model_id: str):
    """
    移除模型实例
    """
    success = await model_manager.remove_model(model_id)
    if success:
        return {"message": f"模型 {model_id} 已移除"}
    else:
        raise HTTPException(status_code=404, detail=f"模型 {model_id} 不存在")


@router.get("/{model_id}/logs")
async def get_model_logs(model_id: str, lines: int = 500):
    """
    Get logs for a specific model
    """
    from ..services.model_logger import model_logger
    
    logs = model_logger.get_logs(model_id, lines)
    
    if not logs:
        # Check if model exists
        manager = get_model_manager()
        try:
            manager.get_model_info(model_id)
            # Model exists but no logs yet
            return {"logs": ["Model is initializing, no logs available yet"], "count": 1}
        except (ValueError, AttributeError):
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return {"logs": logs, "count": len(logs)}


@router.websocket("/ws/logs/{model_id}")
async def websocket_logs(websocket: WebSocket, model_id: str):
    """
    WebSocket real-time log streaming
    """
    from ..services.model_logger import model_logger
    
    await websocket.accept()
    
    try:
        last_log_count = 0
        manager = get_model_manager()
        
        while True:
            # Get new logs
            logs = model_logger.get_logs(model_id, lines=1000)
            
            # Send only new logs
            if len(logs) > last_log_count:
                new_logs = logs[last_log_count:]
                for log in new_logs:
                    await websocket.send_json({
                        "type": "log",
                        "model_id": model_id,
                        "message": log,
                    })
                last_log_count = len(logs)
            
            # Send model status update
            try:
                model_info = manager.get_model_info(model_id)
                await websocket.send_json({
                    "type": "status",
                    "model_id": model_id,
                    "status": model_info.get("status", "UNKNOWN"),
                })
            except:
                pass
            
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {model_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

