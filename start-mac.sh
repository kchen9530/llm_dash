#!/bin/bash

# LLM Dashboard - Mac Startup Script (8GB RAM Optimized)
# This script starts both backend and frontend in separate terminal tabs

set -e

echo "🚀 Starting LLM Dashboard (Mac CPU Mode)"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the llm-dash directory"
    exit 1
fi

# Start backend in background
echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend in background  
echo -e "${GREEN}🎨 Starting Frontend (Vite)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ LLM Dashboard Started!${NC}"
echo "=========================================="
echo -e "${BLUE}Backend:${NC}  http://localhost:7860"
echo -e "${GREEN}Frontend:${NC} http://localhost:5173"
echo ""
echo -e "${YELLOW}📝 Recommended tiny models for 8GB RAM:${NC}"
echo "   - gpt2 (500MB, fastest)"
echo "   - Qwen/Qwen2-0.5B-Instruct (1GB)"
echo "   - TinyLlama/TinyLlama-1.1B-Chat-v1.0 (2GB)"
echo ""
echo -e "${YELLOW}⚠️  Note: CPU inference is SLOW. First load takes 2-5 minutes.${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait


