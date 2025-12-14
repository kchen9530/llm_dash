# 🚀 Server Deployment & Migration Guide

Complete guide for deploying this LLM Dashboard on a new server (Linux, GPU server, cloud instance, etc.)

---

## 📋 Table of Contents

1. [Quick Migration Checklist](#quick-migration-checklist)
2. [Server Requirements](#server-requirements)
3. [Fresh Server Setup (Linux)](#fresh-server-setup-linux)
4. [GPU Server Setup](#gpu-server-setup)
5. [Production Deployment](#production-deployment)
6. [Configuration Changes](#configuration-changes)
7. [Data Migration](#data-migration)
8. [Common Scenarios](#common-scenarios)

---

## 🎯 Quick Migration Checklist

When moving to a new server:

```
□ Server Preparation
  □ Install Python 3.10+
  □ Install Node.js 18+
  □ Install Git
  □ Install CUDA (for GPU server)
  
□ Copy Project Files
  □ Clone/copy project directory
  □ Don't copy: venv/, node_modules/, models_cache/
  
□ Backend Setup
  □ Create virtual environment
  □ Install dependencies
  □ Configure .env file
  □ Test backend startup
  
□ Frontend Setup
  □ Install npm dependencies
  □ Update API URL if needed
  □ Build for production (optional)
  
□ System Configuration
  □ Configure firewall
  □ Set up systemd services (optional)
  □ Configure reverse proxy (optional)
```

---

## 💻 Server Requirements

### Minimum Requirements (CPU Testing)
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, or macOS
- **CPU**: 4+ cores
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB free (for models cache)
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher

### Recommended (GPU Production)
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **GPU**: NVIDIA GPU with 16GB+ VRAM (RTX 3090, 4090, A100, etc.)
- **Storage**: 200GB+ SSD
- **CUDA**: 11.8+
- **Python**: 3.10
- **Node.js**: 18.x LTS

---

## 🐧 Fresh Server Setup (Linux)

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
sudo apt install -y \
    build-essential \
    curl \
    git \
    wget \
    python3.10 \
    python3.10-venv \
    python3-pip \
    nginx \
    supervisor

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3.10 --version  # Should show 3.10.x
node --version        # Should show v18.x
npm --version         # Should show 9.x+
```

### Step 2: Transfer Project Files

**Option A: From Git Repository**
```bash
cd /home/youruser
git clone https://github.com/yourusername/llm-dash.git
cd llm-dash
```

**Option B: From Your Mac (via scp)**
```bash
# On your Mac
cd /Users/kaichen/Desktop
tar czf llm-dash.tar.gz llm-dash/ \
    --exclude='llm-dash/backend/venv' \
    --exclude='llm-dash/frontend/node_modules' \
    --exclude='llm-dash/backend/models_cache'

# Copy to server
scp llm-dash.tar.gz user@server-ip:/home/youruser/

# On server
cd /home/youruser
tar xzf llm-dash.tar.gz
cd llm-dash
```

**Option C: From Git Clone (Recommended)**
```bash
# If you pushed to GitHub
ssh user@server-ip
git clone https://github.com/yourusername/llm-dash.git
cd llm-dash
```

### Step 3: Backend Setup on New Server

```bash
cd /home/youruser/llm-dash/backend

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# For CPU server (lightweight)
pip install -r requirements-lite.txt

# OR for GPU server (full installation)
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit configuration (see Configuration section below)
```

### Step 4: Frontend Setup on New Server

```bash
cd /home/youruser/llm-dash/frontend

# Install dependencies
npm install

# For development
npm run dev

# OR for production build
npm run build
```

### Step 5: Test the Setup

```bash
# Test backend
cd /home/youruser/llm-dash/backend
source venv/bin/activate
python run.py
# Should start on port 7860

# In another terminal, test frontend
cd /home/youruser/llm-dash/frontend
npm run dev
# Should start on port 5173
```

---

## 🎮 GPU Server Setup

If your new server has NVIDIA GPU:

### Step 1: Install CUDA Toolkit

```bash
# Check if GPU is detected
lspci | grep -i nvidia

# Install NVIDIA drivers
sudo apt install nvidia-driver-535  # or latest version

# Install CUDA Toolkit 11.8
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-11-8

# Add to PATH
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvidia-smi  # Should show GPU info
nvcc --version  # Should show CUDA version
```

### Step 2: Install Backend with GPU Support

```bash
cd /home/youruser/llm-dash/backend
source venv/bin/activate

# Install full requirements (includes vLLM)
pip install -r requirements.txt

# This will take 10-20 minutes and download ~3-5GB
```

### Step 3: Configure for GPU Mode

```bash
# Edit configuration
nano backend/app/core/config.py

# Change this line:
FORCE_CPU_MODE: bool = False  # Enable GPU auto-detection

# Or set in .env:
echo "FORCE_CPU_MODE=False" >> backend/.env
```

### Step 4: Test GPU

```bash
# Test PyTorch GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"

# Should output:
# CUDA available: True
# GPU count: 1 (or more)

# Start backend
python run.py
# Should show: "✅ GPU detected and enabled"
```

---

## 🏭 Production Deployment

### Option 1: Using Systemd Services

**Backend Service:**

```bash
# Create service file
sudo nano /etc/systemd/system/llm-dash-backend.service
```

```ini
[Unit]
Description=LLM Dashboard Backend
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/llm-dash/backend
Environment="PATH=/home/youruser/llm-dash/backend/venv/bin"
ExecStart=/home/youruser/llm-dash/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service:**

```bash
sudo nano /etc/systemd/system/llm-dash-frontend.service
```

```ini
[Unit]
Description=LLM Dashboard Frontend
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/llm-dash/frontend
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable llm-dash-backend
sudo systemctl enable llm-dash-frontend

# Start services
sudo systemctl start llm-dash-backend
sudo systemctl start llm-dash-frontend

# Check status
sudo systemctl status llm-dash-backend
sudo systemctl status llm-dash-frontend

# View logs
sudo journalctl -u llm-dash-backend -f
sudo journalctl -u llm-dash-frontend -f
```

### Option 2: Using Docker (Advanced)

```bash
# Create Dockerfile.backend
cat > backend/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app
COPY requirements-lite.txt .
RUN pip install --no-cache-dir -r requirements-lite.txt

COPY . .
CMD ["python", "run.py"]
EOF

# Create Dockerfile.frontend
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
CMD ["npm", "run", "dev"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "7860:7860"
    volumes:
      - ./backend:/app
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - FORCE_CPU_MODE=true
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
EOF

# Run with Docker Compose
docker-compose up -d
```

### Option 3: Nginx Reverse Proxy

```bash
# Install nginx
sudo apt install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/llm-dash
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /api/models/ws {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/llm-dash /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ⚙️ Configuration Changes

### Backend Configuration (.env)

```bash
# Edit backend/.env based on server type

# === CPU Server (8GB RAM) ===
HOST=0.0.0.0
PORT=7860
DEPLOYMENT_MODE=cpu
FORCE_CPU_MODE=True
MAX_MODEL_SIZE_GB=2
HF_HOME=/home/youruser/.cache/huggingface
TRANSFORMERS_CACHE=/home/youruser/.cache/huggingface

# === GPU Server (16GB+ RAM, NVIDIA GPU) ===
HOST=0.0.0.0
PORT=7860
DEPLOYMENT_MODE=gpu
FORCE_CPU_MODE=False
MAX_MODEL_SIZE_GB=20
HF_HOME=/data/models_cache  # Use fast storage
TRANSFORMERS_CACHE=/data/models_cache
VLLM_BASE_PORT=8000
VLLM_MAX_INSTANCES=5

# === Remote GPU Mode (Mac -> Remote Server) ===
HOST=0.0.0.0
PORT=7860
DEPLOYMENT_MODE=remote_gpu
GPU_SERVER_URL=http://gpu-server-ip:8000
GPU_SERVER_API_KEY=your-secret-key

# === China Network (with proxy) ===
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
HF_ENDPOINT=https://hf-mirror.com  # Optional: use mirror
```

### Backend Config File (app/core/config.py)

```python
# For CPU server
FORCE_CPU_MODE: bool = True

# For GPU server
FORCE_CPU_MODE: bool = False

# Model cache location
MODEL_CACHE_DIR: str = "/home/youruser/.cache/huggingface/hub"
# Or for large storage:
# MODEL_CACHE_DIR: str = "/data/models"
```

### Frontend Configuration

If backend is on different host:

```bash
# Edit frontend/src/lib/api.ts
# Change API_BASE_URL

# For development (same machine)
const API_BASE_URL = 'http://localhost:7860'

# For production (different domain)
const API_BASE_URL = 'https://your-api-domain.com'

# For server deployment (use relative URL)
const API_BASE_URL = window.location.origin
```

---

## 📦 Data Migration

### Migrating Model Cache (Optional)

If you've already downloaded models on your Mac and want to copy them to the server:

```bash
# On your Mac
cd ~/.cache/huggingface
tar czf models.tar.gz hub/

# Copy to server
scp models.tar.gz user@server-ip:/home/youruser/

# On server
cd /home/youruser/.cache/huggingface
tar xzf ~/models.tar.gz

# Or specify custom location
mkdir -p /data/models
tar xzf ~/models.tar.gz -C /data/models
```

### Database/State (Future)

Currently the app stores state in memory. For production:

```bash
# Optional: Add Redis for state persistence
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

---

## 🎭 Common Scenarios

### Scenario 1: Mac (Dev) → Ubuntu GPU Server (Production)

```bash
# 1. On Mac - prepare code
cd /Users/kaichen/Desktop/llm-dash
git add .
git commit -m "Ready for deployment"
git push

# 2. On Ubuntu GPU server
ssh user@gpu-server
git clone https://github.com/yourusername/llm-dash.git
cd llm-dash

# 3. Setup GPU environment
# Follow "GPU Server Setup" section above

# 4. Configure for GPU
echo "FORCE_CPU_MODE=False" > backend/.env

# 5. Install dependencies
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Full vLLM installation

cd ../frontend
npm install

# 6. Start services
# Use systemd services (see Production Deployment section)

# 7. Test
curl http://localhost:7860/health
```

### Scenario 2: Dual Setup (Mac Dev + Remote GPU)

**Keep Mac for development, use remote GPU for inference:**

```bash
# On GPU server - run only vLLM
vllm serve meta-llama/Llama-3-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000

# On Mac - configure to use remote GPU
cd /Users/kaichen/Desktop/llm-dash/backend
echo "GPU_SERVER_URL=http://gpu-server-ip:8000" >> .env
echo "DEPLOYMENT_MODE=remote_gpu" >> .env

# Start Mac dashboard
./start-mac.sh

# Now Mac UI talks to GPU server!
```

### Scenario 3: Testing Server (Small Models)

```bash
# On any Linux server (even small VPS)
git clone <repo>
cd llm-dash

# Lightweight setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lite.txt

cd ../frontend
npm install

# Configure for CPU
echo "FORCE_CPU_MODE=True" > backend/.env

# Start
./start-mac.sh  # Works on Linux too!
```

### Scenario 4: Production (Multiple GPUs)

```bash
# On multi-GPU server
nvidia-smi  # Check GPUs

# Configure for multiple instances
nano backend/app/core/config.py
# Set: VLLM_MAX_INSTANCES: int = 8  # Match GPU count

# Start
# vLLM will automatically distribute across GPUs
```

---

## 🔒 Security Considerations

### Firewall Setup

```bash
# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (if using SSL)
sudo ufw allow 7860/tcp  # Backend (internal only if behind nginx)
sudo ufw enable

# For API-only access (block frontend)
sudo ufw deny 5173/tcp
```

### SSL/HTTPS (Recommended for Production)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Environment Variables Security

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secrets management in production
# Option 1: Environment variables
export GPU_SERVER_API_KEY="secret"

# Option 2: Docker secrets
# Option 3: HashiCorp Vault
```

---

## 🧪 Testing Your New Server

```bash
# 1. Check Python
python3 --version

# 2. Check GPU (if applicable)
nvidia-smi

# 3. Check backend
cd backend
source venv/bin/activate
python -c "from app.main import app; print('✅ Backend OK')"

# 4. Check frontend
cd ../frontend
npm run build  # Should complete without errors

# 5. Test API
curl http://localhost:7860/health
# Should return: {"status":"healthy"}

# 6. Test model deployment
# Use the dashboard UI or:
curl -X POST http://localhost:7860/api/models/deploy \
  -H "Content-Type: application/json" \
  -d '{"model_name":"gpt2","parameters":{}}'
```

---

## 📊 Performance Tuning

### For CPU Servers
```bash
# Limit concurrent requests
export UVICORN_WORKERS=2

# Use smaller models
export DEFAULT_MODEL="Qwen/Qwen2-0.5B-Instruct"
```

### For GPU Servers
```bash
# GPU memory utilization
export GPU_MEMORY_UTILIZATION=0.9

# Enable tensor parallelism (multi-GPU)
export TENSOR_PARALLEL_SIZE=2  # For 2 GPUs
```

---

## 🆘 Troubleshooting on New Server

### Port already in use
```bash
# Find and kill process
sudo lsof -ti:7860 | xargs kill
sudo lsof -ti:5173 | xargs kill
```

### Permission denied
```bash
# Fix ownership
sudo chown -R $USER:$USER /home/youruser/llm-dash

# Fix permissions
chmod +x start-mac.sh
```

### Module not found
```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements-lite.txt --force-reinstall
```

### GPU not detected
```bash
# Check CUDA
nvidia-smi
nvcc --version

# Reinstall PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 📝 Quick Reference Commands

```bash
# Check status
sudo systemctl status llm-dash-backend
sudo systemctl status llm-dash-frontend

# View logs
sudo journalctl -u llm-dash-backend -f
sudo journalctl -u llm-dash-frontend -f

# Restart services
sudo systemctl restart llm-dash-backend
sudo systemctl restart llm-dash-frontend

# Stop services
sudo systemctl stop llm-dash-backend
sudo systemctl stop llm-dash-frontend

# Update code
cd /home/youruser/llm-dash
git pull
sudo systemctl restart llm-dash-backend
cd frontend && npm run build
sudo systemctl restart llm-dash-frontend
```

---

## ✅ Deployment Checklist Summary

```
Mac → Linux Server Migration:
□ Prepare server (install Python, Node, CUDA if GPU)
□ Transfer files (git clone or scp)
□ Setup backend (venv, install deps, configure .env)
□ Setup frontend (npm install, build)
□ Configure for server type (CPU vs GPU)
□ Setup systemd services (for auto-start)
□ Configure nginx (for production)
□ Setup firewall (security)
□ Test deployment (health check, deploy model, chat)
□ Monitor logs (ensure everything running)
```

---

**Your deployment is ready! 🚀**

For more help, see:
- `MAC_SETUP.md` - Original Mac setup
- `CPU_GPU_SWITCH.md` - Switching between modes
- `CHINA_NETWORK_GUIDE.md` - Network setup in China

