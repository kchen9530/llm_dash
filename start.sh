#!/bin/bash

echo "🚀 Starting LLM Local Ops Center..."

# 检查端口
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# 启动后端
start_backend() {
    echo "📡 Starting Backend (Port 7860)..."
    cd backend
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt
    python run.py &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
}

# 启动前端
start_frontend() {
    echo "🎨 Starting Frontend (Port 5173)..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# 清理函数
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# 主流程
check_port 7860 || exit 1
check_port 5173 || exit 1

start_backend
sleep 3
start_frontend

echo ""
echo "✨ LLM Local Ops Center is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:7860"
echo "   API Docs: http://localhost:7860/docs"
echo ""
echo "Press Ctrl+C to stop"

wait

