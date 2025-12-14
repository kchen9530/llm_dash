# 🚀 快速开始指南

欢迎使用 **LLM Local Ops Center (LLOC)**！

## 一键启动

### 方式 1: 使用启动脚本（推荐）

```bash
./start.sh
```

这会自动：
- 安装后端依赖
- 安装前端依赖
- 启动后端服务 (Port 7860)
- 启动前端服务 (Port 5173)

### 方式 2: 手动启动

#### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

#### 前端（新终端）
```bash
cd frontend
npm install
npm run dev
```

## 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:7860
- **API 文档**: http://localhost:7860/docs

## 第一次使用

### 1. 验证系统状态

访问 Dashboard，查看 CPU、内存、GPU 信息。

### 2. 部署测试模型

推荐先部署一个小模型进行测试：

1. 点击 "Deploy Model" 或访问 `/deploy`
2. 选择 **Qwen/Qwen2-0.5B-Instruct** (只需 ~1GB 显存)
3. 保持默认配置
4. 点击 "Deploy Model"
5. 在 Dashboard 查看部署日志

### 3. 测试对话

1. 等待模型状态变为 "Running" (大约 1-2 分钟)
2. 访问 Chat 页面
3. 选择刚部署的模型
4. 开始聊天测试！

## 部署生产级模型

如果 GPU 显存充足（16GB+），可以部署更强大的模型：

### 推荐模型

| 模型 | 大小 | 显存需求 | 特点 |
|------|------|----------|------|
| Qwen2-0.5B-Instruct | 0.5B | ~1GB | 测试用 |
| Qwen2-7B-Instruct | 7B | ~14GB | 生产级，中文优秀 |
| Llama-3-8B-Instruct | 8B | ~16GB | Meta 官方 |
| Mistral-7B-Instruct | 7B | ~14GB | 高效推理 |

### 部署步骤

```bash
# 1. 访问 Deploy 页面
# 2. 输入模型名称，例如: Qwen/Qwen2-7B-Instruct
# 3. 调整参数（可选）:
#    - GPU Memory: 0.85 (使用 85% 显存)
#    - Max Context: 4096 tokens
#    - Data Type: auto
# 4. 点击 Deploy
```

## 常见问题

### Q: 模型下载速度慢？

**A:** 设置 HuggingFace 镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: 显存不足？

**A:** 降低 GPU Memory Utilization 或选择更小的模型。

### Q: 端口被占用？

**A:** 修改配置：
- 后端: `backend/run.py` 中的 `port=7860`
- 前端: `frontend/vite.config.ts` 中的 `port: 5173`

### Q: 如何停止所有服务？

**A:** 按 `Ctrl+C` 或：

```bash
pkill -f "uvicorn"
pkill -f "vite"
```

## 性能优化建议

### 1. 使用本地模型缓存

首次下载后，模型会缓存在 `~/.cache/huggingface/hub`。
再次部署时可以指定 Local Path 跳过下载。

### 2. 调整 vLLM 参数

- **gpu_memory_utilization**: 0.8-0.9（根据显存情况）
- **max_model_len**: 减小可节省显存
- **dtype**: bfloat16（支持的话）比 float16 更稳定

### 3. 多模型部署

系统支持同时运行多个模型实例（默认最多 5 个）。
注意监控 GPU 显存使用情况。

## 项目结构

```
llm-dash/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py   # 主应用
│   │   ├── routers/  # API 路由
│   │   ├── services/ # 核心服务
│   │   └── models/   # 数据模型
│   └── run.py        # 启动脚本
├── frontend/          # React 前端
│   ├── src/
│   │   ├── components/ # UI 组件
│   │   ├── pages/      # 页面
│   │   ├── store/      # 状态管理
│   │   └── lib/        # 工具库
│   └── package.json
├── start.sh          # 一键启动脚本
└── README.md         # 项目文档
```

## 下一步

- 📖 阅读完整文档: [README.md](./README.md)
- 🔧 查看 API 文档: http://localhost:7860/docs
- 💬 加入社区讨论
- ⭐ 给项目点个星！

## 需要帮助？

- 查看日志：Dashboard 中每个模型都有实时日志
- 检查系统状态：Dashboard 顶部显示 CPU/Memory/GPU
- 阅读错误信息：部署失败时会显示详细错误

---

**Happy Deploying! 🚀**

