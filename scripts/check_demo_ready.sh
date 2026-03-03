#!/bin/bash
# Check if all prerequisites for the demo are installed

echo "🔍 Checking Demo Prerequisites..."
echo ""

MISSING=0

# Check UV
if command -v uv &> /dev/null; then
    echo "✅ UV installed ($(uv --version))"
else
    echo "❌ UV not found. Install with: brew install uv"
    MISSING=1
fi

# Check pnpm
if command -v pnpm &> /dev/null; then
    echo "✅ pnpm installed ($(pnpm --version))"
else
    echo "❌ pnpm not found. Install with: brew install pnpm"
    MISSING=1
fi

# Check video file from .env
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Extract video file path from .env
    VIDEO_FILE=$(grep "^MOCK_CAMERA_STREAM=" .env | cut -d'=' -f2)
    
    if [ -n "$VIDEO_FILE" ]; then
        if [[ "$VIDEO_FILE" == rtsp://* ]] || [[ "$VIDEO_FILE" == http://* ]]; then
            echo "ℹ️  Using stream URL: $VIDEO_FILE"
            echo "⚠️  Note: For RTSP streams, you'll need MediaMTX and FFmpeg"
        elif [ -f "$VIDEO_FILE" ]; then
            echo "✅ Video file found: $VIDEO_FILE"
            FILE_SIZE=$(du -h "$VIDEO_FILE" | cut -f1)
            echo "   File size: $FILE_SIZE"
        else
            echo "❌ Video file not found: $VIDEO_FILE"
            MISSING=1
        fi
    else
        echo "⚠️  MOCK_CAMERA_STREAM not configured in .env"
    fi
    
    # Check for required API keys
    if grep -q "^STREAM_API_KEY=.\+" .env; then
        echo "✅ Stream API key configured"
    else
        echo "⚠️  Stream API key might not be configured"
    fi
    
    if grep -q "TWELVE_LABS_API_KEY=tlk_" .env; then
        echo "✅ Twelve Labs API key configured"
    else
        echo "⚠️  Twelve Labs API key might not be configured"
    fi
    
    if grep -q "VIDEODB_API_KEY=sk-" .env; then
        echo "✅ VideoDB API key configured"
    else
        echo "⚠️  VideoDB API key might not be configured"
    fi
else
    echo "❌ .env file not found"
    MISSING=1
fi

# Check frontend dependencies
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  Frontend dependencies not installed. Run: cd frontend && pnpm install"
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo "🎉 All prerequisites are ready! You can start the demo."
    echo ""
    echo "Quick start:"
    echo "  uv run python demo.py"
    echo ""
    echo "Then open: http://localhost:5173"
else
    echo "⚠️  Some prerequisites are missing. Please install them first."
    exit 1
fi
