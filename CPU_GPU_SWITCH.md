# 🔄 CPU ↔️ GPU Mode Switch Guide

## Current Configuration: CPU Mode ✅

Your project is currently set up for **CPU-only mode** on your 8GB Mac.

---

## 📊 Comparison Table

| Feature | CPU Mode (Current) | GPU Mode (Future) |
|---------|-------------------|-------------------|
| **Hardware** | Mac 8GB RAM | NVIDIA GPU server |
| **Models** | Tiny (0.5-1.5B) | Large (7B-70B+) |
| **Memory** | ~5GB total | 16GB+ VRAM |
| **Speed** | 🐢 2-10 sec/response | ⚡ 0.1-1 sec/response |
| **Quality** | 😅 Basic/silly | 🎯 Production-ready |
| **Use Case** | Testing UI | Real applications |
| **Cost** | $0 (local) | $0.20-2/hour (cloud) |

---

## 🎯 Current Setup (CPU Mode)

### Configuration Files

**backend/app/core/config.py:**
```python
FORCE_CPU_MODE: bool = True  # ← Your current setting
USE_GPU: bool = False        # Auto-detected
```

**backend/requirements-lite.txt:**
- No vLLM (too heavy)
- PyTorch CPU-only
- Transformers for tiny models

### What Works Now:
✅ Dashboard UI  
✅ Model deployment interface  
✅ Chat with tiny models (gpt2, Qwen2-0.5B)  
✅ Learning the workflow  
✅ Testing and development  

### What Doesn't Work:
❌ Large models (7B+)  
❌ Fast inference  
❌ Production quality responses  
❌ Multiple concurrent users  

---

## 🚀 Switching to GPU Mode

### Option 1: Remote GPU Server (Recommended 👍)

**Best for:** Most users, no hardware changes needed

**Setup:**
1. Get GPU server access:
   - **RunPod** ($0.20-0.50/hour): runpod.io
   - **Vast.ai** (cheaper spot instances): vast.ai
   - **Modal** (serverless): modal.com
   - **Your own server** with NVIDIA GPU

2. Deploy vLLM on GPU server (one-time):
   ```bash
   # On GPU server
   pip install vllm
   vllm serve meta-llama/Llama-3-8B-Instruct --port 8000
   ```

3. Configure your Mac dashboard:
   ```bash
   # On your Mac
   cd /Users/kaichen/Desktop/llm-dash/backend
   
   # Edit or create .env file
   echo "DEPLOYMENT_MODE=remote_gpu" >> .env
   echo "GPU_SERVER_URL=http://your-gpu-server-ip:8000" >> .env
   echo "GPU_SERVER_API_KEY=your-secret-key" >> .env
   ```

4. Restart backend:
   ```bash
   cd backend
   source venv/bin/activate
   python run.py
   ```

5. Now when you deploy models, they run on the GPU server! 🎉

**Pros:**
- ✅ No local changes needed
- ✅ Use large models (7B-70B)
- ✅ Fast inference (GPU speed)
- ✅ Keep 8GB Mac as-is

**Cons:**
- 💰 Costs money (but cheap: $0.20-2/hour)
- 🌐 Needs internet connection

---

### Option 2: Install vLLM Locally (If You Get a GPU)

**Best for:** If you get a GPU Mac or dedicated GPU machine

**Requirements:**
- NVIDIA GPU (RTX 3090, 4090, A100, etc.)
- 16GB+ VRAM
- CUDA support

**Setup:**

1. Install vLLM (3GB+ download):
   ```bash
   cd /Users/kaichen/Desktop/llm-dash/backend
   source venv/bin/activate
   pip install vllm==0.6.3.post1
   ```

2. Edit configuration:
   ```python
   # backend/app/core/config.py
   FORCE_CPU_MODE: bool = False  # ← Change this
   ```

3. Restart backend:
   ```bash
   python run.py
   ```

4. Now you can deploy large models locally!

**Pros:**
- ✅ No ongoing costs
- ✅ No internet needed
- ✅ Full control

**Cons:**
- ❌ Needs expensive hardware ($1000-5000+)
- ❌ Large installation (3GB+)
- ❌ Won't work on 8GB RAM Mac

---

## 🔀 Switching Back to CPU Mode

If you tried GPU mode and want to go back:

**From Remote GPU:**
```bash
# backend/.env
DEPLOYMENT_MODE=cpu
# (comment out GPU_SERVER_URL)
```

**From Local vLLM:**
```python
# backend/app/core/config.py
FORCE_CPU_MODE: bool = True  # Back to CPU
```

Then restart the backend.

---

## 🧪 Testing the Switch

### Test CPU Mode (Current):
```bash
./start-mac.sh
# Deploy: gpt2
# Chat: "Hello"
# Speed: ~3 seconds
```

### Test Remote GPU Mode:
```bash
./start-mac.sh
# Deploy: meta-llama/Llama-3-8B-Instruct
# Chat: "Hello"
# Speed: ~0.5 seconds
```

### Verify Which Mode You're In:
```bash
cd backend
source venv/bin/activate
python -c "from app.core.config import settings; print('CPU Mode' if settings.FORCE_CPU_MODE else 'GPU Mode')"
```

---

## 📝 Configuration Files Quick Reference

### CPU Mode (Default):
```python
# backend/app/core/config.py
FORCE_CPU_MODE: bool = True

# backend/.env (optional)
DEPLOYMENT_MODE=cpu
```

### Remote GPU Mode:
```python
# backend/app/core/config.py
FORCE_CPU_MODE: bool = False

# backend/.env
DEPLOYMENT_MODE=remote_gpu
GPU_SERVER_URL=http://your-server:8000
GPU_SERVER_API_KEY=your-key
```

### Local vLLM GPU Mode:
```python
# backend/app/core/config.py
FORCE_CPU_MODE: bool = False

# backend/.env
DEPLOYMENT_MODE=local_gpu
```

---

## 🎯 Recommended Path

**Phase 1: Now (CPU Mode)**
- Learn the interface
- Test with gpt2
- Understand the workflow
- Develop features

**Phase 2: When Ready (Remote GPU)**
- Sign up for RunPod/Vast.ai
- Deploy vLLM on GPU server
- Point dashboard to GPU
- Use real models (7B-70B)

**Phase 3: Later (Local GPU - Optional)**
- If you build/buy GPU machine
- Install vLLM locally
- Run everything self-hosted

---

## 💡 Pro Tips

1. **Start Small**: Test CPU mode thoroughly first
2. **GPU Budget**: Start with spot instances ($0.20/hour)
3. **Model Size**: Begin with 7B models on GPU, then try larger
4. **Monitor Costs**: Set billing alerts on cloud GPU platforms
5. **Cache Models**: Download models once, reuse them
6. **Hybrid Setup**: Keep CPU for dev, GPU for prod

---

## 🆘 Troubleshooting Mode Switches

### "Backend won't start after GPU mode"
```bash
cd backend
source venv/bin/activate
pip install vllm  # If missing
python run.py
```

### "Can't connect to GPU server"
```bash
# Check GPU server is running
curl http://your-gpu-server:8000/health

# Check .env file
cat backend/.env
```

### "Want to remove vLLM (too big)"
```bash
cd backend
source venv/bin/activate
pip uninstall vllm

# Set back to CPU mode
# Edit config.py: FORCE_CPU_MODE = True
```

---

## 📊 Performance Benchmarks

### gpt2 on CPU (Current):
- Load time: 30 sec
- "Hello": 2-3 sec
- Quality: 3/10

### Llama-3-8B on GPU (Future):
- Load time: 10 sec
- "Hello": 0.3 sec
- Quality: 9/10

### Llama-3-70B on GPU (Future with big server):
- Load time: 30 sec
- "Hello": 0.8 sec
- Quality: 10/10

---

**Current Status:** ✅ CPU Mode (Perfect for your 8GB Mac)  
**Next Step:** Try it out with `./start-mac.sh`  
**Future:** Add GPU when you need real performance! 🚀

