#!/bin/bash
# test_rtsp_stream.sh
# Script to test if RTSP stream is accessible

set -e

RTSP_URL="${1:-rtsp://localhost:8554/courtcam}"

echo "🔍 Testing RTSP Stream"
echo "====================="
echo "URL: $RTSP_URL"
echo ""

# Check if ffprobe is installed
if ! command -v ffprobe &> /dev/null; then
    echo "❌ Error: ffprobe is not installed (comes with ffmpeg)"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Linux:   sudo apt-get install ffmpeg"
    exit 1
fi

echo "Probing stream..."
echo ""

# Probe the RTSP stream
if ffprobe -v error -show_entries stream=codec_name,codec_type,width,height,r_frame_rate -of default=noprint_wrappers=1 "$RTSP_URL" 2>&1; then
    echo ""
    echo "✅ RTSP stream is accessible and valid!"
else
    echo ""
    echo "❌ Failed to access RTSP stream"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure the RTSP server is running"
    echo "  2. Check if port 8554 is open"
    echo "  3. Verify the stream URL is correct"
    exit 1
fi
