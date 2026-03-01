#!/bin/bash
# One-command demo launcher

echo "🚀 Starting Courtroom Video Analyzer Demo..."
echo ""
echo "Configuration:"
echo "  Video: /Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the demo
uv run python demo.py
