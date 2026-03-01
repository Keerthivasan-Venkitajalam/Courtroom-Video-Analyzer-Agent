#!/bin/bash
# Stream the demo video file to RTSP server for testing
# First, start MediaMTX server, then stream the video

VIDEO_FILE="/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4"

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
