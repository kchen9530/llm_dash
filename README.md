# 🚀 LLM Local Ops Center (LLOC)

一个现代化的本地 LLM 模型部署与管理中心，提供优雅的 Web 界面来管理多个 vLLM 实例。

## ✨ 特性

- 🎯 **一键部署**: 快速部署 HuggingFace 模型到本地 GPU
- 🔧 **CPU/GPU 双模式**: 一键切换 CPU 测试模式或 GPU 生产模式 *(NEW!)*
- 📊 **实时监控**: CPU、内存、GPU 使用率实时显示
- 📝 **日志流**: WebSocket 实时日志查看
- 💬 **即时对话**: 内置聊天界面测试模型
- 🎨 **现代 UI**: 基于 Shadcn/ui 的精美界面
- ⚡ **高性能**: vLLM 引擎提供极致推理速度

## 🏗️ 架构

```
┌─────────────────┐
│   React + Vite  │  前端 (Port 5173)
│   Shadcn/ui     │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│    FastAPI      │  后端 (Port 7860)
│  ModelManager   │
└────────┬────────┘
         │ subprocess
┌────────▼────────┐
│  vLLM Instance  │  模型服务 (Port 8000+)
│  (GPU Inference)│
└─────────────────┘
```

## 📦 技术栈

### 后端
- **FastAPI**: 高性能 Web 框架
- **vLLM**: LLM 推理引擎
- **pynvml**: GPU 监控
- **WebSocket**: 实时通信

### 前端
- **React 18**: UI 框架
- **Vite**: 构建工具
- **Shadcn/ui**: 组件库
- **Tailwind CSS**: 样式
- **xterm.js**: 终端日志显示

## 🚀 快速开始

### ⚠️ CPU/GPU 模式说明

本项目支持两种运行模式：

| 模式 | 适用场景 | 性能 | 配置 |
|------|---------|------|------|
| **CPU 模式** | 开发测试 | 慢 (5-30s/响应) | `FORCE_CPU_MODE=True` (当前) |
| **GPU 模式** | 生产部署 | 快 (20-100+ tok/s) | `FORCE_CPU_MODE=False` |

**当前配置：CPU 模式** - 适合测试部署流程，只能运行小模型 (0.5B-1.5B)

📖 **切换到 GPU 模式**: 查看 [`CPU_GPU_MODE.md`](./CPU_GPU_MODE.md) 了解如何一键切换

---

### 前置要求

- Python 3.10+
- Node.js 18+
- NVIDIA GPU (带 CUDA 支持)
- 至少 16GB RAM

### 1. 克隆项目

```bash
cd /root/llm-dash
```

### 2. 后端设置

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python run.py
```

后端将在 `http://0.0.0.0:7860` 启动。

### 3. 前端设置

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动。

## 📖 使用指南

### 部署模型

1. 访问 Dashboard
2. 点击 "Deploy Model"
3. 输入 HuggingFace 模型 ID（如 `Qwen/Qwen2-0.5B-Instruct`）
4. 配置参数（GPU 内存、最大长度等）
5. 点击部署，实时查看日志

### 管理实例

- 🟢 **运行中**: 绿色指示器
- 🟡 **启动中**: 黄色指示器
- 🔴 **错误**: 红色指示器
- ⚪ **已停止**: 灰色指示器

### 聊天测试

1. 在侧边栏选择 "Chat"
2. 从下拉框选择运行中的模型
3. 开始对话测试

## 📊 API 文档

### 系统监控
- `GET /api/system/status` - 系统状态
- `GET /api/system/gpu` - GPU 信息

### 模型管理
- `POST /api/models/deploy` - 部署模型
- `GET /api/models/list` - 模型列表
- `POST /api/models/{id}/stop` - 停止模型
- `DELETE /api/models/{id}` - 删除实例
- `WS /api/models/ws/logs/{id}` - 实时日志

### 对话
- `POST /api/chat/completions` - 聊天（支持流式）

完整文档: http://localhost:7860/docs

## 🎯 推荐模型

### 测试用（快速验证）
- `Qwen/Qwen2-0.5B-Instruct` (0.5B, ~1GB)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (1.1B, ~2GB)

### 生产用
- `Qwen/Qwen2-7B-Instruct` (7B, ~14GB)
- `meta-llama/Llama-3-8B-Instruct` (8B, ~16GB)
- `mistralai/Mistral-7B-Instruct-v0.3` (7B, ~14GB)

## 🛠️ 开发计划

- [x] 后端基础架构
- [x] 进程管理器
- [x] WebSocket 日志流
- [ ] 前端 UI（进行中）
- [ ] 聊天界面
- [ ] Docker 部署
- [ ] 多机分布式支持

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for the LLM Community**

