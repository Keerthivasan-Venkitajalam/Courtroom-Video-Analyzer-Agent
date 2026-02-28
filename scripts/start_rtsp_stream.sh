#!/bin/bash
# start_rtsp_stream.sh
# Script to start a mock RTSP stream for testing

set -e

echo "🎥 Starting Mock RTSP Stream for Courtroom Video Analyzer"
echo "=========================================================="

# Check if video file is provided
if [ -z "$1" ]; then
    echo "❌ Error: No video file provided"
    echo ""
    echo "Usage: ./scripts/start_rtsp_stream.sh <video_file>"
    echo ""
    echo "Example:"
    echo "  ./scripts/start_rtsp_stream.sh mock_trial.mp4"
    exit 1
fi

VIDEO_FILE="$1"

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ Error: Video file not found: $VIDEO_FILE"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ Error: ffmpeg is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Linux:   sudo apt-get install ffmpeg"
    exit 1
fi

# RTSP stream configuration
RTSP_URL="rtsp://localhost:8554/courtcam"
RESOLUTION="${2:-1920x1080}"  # Default to 1080p
FPS="${3:-30}"  # Default to 30 FPS

echo ""
echo "Configuration:"
echo "  Video File: $VIDEO_FILE"
echo "  RTSP URL:   $RTSP_URL"
echo "  Resolution: $RESOLUTION"
echo "  FPS:        $FPS"
echo ""
echo "Starting stream... (Press Ctrl+C to stop)"
echo ""

# Start FFmpeg RTSP stream
ffmpeg -re -stream_loop -1 -i "$VIDEO_FILE" \
    -vf "scale=$RESOLUTION" \
    -r "$FPS" \
    -c:v libx264 \
    -preset ultrafast \
    -tune zerolatency \
    -b:v 2M \
    -maxrate 2M \
    -bufsize 4M \
    -c:a aac \
    -b:a 128k \
    -f rtsp \
    "$RTSP_URL"
