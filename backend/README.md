# LLM Local Ops Center - Backend

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 根据需要修改 .env 文件
```

### 3. 启动服务

```bash
python run.py
```

服务将在 `http://0.0.0.0:7860` 启动。

## API 文档

启动后访问：
- Swagger UI: http://localhost:7860/docs
- ReDoc: http://localhost:7860/redoc

## 主要功能

### 1. 系统监控
- `GET /api/system/status` - 获取 CPU、内存、GPU 状态
- `GET /api/system/gpu` - 获取 GPU 详细信息

### 2. 模型管理
- `POST /api/models/deploy` - 部署新模型
- `GET /api/models/list` - 列出所有模型
- `GET /api/models/{model_id}` - 获取模型信息
- `POST /api/models/{model_id}/stop` - 停止模型
- `DELETE /api/models/{model_id}` - 移除模型
- `GET /api/models/{model_id}/logs` - 获取模型日志
- `WS /api/models/ws/logs/{model_id}` - 实时日志流

### 3. 对话
- `POST /api/chat/completions` - 聊天补全（支持流式）

## 部署示例

```bash
curl -X POST "http://localhost:7860/api/models/deploy" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "Qwen/Qwen2-0.5B-Instruct",
    "port": 8000,
    "parameters": {
      "dtype": "auto",
      "gpu_memory_utilization": 0.8,
      "max_model_len": 2048,
      "trust_remote_code": true
    }
  }'
```

## 技术栈

- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **pynvml**: GPU 监控
- **psutil**: 系统监控
- **WebSocket**: 实时日志流

