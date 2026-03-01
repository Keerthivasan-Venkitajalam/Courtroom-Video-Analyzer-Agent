# Quick Start Guide - Direct Video File

This guide shows you how to run the demo using your local video file directly (no RTSP streaming needed).

## Prerequisites

Install the required tools:

```bash
# Install UV (Python package manager)
brew install uv

# Install pnpm (Frontend package manager)
brew install pnpm
```

## Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
pnpm install
cd ..
```

### 2. Verify Configuration

Your `.env` file is already configured to use the video file directly:

```bash
MOCK_CAMERA_STREAM=/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4
```

All API keys are already set up.

## Running the Demo

### Single Command Launch

Simply run:

```bash
uv run python demo.py
```

This will:
1. Start the backend API server on port 8000
2. Start the frontend dev server on port 5173
3. Begin processing your video file automatically

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

You should see:
- Video player showing your courtroom footage
- Real-time transcript panel (as the video is processed)
- Chat interface for querying the agent

## What Happens Behind the Scenes

1. **Video Processing**: The backend reads your MP4 file directly and processes it frame-by-frame
2. **Audio Transcription**: Deepgram transcribes the audio with speaker diarization
3. **Visual Analysis**: Twelve Labs Pegasus analyzes the video for legal events
4. **Indexing**: Transcript and video moments are indexed in TurboPuffer and VideoDB
5. **Query Interface**: You can ask questions about anything in the video

## Testing the System

Once the application is running, try these queries in the chat:

- "What did the lawyer say about the murder case?"
- "Show me when evidence was presented"
- "Find objections in the trial"
- "What was the witness testimony about?"

## Verification

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "indexer": true,
  "mcp_server": true,
  "agent_running": true,
  "scene_index_id": "..."
}
```

### Check Frontend

Open http://localhost:5173 - you should see the UI load

## Stopping the Demo

Press `Ctrl+C` in the terminal where `demo.py` is running. This will gracefully shut down both the backend and frontend.

## Troubleshooting

### Video file not found
- Verify the path in `.env` matches your video location
- Current path: `/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4`

### Backend fails to start
- Check all API keys are set in `.env`
- Verify UV is installed: `uv --version`
- Check Python version: `python --version` (should be 3.11+)

### Frontend fails to start
- Ensure pnpm is installed: `pnpm --version`
- Run `cd frontend && pnpm install` again
- Check port 5173 is available: `lsof -i :5173`

### Processing is slow
- Video processing happens in real-time as the video plays
- First-time indexing may take a few minutes depending on video length
- Subsequent queries will be fast (< 500ms)

## Architecture

```
┌─────────────────┐
│  Your Video     │
│  File (MP4)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │
│  (Port 8000)    │
│                 │
│  • Video Proc   │
│  • Transcription│
│  • Indexing     │
│  • Query Engine │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Frontend UI    │
│  (Port 5173)    │
│                 │
│  • Video Player │
│  • Transcript   │
│  • Chat         │
└─────────────────┘
```

## Next Steps

- Try different queries to test the system
- Check the transcript panel for real-time transcription
- Use the video player to navigate to specific moments
- Monitor the backend logs for processing details

## Environment Variables

All configured in `.env`:
- ✅ Stream API (GetStream.io)
- ✅ Twelve Labs API (Video Intelligence)
- ✅ VideoDB API (Video Storage)
- ✅ Deepgram API (Transcription)
- ✅ TurboPuffer API (Vector Search)
- ✅ Gemini API (Agent Intelligence)
- ✅ Video File Path (Direct MP4)
