# Courtroom Video Analyzer Agent - Project Status

## 🎯 Project Overview

A real-time multimodal AI system for querying live courtroom proceedings with sub-500ms latency, built for the WeMakeDevs "Vision Possible: Agent Protocol" Hackathon.

## ✅ Completed Tasks

### Phase 1: Infrastructure Setup (COMPLETED)

#### ✓ Task 1.1: Frontend Project Bootstrap
- React + TypeScript project created with Vite 8 beta
- Located in `./frontend/` directory
- Dependencies installed and ready

#### ✓ Task 2.1: Vision Agents SDK Configuration
- Requirements file created with all dependencies
- Environment variables configured in `.env`
- Stream API credentials integrated (API Key: x563t6g4ysy7)

#### ✓ Task 3.1: Repository & API Keys Setup
- `.gitignore` configured to exclude secrets
- `.env.example` template created
- Stream, Twelve Labs, VideoDB, Deepgram, TurboPuffer, Gemini placeholders ready

#### ✓ Task 4.1: TurboPuffer Database Structure
- Configuration in `constants.py` (chunk_size=1000, overlap=100)
- Integration code in `index.py`

### Core Python Modules Created

#### 1. `constants.py` ✅
- All API keys and configuration
- Shared epoch offset for timestamp synchronization
- Latency budgets (Query: 100ms, Search: 150ms, Video: 200ms, Playback: 50ms)
- Speaker role mapping (0=Judge, 1=Witness, 2=Prosecution, 3=Defense)
- Pegasus legal domain prompt
- Gemini system prompt with anti-hallucination instructions

#### 2. `processor.py` ✅
- `CourtroomProcessor` class for video/audio processing
- Configured for 5 FPS processing
- `process_audio_chunk()` for Deepgram STT with speaker diarization
- `process_frame()` for YOLO entity detection
- Belief drift prevention through temporal consistency

#### 3. `index.py` ✅
- `CourtroomIndexer` class for video and transcript indexing
- VideoDB + Twelve Labs Pegasus 1.2 integration
- TurboPuffer hybrid search (BM25 + vector)
- `start_live_indexing()` for RTStream connection
- `query_video_moments()` for semantic video search
- `query_transcript()` for hybrid transcript search

#### 4. `agent.py` ✅
- Main orchestration logic
- Gemini Live API integration
- MCP tool registration (`search_video`, `search_transcript`)
- Vision processor attachment
- Stream Edge network connection

#### 5. `demo.py` ✅
- 1-click launch script
- Frontend and backend coordination
- Graceful shutdown handling

#### 6. `README.md` ✅
- Complete project documentation
- Architecture overview
- Installation instructions
- Tech stack table
- Performance metrics

## 📋 Next Steps (Remaining Tasks)

### Immediate Priority

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   # or
   uv pip install -r requirements.txt
   ```

2. **Obtain Missing API Keys**
   - Twelve Labs API key (https://twelvelabs.io/)
   - VideoDB API key (https://videodb.io/)
   - Deepgram API key (https://deepgram.com/)
   - TurboPuffer API key (https://turbopuffer.com/)
   - Gemini API key (https://ai.google.dev/)

3. **Install Stream Video SDK in Frontend**
   ```bash
   cd frontend
   npm install @stream-io/video-react-sdk hls.js
   ```

4. **Set Up Mock RTSP Stream (Task 3.2)**
   - Install OBS Studio
   - Configure virtual camera at rtsp://localhost:8554/courtcam
   - Use pre-recorded mock trial video

### Phase 2: Core Implementation (Day 1 Afternoon)

- Task 1.2: Create mock WebRTC courtroom room
- Task 2.2: Deploy baseline Echo voice agent
- Task 5.1-5.3: Build Evidentiary Player UI
- Task 6.1-6.3: Complete processor implementation
- Task 7.1-7.3: Complete VideoDB integration
- Task 8.1-8.3: Complete MCP server and hybrid search

### Phase 3: Integration (Day 2 Morning)

- Task 9.1-9.2: Frontend-backend handshake
- Task 10.1-10.2: Agent orchestration wiring
- Task 11.1-11.2: Timestamp synchronization

### Phase 4: Testing & Optimization (Day 2 Afternoon)

- Task 12.1-12.2: Mock trial stress test
- Task 13.1: Edge case testing
- Task 14.1: Pegasus prompt optimization
- Task 15.1: Hybrid search tuning

### Phase 5: Finalization (Day 2 Evening)

- Task 16.1-16.2: UI polish and demo video
- Task 17.1: Comprehensive README
- Task 18.1-18.2: Repository finalization
- Task 19.1-19.2: Technical blog and submission

## 🏗️ Project Structure

```
courtroom-video-analyzer/
├── .env                          # ✅ API keys and secrets
├── .env.example                  # ✅ Template
├── .gitignore                    # ✅ Security configured
├── README.md                     # ✅ Documentation
├── requirements.txt              # ✅ Python dependencies
├── constants.py                  # ✅ Configuration
├── processor.py                  # ✅ Video/audio processing
├── index.py                      # ✅ VideoDB + TurboPuffer
├── agent.py                      # ✅ Main orchestration
├── demo.py                       # ✅ Launch script
├── frontend/                     # ✅ React + TypeScript
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── .kiro/specs/courtroom-video-analyzer/
    ├── requirements.md           # ✅ 15 requirements
    ├── design.md                 # ✅ Architecture + 61 properties
    └── tasks.md                  # ✅ 19 implementation tasks
```

## 🎯 Critical Integration Checkpoints

| Checkpoint | Time | Status | Success Criteria |
|------------|------|--------|------------------|
| Echo Agent Live | Day 1, 12:30 PM | ⏳ Pending | Voice echoes within 500ms |
| RTStream Active | Day 1, 5:00 PM | ⏳ Pending | Twelve Labs logs scene_index_id |
| MCP Tools Fire | Day 1, 9:00 PM | ⏳ Pending | Both tools return valid results |
| UI ↔️ Agent Handshake | Day 2, 11:00 AM | ⏳ Pending | Query in UI → HLS plays |
| Timestamp Sync | Day 2, 1:00 PM | ⏳ Pending | Video matches transcript exactly |
| Full Stress Test | Day 2, 4:00 PM | ⏳ Pending | 20-min trial queryable <500ms |

## 🔑 API Keys Status

| Service | Status | Notes |
|---------|--------|-------|
| Stream | ✅ Configured | API Key: x563t6g4ysy7 |
| Twelve Labs | ⚠️ Needed | Sign up at twelvelabs.io |
| VideoDB | ⚠️ Needed | Sign up at videodb.io |
| Deepgram | ⚠️ Needed | Sign up at deepgram.com |
| TurboPuffer | ⚠️ Needed | Sign up at turbopuffer.com |
| Gemini | ⚠️ Needed | Get from ai.google.dev |

## 🚀 Quick Start Commands

### 1. Install Dependencies
```bash
# Python backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install @stream-io/video-react-sdk hls.js
cd ..
```

### 2. Configure API Keys
```bash
# Edit .env file with your API keys
nano .env
```

### 3. Run the System
```bash
# Option 1: Full demo (frontend + backend)
python demo.py

# Option 2: Backend only
python agent.py

# Option 3: Frontend only
cd frontend && npm run dev
```

## 📊 Progress Summary

- **Completed**: 4/19 major tasks (21%)
- **In Progress**: Infrastructure setup phase
- **Next Milestone**: Echo Agent Live (Day 1, 12:30 PM)
- **Time Remaining**: ~46 hours (assuming 48-hour hackathon)

## 🎓 Key Technical Decisions

1. **Latency Optimization**: Parallel processing (video + transcript search)
2. **Timestamp Sync**: Shared epoch offset in constants.py
3. **Hybrid Search**: BM25 for exact legal terms + vector for semantic
4. **Belief Drift Prevention**: Temporal consistency checks in processor
5. **Security**: All secrets in .env, excluded from git

## 📝 Notes

- Stream credentials are already configured and ready to use
- All Python modules have placeholder implementations ready for API integration
- Frontend scaffolding is complete with Vite 8 beta
- Architecture supports sub-500ms latency through edge processing
- MCP tools prevent LLM hallucinations through structured data access

## 🔗 Important Links

- Spec Documents: `.kiro/specs/courtroom-video-analyzer/`
- Stream Dashboard: https://beta.dashboard.getstream.io/
- Twelve Labs: https://twelvelabs.io/
- VideoDB: https://videodb.io/
- Deepgram: https://deepgram.com/
- TurboPuffer: https://turbopuffer.com/
- Gemini API: https://ai.google.dev/

---

**Last Updated**: Initial setup complete
**Next Action**: Obtain remaining API keys and install dependencies
