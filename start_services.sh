#!/bin/bash
# Bob Sentinel - Start Backend API and Frontend Dashboard

echo "🚀 Starting Bob Sentinel Services..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ All dependencies ready!"
echo ""

# Start backend API in background
echo "🔧 Starting Backend API Server on http://localhost:8000..."
python3 src/api_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend Dashboard on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✨ Bob Sentinel is running!"
echo ""
echo "📊 Dashboard: http://localhost:5173"
echo "🔌 API: http://localhost:8000"
echo "💚 Health Check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait

# Made with Bob
