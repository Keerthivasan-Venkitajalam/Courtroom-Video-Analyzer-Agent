# Demo Setup Guide - Direct Video File Mode

This guide will help you run the demo with your local video file directly (no RTSP streaming required).

## Prerequisites

1. **Install UV** (Python package manager):
   ```bash
   brew install uv
   ```

2. **Install pnpm** (Frontend package manager):
   ```bash
   brew install pnpm
   ```

## Setup Steps

### 1. Verify Environment Configuration

Your `.env` file is already configured with:
- ✅ All API keys (Stream, Twelve Labs, VideoDB, Deepgram, TurboPuffer, Gemini)
- ✅ Video file path: `/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4`

The system will automatically detect that you're using a local file (not an RTSP stream) and upload it directly to VideoDB for processing.

### 2. Install Frontend Dependencies

```bash
cd frontend
pnpm install
cd ..
```

### 3. Start the Demo Application

```bash
uv run python demo.py
```

This single command will:
- Upload your video file to VideoDB
- Start Twelve Labs Pegasus 1.2 scene indexing
- Start the backend API server on port 8000
- Start the frontend dev server on port 5173
- Initialize the Vision Agent

## Accessing the Demo

Open your browser and navigate to:
```
http://localhost:5173
```

You should see:
- Video player with your courtroom footage
- Real-time transcript panel (as the video is processed)
- Chat interface for querying the agent

## What Happens Behind the Scenes

1. **Video Upload**: Your local MP4 file is uploaded to VideoDB
2. **Scene Indexing**: Twelve Labs Pegasus 1.2 analyzes the video for:
   - Visual events (evidence presentation, gestures, objections)
   - Speaker identification (judge, witness, attorneys)
   - Legal terminology and courtroom actions
3. **Transcript Processing**: Deepgram transcribes audio with speaker diarization
4. **Hybrid Search**: TurboPuffer indexes transcript segments for fast retrieval
5. **Agent Ready**: Gemini 2.0 Flash connects to answer queries in real-time

## Verification

1. **Check Backend API**:
   ```bash
   curl http://localhost:8000/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "indexer": true,
     "mcp_server": true,
     "agent_running": true,
     "scene_index_id": "..."
   }
   ```

2. **Check Frontend**:
   Open http://localhost:5173 in your browser

3. **Check Video Processing**:
   The backend logs will show:
   ```
   Pegasus 1.2 indexing started | index_id=...
   ```

## Troubleshooting

### Video file not found
- Verify the path in `.env` matches your video location
- Current path: `/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4`
- Check file exists: `ls -lh "/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4"`

### Backend fails to start
- Check all API keys are set in `.env`
- Verify UV is installed: `uv --version`
- Check Python version: `python --version` (should be 3.11+)
- Check logs for specific errors

### Frontend fails to start
- Ensure pnpm is installed: `pnpm --version`
- Run `cd frontend && pnpm install` again
- Check port 5173 is available: `lsof -i :5173`

### Video upload fails
- Check VideoDB API key is valid
- Verify video file is accessible and not corrupted
- Check file size (VideoDB may have upload limits)
- Review backend logs for specific error messages

### Indexing takes too long
- Twelve Labs Pegasus 1.2 processes video in real-time
- For a 10-minute video, expect 10-15 minutes of processing
- You can query the agent while indexing is in progress
- Check indexing status in backend logs

## Environment Variables

All required API keys are configured in `.env`:
- ✅ Stream API (GetStream.io) - for real-time video streaming
- ✅ Twelve Labs API - for Pegasus 1.2 video intelligence
- ✅ VideoDB API - for video storage and scene indexing
- ✅ Deepgram API - for audio transcription with diarization
- ✅ TurboPuffer API - for hybrid search (BM25 + vector)
- ✅ Gemini API - for the AI agent (Gemini 2.0 Flash)

## Quick Start

```bash
# Install frontend dependencies (first time only)
cd frontend && pnpm install && cd ..

# Start everything
uv run python demo.py

# Open browser
open http://localhost:5173
```

## Stopping the Demo

Press `Ctrl+C` in the terminal running `demo.py` to stop everything gracefully.

## Notes

- The video file is uploaded once and cached by VideoDB
- Transcription and scene indexing happen asynchronously
- You can start querying as soon as the agent is ready
- The system maintains timestamp alignment between video and transcript
- All queries are answered using only the indexed video content (no hallucinations)

## Alternative: RTSP Streaming Mode

If you prefer to use RTSP streaming instead of direct file upload:

1. Install MediaMTX and FFmpeg:
   ```bash
   brew install mediamtx ffmpeg
   ```

2. Update `.env`:
   ```bash
   MOCK_CAMERA_STREAM=rtsp://localhost:8554/courtcam
   ```

3. Start MediaMTX (Terminal 1):
   ```bash
   mediamtx
   ```

4. Stream your video (Terminal 2):
   ```bash
   ./scripts/stream_demo_video.sh
   ```

5. Start demo (Terminal 3):
   ```bash
   uv run python demo.py
   ```
