# Setup Complete ✅

Your Courtroom Video Analyzer is now configured to use your video file directly!

## What Was Done

1. ✅ Switched to `test` branch
2. ✅ Updated `.env` with all API credentials
3. ✅ Configured direct video file path (no RTSP needed)
4. ✅ Installed frontend dependencies
5. ✅ Created quick start script
6. ✅ Updated documentation
7. ✅ Pushed all changes to GitHub

## Your Configuration

**Video File:**
```
/Users/keerthivasan/Vision/Great_Argument_by_lawyer_in_Murder_case._Accuse_is_a_22_year_old_girl._thelegalnow_720P.mp4
```

**API Keys:** All configured in `.env`
- Stream API ✅
- Twelve Labs API ✅
- VideoDB API ✅
- Deepgram API ✅
- TurboPuffer API ✅
- Gemini API ✅

## How to Run

### Option 1: One-Command Start (Recommended)

```bash
./start_demo.sh
```

### Option 2: Manual Start

```bash
uv run python demo.py
```

Both options will:
1. Start the backend API server on port 8000
2. Start the frontend dev server on port 5173
3. Begin processing your video file

## Access the Application

Open your browser:
```
http://localhost:5173
```

## What You'll See

1. **Video Player**: Your courtroom video playing
2. **Transcript Panel**: Real-time transcription with speaker labels
3. **Chat Interface**: Ask questions about the video

## Example Queries

Try these once the video is processing:

- "What did the lawyer say about the murder case?"
- "Show me when the witness testified"
- "Find objections in the trial"
- "What evidence was presented?"

## Verification

Check backend health:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "indexer": true,
  "mcp_server": true,
  "agent_running": true
}
```

## Stopping the Demo

Press `Ctrl+C` in the terminal where the demo is running.

## Troubleshooting

### Video file not found
- Check the path in `.env` is correct
- Ensure the file exists at that location

### Backend fails to start
- Verify UV is installed: `uv --version`
- Check Python version: `python --version` (need 3.11+)

### Frontend fails to start
- Verify pnpm is installed: `pnpm --version`
- Try reinstalling: `cd frontend && pnpm install`

### Port already in use
- Backend (8000): `lsof -i :8000` and kill the process
- Frontend (5173): `lsof -i :5173` and kill the process

## Documentation

- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Full Setup**: [DEMO_SETUP.md](DEMO_SETUP.md)
- **API Setup**: [API_SETUP.md](API_SETUP.md)
- **Main README**: [README.md](README.md)

## Next Steps

1. Run `./start_demo.sh`
2. Open http://localhost:5173
3. Wait for video processing to start
4. Try querying the video!

---

**Everything is ready to go!** 🚀
