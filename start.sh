#!/bin/bash

# One-command startup script for Job Application Workflow Dashboard
# Starts both backend and frontend servers

set -e

echo "============================================================"
echo "  Job Application Workflow Dashboard"
echo "  Bhavesh Chainani - Application Pipeline Management"
echo "============================================================"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ Virtual environment not found. Please create one first:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed."
    echo "   Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped. Goodbye!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start backend
echo ""
echo "🚀 Starting backend server on http://localhost:8000..."
python backend/main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check /tmp/backend.log for details"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server on http://localhost:3000..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start. Check /tmp/frontend.log for details"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 2
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sleep 2
    xdg-open http://localhost:3000 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "✅ Dashboard is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop both servers"
echo "============================================================"
echo ""

# Wait for user interrupt
wait $BACKEND_PID $FRONTEND_PID











