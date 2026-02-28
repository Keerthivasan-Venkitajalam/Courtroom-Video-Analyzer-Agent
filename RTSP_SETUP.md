# RTSP Stream Setup Guide

This guide explains how to set up a mock RTSP stream for testing the Courtroom Video Analyzer Agent.

## Option 1: Using OBS Studio (Recommended)

### Installation

**macOS**:
```bash
brew install obs
```

**Linux**:
```bash
sudo apt-get install obs-studio
```

**Windows**:
Download from https://obsproject.com/

### Configuration Steps

1. **Install OBS Studio** using the command above

2. **Install RTSP Server Plugin**:
   - Download the OBS RTSP Server plugin from: https://github.com/iamscottxu/obs-rtspserver
   - Follow installation instructions for your platform

3. **Configure OBS**:
   - Open OBS Studio
   - Go to Settings → Stream
   - Select "Custom" as Service
   - Set Server to: `rtsp://localhost:8554/courtcam`

4. **Add Video Source**:
   - Click "+" in Sources panel
   - Select "Media Source"
   - Choose your mock trial video file
   - Enable "Loop" to play continuously

5. **Start Streaming**:
   - Click "Start Streaming" in OBS
   - Your RTSP stream is now available at `rtsp://localhost:8554/courtcam`

## Option 2: Using FFmpeg

If you have a video file and want to stream it via RTSP:

### Installation

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt-get install ffmpeg
```

### Stream a Video File

```bash
ffmpeg -re -stream_loop -1 -i mock_trial.mp4 \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -c:a aac -f rtsp rtsp://localhost:8554/courtcam
```

Parameters:
- `-re`: Read input at native frame rate
- `-stream_loop -1`: Loop indefinitely
- `-preset ultrafast`: Fast encoding
- `-tune zerolatency`: Minimize latency

## Option 3: Using MediaMTX (RTSP Server)

MediaMTX is a lightweight RTSP server that can relay streams.

### Installation

**macOS**:
```bash
brew install mediamtx
```

**Linux**:
```bash
wget https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_linux_amd64.tar.gz
tar -xzf mediamtx_linux_amd64.tar.gz
```

### Configuration

1. **Start MediaMTX**:
   ```bash
   mediamtx
   ```

2. **Publish a stream** using FFmpeg:
   ```bash
   ffmpeg -re -stream_loop -1 -i mock_trial.mp4 \
     -c copy -f rtsp rtsp://localhost:8554/courtcam
   ```

## Mock Trial Video Sources

You can use any of these sources for testing:

1. **Public Domain Court Footage**:
   - Search YouTube for "public domain court proceedings"
   - Download using `yt-dlp`: `yt-dlp <youtube-url>`

2. **Create Your Own**:
   - Record a mock trial scenario
   - Use screen recording of legal proceedings

3. **Sample Videos**:
   - Use any MP4 video file for initial testing
   - Ensure it has audio for transcription testing

## Verification

Test your RTSP stream is working:

```bash
# Using FFplay (comes with FFmpeg)
ffplay rtsp://localhost:8554/courtcam

# Using VLC
vlc rtsp://localhost:8554/courtcam
```

## Environment Configuration

Update your `.env` file:
```bash
MOCK_CAMERA_STREAM=rtsp://localhost:8554/courtcam
```

## Troubleshooting

### Stream not accessible
- Verify the RTSP server is running
- Check firewall settings allow port 8554
- Ensure the video file path is correct

### High latency
- Use `-tune zerolatency` with FFmpeg
- Reduce video resolution if needed
- Check network conditions

### Audio issues
- Verify audio codec is supported (AAC recommended)
- Check audio is present in source video
- Test with `ffprobe <video-file>` to inspect streams

## Production Considerations

For production deployment:
- Use actual courtroom camera feeds
- Implement authentication for RTSP streams
- Consider using SRT or WebRTC for lower latency
- Set up redundant streams for reliability

## Resolution Support

The system supports:
- 720p (1280x720) - Minimum
- 1080p (1920x1080) - Recommended
- 4K (3840x2160) - Maximum

Configure in OBS or FFmpeg based on your needs.
