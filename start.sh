#!/bin/bash

# AgentPay Mesh - Concurrent Development Startup Script
# This script starts both the Python backend and Next.js frontend concurrently

echo "🚀 Starting AgentPay Mesh..."
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""

# Kill any existing processes on ports 8000 and 3000
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start the Python backend
echo "🐍 Starting Python backend..."
cd "$(dirname "$0")"
python run.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Start the Next.js frontend
echo "⚛️  Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Both services started!"
echo "   → Backend running at http://localhost:8000"
echo "   → Frontend running at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Handle Ctrl+C to kill both processes
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for any process to exit
wait