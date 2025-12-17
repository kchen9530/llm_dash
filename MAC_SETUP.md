# LLM Dashboard - Mac Setup Guide (8GB RAM)

## 🎯 Quick Start

This project is configured for **CPU-only mode** suitable for Macs with limited RAM (8GB). Perfect for testing and development.

### Prerequisites
- Mac with 8GB RAM (works on M1/M2/Intel)
- Python 3.10+ (check with `python3 --version`)
- Node.js 18+ (check with `node --version`)

### Installation (Already Done ✅)

Your dependencies are already installed with lightweight packages suitable for 8GB RAM:
- ✅ Backend: FastAPI, Transformers, PyTorch (CPU-only)
- ✅ Frontend: React, Vite, Tailwind CSS

### Running the Dashboard

**Option 1: Quick Start (Recommended)**
```bash
chmod +x start-mac.sh
./start-mac.sh
```

**Option 2: Manual Start**

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python run.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Dashboard
- 🎨 **Frontend**: http://localhost:5173
- 📡 **Backend API**: http://localhost:7860
- 📚 **API Docs**: http://localhost:7860/docs

---

## 🤖 Recommended Models for 8GB RAM

### For Quick Testing (Hello World, 1+1)

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| `gpt2` | 500MB | ~1GB | ⚡️ Fast | Quick tests |
| `Qwen/Qwen2-0.5B-Instruct` | 1GB | ~2GB | ⚡️ Fast | Better quality |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 2GB | ~3GB | 🐢 Slow | Best quality |

**⚠️ Important Notes:**
- First model load takes 2-5 minutes (downloads from HuggingFace)
- CPU inference is SLOW: expect 1-5 seconds per response
- Don't use models larger than 1.5B on 8GB RAM
- Models are cached in `~/.cache/huggingface/` after first download

---

## 🔄 Switching to GPU Mode (Future)

When you want to deploy larger models on a GPU server:

### Method 1: Remote GPU Server

1. Edit `backend/.env`:
```env
DEPLOYMENT_MODE=gpu
GPU_SERVER_URL=http://your-gpu-server:8000
GPU_SERVER_API_KEY=your-api-key
```

2. The dashboard will forward requests to your GPU server

### Method 2: Install vLLM (If You Get a GPU Mac/Server)

1. Add vLLM to dependencies:
```bash
cd backend
source venv/bin/activate
pip install vllm==0.6.3.post1
```

2. Edit `backend/app/core/config.py`:
```python
FORCE_CPU_MODE: bool = False  # Enable GPU auto-detection
```

3. Restart the backend

---

## 📊 Testing the Dashboard

### 1. Test with GPT-2 (Fastest)

1. Open http://localhost:5173
2. Go to "Deploy" tab
3. Enter model: `gpt2`
4. Click "Deploy Model"
5. Wait 30-60 seconds for startup
6. Go to "Chat" tab
7. Select "gpt2" from dropdown
8. Try: "Hello! How are you?"

### 2. Test with Better Model

Same steps but use:
- Model: `Qwen/Qwen2-0.5B-Instruct`
- First load: 2-3 minutes (downloading)
- Subsequent loads: 30-60 seconds

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
cd backend
source venv/bin/activate
pip install -r requirements-lite.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Model loading fails
- Check you have internet (first download)
- Check available RAM: `top` or Activity Monitor
- Try smaller model (gpt2)
- Clear cache: `rm -rf ~/.cache/huggingface/`

### Out of memory
- Close other applications
- Use smaller model (gpt2 instead of TinyLlama)
- Restart your Mac to free RAM

### Port already in use
```bash
# Kill processes on ports
lsof -ti:7860 | xargs kill  # Backend
lsof -ti:5173 | xargs kill  # Frontend
```

---

## 📈 Performance Expectations

### On Mac with 8GB RAM (CPU):

| Task | Time | Notes |
|------|------|-------|
| First model download | 2-5 min | One-time per model |
| Model startup | 30-60 sec | Each time |
| "Hello" response | 1-3 sec | Short prompt |
| "1+1" calculation | 2-5 sec | May not be accurate! |
| Long conversation | 5-15 sec | Longer prompts |

**💡 These tiny models are NOT production-ready! They're for:**
- Testing the dashboard interface
- Learning the deployment flow
- Development work

For actual LLM applications, you need:
- Larger models (7B+)
- GPU server (see GPU mode above)
- More RAM (16GB+ for model + system)

---

## 🚀 Next Steps

1. **Test the basic flow** with gpt2
2. **Try a chat conversation** with Qwen2-0.5B
3. **Monitor system resources** in Activity Monitor
4. **Plan GPU deployment** when you need real performance

### Future: Deploy to GPU Server

Options for production deployment:
- **Cloud GPU**: RunPod, Vast.ai, Lambda Labs (~$0.20-0.50/hour)
- **Modal/Banana**: Serverless GPU inference
- **Your own server**: NVIDIA GPU (RTX 3090, 4090, A100, etc.)

The dashboard will work the same way, just point it to your GPU endpoint!

---

## 📝 Project Structure

```
llm-dash/
├── backend/
│   ├── venv/              # Python virtual environment ✅
│   ├── app/
│   │   ├── services/
│   │   │   ├── model_manager.py      # vLLM process manager
│   │   │   └── cpu_model_runner.py   # Lightweight CPU runner 🆕
│   │   ├── routers/       # API endpoints
│   │   └── core/          # Config (CPU/GPU mode)
│   ├── requirements-lite.txt  # Mac-friendly deps 🆕
│   └── run.py             # Start backend
├── frontend/
│   ├── src/               # React components
│   └── package.json
├── start-mac.sh           # One-command startup 🆕
└── MAC_SETUP.md          # This file 🆕
```

---

## 🤝 Need Help?

- Check backend logs in terminal
- Check browser console (F12)
- API docs: http://localhost:7860/docs
- System resources: Activity Monitor

Enjoy your local LLM dashboard! 🎉


