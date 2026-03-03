#!/bin/bash
# One-command demo launcher

echo "🚀 Starting Courtroom Video Analyzer Demo..."
echo ""
VIDEO=$(grep "^MOCK_CAMERA_STREAM=" .env | cut -d'=' -f2)
echo "Configuration:"
echo "  Video: $VIDEO"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the demo
uv run python demo.py
