#!/bin/bash

# ============================================================================
# PHARMA INVENTORY OPTIMIZATION PLATFORM - STARTUP SCRIPT
# ============================================================================
# This script starts the complete application:
#   - FastAPI backend on port 8000
#   - Streamlit dashboard on port 8501
# ============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🏥 PHARMA INVENTORY OPTIMIZATION PLATFORM"
echo "=========================================="
echo ""

# Kill any existing processes
echo "🛑 Stopping any existing processes..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 2

echo ""
echo "✅ Previous processes stopped"
echo ""

# Start FastAPI
echo "🚀 Starting FastAPI backend..."
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!

sleep 3

# Check if FastAPI started
if ps -p $FASTAPI_PID > /dev/null 2>&1; then
    echo "✅ FastAPI started (PID: $FASTAPI_PID)"
else
    echo "❌ FastAPI failed to start"
    cat /tmp/fastapi.log
    exit 1
fi

echo ""

# Start Streamlit
echo "🎨 Starting Streamlit dashboard..."
streamlit run dashboard.py --logger.level=warning > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!

sleep 4

# Check if Streamlit bound to port
if lsof -i :8501 > /dev/null 2>&1; then
    echo "✅ Streamlit started (PID: $STREAMLIT_PID)"
else
    echo "❌ Streamlit failed to bind to port 8501"
    cat /tmp/streamlit.log | tail -20
    kill $FASTAPI_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ APPLICATION READY!"
echo "=========================================="
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔧 API:       http://127.0.0.1:8000"
echo ""
echo "FastAPI PID:  $FASTAPI_PID"
echo "Streamlit PID: $STREAMLIT_PID"
echo ""
echo "To stop the application:"
echo "  kill $FASTAPI_PID $STREAMLIT_PID"
echo "  or press Ctrl+C multiple times"
echo ""

# Keep script running
wait
