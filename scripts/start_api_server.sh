#!/bin/bash
# Start the API server for frontend-to-backend integration

echo "=========================================="
echo "Starting Courtroom Video Analyzer API"
echo "=========================================="
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start the API server
python api_server.py
