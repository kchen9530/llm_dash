# GPU/CPU Mode Configuration Guide

## 🎯 Current Status: CPU Mode (Testing)

This application is currently configured to run in **CPU-only mode** for reference testing. This allows you to test the deployment workflow without requiring a GPU.

## 🔧 Feature Switch Overview

The GPU/CPU mode is controlled by a single configuration flag in your backend settings.

### Current Configuration (CPU Mode)

**File:** `backend/app/core/config.py`
```python
FORCE_CPU_MODE: bool = True  # ✅ Currently enabled for testing
```

## 🚀 Switching to GPU Mode

When you're ready to deploy on a GPU server, follow these steps:

### Step 1: Verify GPU Availability

```bash
# Check if NVIDIA GPU is detected
nvidia-smi

# Should show your GPU details and CUDA version
```

### Step 2: Update Configuration

**Option A: Using .env file (Recommended)**
```bash
# Copy the example file
cp backend/.env.example backend/.env

# Edit the .env file
nano backend/.env

# Change this line:
FORCE_CPU_MODE=False
```

**Option B: Direct code change**
```python
# Edit: backend/app/core/config.py
FORCE_CPU_MODE: bool = False  # Change True to False
```

### Step 3: Restart Backend

```bash
cd backend
source venv/bin/activate
python run.py
```

You should see:
```
✅ GPU detected and enabled
```

## 📊 Mode Comparison

| Feature | CPU Mode | GPU Mode |
|---------|----------|----------|
| Speed | Slow (10-100x slower) | Fast |
| Model Size | Small only (<1B params) | Large (up to 70B+) |
| Memory | System RAM | GPU VRAM |
| Setup | No special requirements | NVIDIA GPU + CUDA |
| Use Case | Testing, Development | Production |

## ⚙️ How It Works

### Auto-Detection Logic

```python
# In config.py
if not self.FORCE_CPU_MODE:
    self.USE_GPU = detect_gpu()  # Auto-detects GPU
else:
    self.USE_GPU = False  # Forced CPU mode
```

### vLLM Command Differences

**CPU Mode:**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2-0.5B-Instruct \
  --device cpu \
  --dtype float32
```

**GPU Mode:**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2-0.5B-Instruct \
  --gpu-memory-utilization 0.85 \
  --dtype auto
```

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Check driver installation
nvidia-smi

# Check CUDA version
nvcc --version

# Reinstall NVIDIA drivers if needed
# (varies by OS - Ubuntu/CentOS/etc)
```

### vLLM Not Using GPU

```bash
# Check vLLM can see CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Should output: True
```

### Performance Issues

**CPU Mode:**
- Use tiny models only (0.5B-1.5B parameters)
- Expect slow inference (5-30 seconds per response)
- Good for testing deployment workflow

**GPU Mode:**
- Use appropriately sized models for your VRAM
- Expected speed: 20-100+ tokens/second
- Production-ready performance

## 📝 Recommended Test Models

### CPU Mode (Current)
- ✅ `Qwen/Qwen2-0.5B-Instruct` - Works well
- ⚠️  `Qwen/Qwen2-1.5B-Instruct` - Slow but functional
- ❌ `Qwen/Qwen2-7B-Instruct` - Too large for CPU

### GPU Mode (8GB VRAM)
- ✅ `Qwen/Qwen2-7B-Instruct`
- ✅ `meta-llama/Llama-3-8B-Instruct`
- ✅ `mistralai/Mistral-7B-Instruct-v0.3`

### GPU Mode (24GB+ VRAM)
- ✅ Models up to 30B parameters
- ✅ `meta-llama/Llama-2-70B-chat` (with quantization)

## 🎓 Summary

1. **Current Mode:** CPU (FORCE_CPU_MODE=True)
2. **To Enable GPU:** Set FORCE_CPU_MODE=False
3. **Auto-Detection:** System checks for nvidia-smi
4. **No Code Changes:** Just flip the config flag
5. **Restart Required:** Yes, after changing config

---

**Questions?** The code will automatically log which mode it's running in at startup.
