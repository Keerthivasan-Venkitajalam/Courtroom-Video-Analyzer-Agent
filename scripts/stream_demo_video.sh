#!/bin/bash
# Stream the demo video file to RTSP server for testing
# First, start MediaMTX server, then stream the video

# Determine video file from MOCK_CAMERA_STREAM env var or .env file
VIDEO_FILE="${MOCK_CAMERA_STREAM}"

if [ -z "$VIDEO_FILE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [ -f "$SCRIPT_DIR/../.env" ]; then
    # shellcheck source=/dev/null
    . "$SCRIPT_DIR/../.env"
    VIDEO_FILE="${MOCK_CAMERA_STREAM}"
  fi
fi

if [ -z "$VIDEO_FILE" ]; then
  echo "❌ Error: MOCK_CAMERA_STREAM is not set. Please set it in your environment or in .env"
  exit 1
fi

echo "🎥 Starting RTSP stream from local video file..."
echo "Video: $VIDEO_FILE"
echo "Stream URL: rtsp://localhost:8554/courtcam"
echo ""
echo "⚠️  Make sure MediaMTX is running first!"
echo "   Run: mediamtx"
echo ""
echo "Press Ctrl+C to stop streaming"
echo ""

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ Error: Video file not found at $VIDEO_FILE"
    exit 1
fi

# Stream the video file to RTSP server with loop
ffmpeg -re -stream_loop -1 -i "$VIDEO_FILE" \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -c:a aac -f rtsp rtsp://localhost:8554/courtcam
