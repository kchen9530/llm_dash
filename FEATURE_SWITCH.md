# 🔧 Feature Switch: CPU ↔️ GPU Mode

## Visual Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Startup                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Check Configuration │
              │  FORCE_CPU_MODE = ?  │
              └──────────┬───────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
    True │                                │ False
         │                                │
         ▼                                ▼
┌────────────────────┐        ┌──────────────────────┐
│   CPU MODE         │        │  Auto-Detect GPU     │
│                    │        │  (nvidia-smi check)  │
│ ℹ️  CPU forced     │        └──────────┬───────────┘
│                    │                   │
│ • Small models     │        ┌──────────┴───────────┐
│ • Slow inference   │        │                      │
│ • Testing only     │   Found │                      │ Not Found
│                    │        │                      │
└────────────────────┘        ▼                      ▼
                     ┌─────────────────┐  ┌─────────────────┐
                     │   GPU MODE      │  │   CPU MODE      │
                     │                 │  │                 │
                     │ ✅ GPU enabled  │  │ ⚠️  No GPU      │
                     │                 │  │                 │
                     │ • Fast          │  │ • Fallback      │
                     │ • Large models  │  │ • Limited       │
                     │ • Production    │  │                 │
                     └─────────────────┘  └─────────────────┘
```

## The One-Line Switch

**Location:** `backend/app/core/config.py`

```python
# Line 41
FORCE_CPU_MODE: bool = True  # ← This controls everything!
```

### Current Setting: `True` (CPU Mode)
```python
FORCE_CPU_MODE: bool = True  # CPU for testing
```

### To Enable GPU: Change to `False`
```python
FORCE_CPU_MODE: bool = False  # GPU auto-detection
```

## Code Flow

### 1. Configuration Loading (`config.py`)

```python
class Settings(BaseSettings):
    FORCE_CPU_MODE: bool = True  # Feature switch
    USE_GPU: bool = False        # Auto-set
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.FORCE_CPU_MODE:
            self.USE_GPU = detect_gpu()  # Check nvidia-smi
            if self.USE_GPU:
                print("✅ GPU detected and enabled")
            else:
                print("⚠️  No GPU detected, using CPU mode")
        else:
            self.USE_GPU = False
            print("ℹ️  CPU mode forced via config")
```

### 2. Model Deployment (`model_manager.py`)

```python
async def _start_vllm_process(self, instance, request):
    cmd = ["python", "-m", "vllm.entrypoints.openai.api_server"]
    
    if settings.USE_GPU:
        # GPU mode
        cmd.extend([
            "--gpu-memory-utilization", "0.85",
            "--dtype", "auto"
        ])
    else:
        # CPU mode
        cmd.extend([
            "--device", "cpu",
            "--dtype", "float32"
        ])
```

### 3. Frontend Display (`Deploy.tsx`)

```typescript
useEffect(() => {
  api.get('/api/system/compute-mode')
    .then(res => setComputeMode(res.data))
}, [])

// Shows warning banner in CPU mode
{computeMode && !computeMode.use_gpu && (
  <div className="warning">CPU Mode - Testing Only</div>
)}
```

## API Endpoint

### GET `/api/system/compute-mode`

**Response:**
```json
{
  "use_gpu": false,
  "force_cpu_mode": true,
  "mode": "CPU",
  "description": "CPU mode - testing only, use small models"
}
```

**When GPU enabled:**
```json
{
  "use_gpu": true,
  "force_cpu_mode": false,
  "mode": "GPU",
  "description": "GPU acceleration enabled"
}
```

## Switching Process

### Method 1: Config File (Recommended)

```bash
# 1. Edit config
nano backend/app/core/config.py

# 2. Change line 41
FORCE_CPU_MODE: bool = False

# 3. Restart backend
cd backend
source venv/bin/activate
python run.py
```

### Method 2: Environment Variable

```bash
# 1. Create .env file
echo "FORCE_CPU_MODE=False" > backend/.env

# 2. Restart backend
cd backend
source venv/bin/activate
python run.py
```

## Verification

### Check Logs

**CPU Mode:**
```
ℹ️  CPU mode forced via config (FORCE_CPU_MODE=True)
```

**GPU Mode (with GPU):**
```
✅ GPU detected and enabled
```

**GPU Mode (no GPU):**
```
⚠️  No GPU detected, using CPU mode
```

### Check API

```bash
curl http://localhost:5000/api/system/compute-mode
```

### Check Frontend

Navigate to Deploy page:
- CPU mode: Shows amber warning banner
- GPU mode: Shows green success banner

## Impact Matrix

| Component | CPU Mode | GPU Mode |
|-----------|----------|----------|
| **Config** | `FORCE_CPU_MODE=True` | `FORCE_CPU_MODE=False` |
| **Detection** | Skipped | Runs `nvidia-smi` |
| **vLLM Device** | `--device cpu` | Uses GPU |
| **vLLM DType** | `float32` | `auto` |
| **GPU Memory** | N/A | `--gpu-memory-utilization 0.85` |
| **Model Cards** | Small only | All available |
| **UI Banner** | Amber warning | Green success |
| **Performance** | 5-30s/response | 20-100+ tok/s |

## Testing the Switch

### 1. Verify Current Mode
```bash
cd backend
source venv/bin/activate
python -c "from app.core.config import settings; print(f'Mode: {settings.USE_GPU}')"
```

### 2. Switch Mode
```bash
# Edit config.py
sed -i 's/FORCE_CPU_MODE: bool = True/FORCE_CPU_MODE: bool = False/' app/core/config.py
```

### 3. Verify Change
```bash
python -c "from app.core.config import settings; print(f'Mode: {settings.USE_GPU}')"
```

### 4. Switch Back
```bash
sed -i 's/FORCE_CPU_MODE: bool = False/FORCE_CPU_MODE: bool = True/' app/core/config.py
```

## No Code Changes Required

✅ **Just flip one boolean flag**  
✅ **System auto-detects GPU**  
✅ **Frontend auto-updates**  
✅ **Safe to switch back and forth**  
✅ **No migration needed**  

## Summary

```
┌──────────────────────────────────────────┐
│   Single Point of Control               │
│                                          │
│   backend/app/core/config.py:41         │
│                                          │
│   FORCE_CPU_MODE: bool = ???            │
│                                          │
│   True  → CPU mode (testing)            │
│   False → GPU mode (auto-detect)        │
└──────────────────────────────────────────┘
```

**That's it!** One line controls the entire system behavior.



