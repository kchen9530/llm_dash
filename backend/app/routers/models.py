"""
模型管理路由
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

from app.models.schemas import DeployRequest, ModelInfo
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
async def get_model_logs(model_id: str, lines: int = 100):
    """
    获取模型日志
    """
    logs = model_manager.get_logs(model_id, lines)
    return {"model_id": model_id, "logs": logs}


@router.websocket("/ws/logs/{model_id}")
async def websocket_logs(websocket: WebSocket, model_id: str):
    """
    WebSocket 实时日志流
    """
    await websocket.accept()
    
    try:
        last_log_count = 0
        
        while True:
            # 获取新日志
            logs = model_manager.get_logs(model_id, lines=1000)
            
            # 只发送新增的日志
            if len(logs) > last_log_count:
                new_logs = logs[last_log_count:]
                for log in new_logs:
                    await websocket.send_json({
                        "type": "log",
                        "model_id": model_id,
                        "message": log,
                    })
                last_log_count = len(logs)
            
            # 发送模型状态更新
            model_info = model_manager.get_model(model_id)
            if model_info:
                await websocket.send_json({
                    "type": "status",
                    "model_id": model_id,
                    "status": model_info.status,
                })
            
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        print(f"WebSocket 断开: {model_id}")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

