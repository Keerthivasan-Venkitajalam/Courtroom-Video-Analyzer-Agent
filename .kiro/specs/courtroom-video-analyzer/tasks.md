# Implementation Tasks: Courtroom Video Analyzer Agent

## Overview

This document outlines the implementation tasks for building the Courtroom Video Analyzer Agent - a real-time multimodal AI system for querying live courtroom proceedings with sub-500ms latency. The project follows a 48-hour hackathon timeline with a 4-member team structure.

## Team Structure

- **M1 (Frontend & Transport Engineer)**: React UI, Stream WebRTC, HLS player, demo video
- **M2 (Agent Orchestrator)**: Vision Agents SDK, Gemini Live, Python event loop, processor.py, agent.py
- **M3 (Video Intelligence Engineer)**: Twelve Labs Pegasus, VideoDB RTStream, index.py, GitHub repo
- **M4 (Memory & Data Protocol Engineer)**: TurboPuffer RAG, Deepgram integration, MCP server, technical blog

## Task List

### Phase 1: Infrastructure Setup & Core Components (Day 1: 9:00 AM - 1:00 PM)

#### 1. M1: Frontend Project Bootstrap
- [x] 1.1 Initialize React project with Vite
  - Install Stream Video React SDK
  - Configure .env with Stream API keys
  - Verify package.json resolves without errors
  - **Validates**: Property 47 (Query result display completeness)
  - **Time**: 9:00-10:30 AM

- [x] 1.2 Create mock WebRTC courtroom room
  - Use Stream's useCallStateHooks
  - Render basic video tile
  - Confirm A/V transport working
  - Verify media transport latency is sub-30ms in Network tab
  - **Validates**: Property 1 (Frame continuity), Property 4 (Microsecond timestamp precision)
  - **Time**: 10:30 AM-12:30 PM

#### 2. M2: Vision Agents SDK Setup
- [x] 2.1 Install and configure Vision Agents SDK
  - Run: `uv add "vision-agents[getstream, openai]"`
  - Authenticate all Stream API credentials
  - Verify imports are clean
  - **Validates**: Property 37 (Unified clock reference)
  - **Time**: 9:00-10:30 AM

- [x] 2.2 Deploy baseline Echo voice agent
  - Use gemini.Realtime() class
  - Confirm bidirectional Stream Edge network connection
  - Agent joins WebRTC room and echoes back audio
  - Log round-trip latency to terminal
  - **Validates**: Property 2 (End-to-end query latency)
  - **Checkpoint**: Echo Agent Live (Day 1, 12:30 PM)
  - **Time**: 10:30 AM-12:30 PM

#### 3. M3: Video Intelligence Infrastructure
- [x] 3.1 Provision API keys and initialize repository
  - Provision Twelve Labs Playground API keys
  - Create sandbox VideoDB account
  - Store keys in .env.example (values masked)
  - Initialize public GitHub repository
  - Set up .gitignore to exclude all .env and secret files
  - Verify NO API keys appear in any commit
  - **Validates**: Property 46 (API version backward compatibility)
  - **Time**: 9:00-10:30 AM

- [x] 3.2 Set up mock RTSP stream
  - Install OBS Studio locally
  - Configure virtual RTSP camera at rtsp://localhost:8554/courtcam
  - Broadcast pre-recorded mock trial video in continuous loop
  - **Validates**: Property 5 (Resolution support range)
  - **Time**: 10:30 AM-12:30 PM

#### 4. M4: TurboPuffer RAG Setup
- [x] 4.1 Initialize TurboPuffer database
  - Initialize remote TurboPuffer namespace (court-session-{session_id})
  - Configure turbopuffer.TurboPufferRAG plugin
  - Set chunk_size=1000 and chunk_overlap=100
  - **Validates**: Property 25 (Dual index representation)
  - **Time**: 9:00-10:30 AM

- [x] 4.2 Implement base data ingestion script
  - Parse incoming diarized text strings
  - Format as '[{timestamp}] {speaker}: {text}'
  - Ingest via memory_rag.add_documents()
  - Test with 10 synthetic court dialogue samples
  - Verify documents appear in TurboPuffer namespace
  - **Validates**: Property 18 (Transcript storage latency)
  - **Time**: 10:30 AM-12:30 PM

### Phase 2: Core Pipeline Construction (Day 1: 1:30 PM - 9:00 PM)

#### 5. M1: Evidentiary Player UI
- [x] 5.1 Build dual-canvas layout
  - Primary canvas = live stream feed
  - Secondary canvas = programmable HLS player (use hls.js)
  - HLS player accepts URL via state props
  - Instantly mounts and plays clips
  - **Validates**: Property 30 (HLS manifest generation), Property 36 (Playback start latency)
  - **Time**: 1:30-4:00 PM

- [x] 5.2 Build chat panel interface
  - Right-side chat panel
  - Text input + send button
  - Display messages exchanged with agent
  - Style with dark-mode, high-contrast legal aesthetic
  - Deep navy background, white text, gold accents
  - **Validates**: Property 47 (Query result display completeness)
  - **Time**: 4:00-6:30 PM

- [x] 5.3 Add voice mode and real-time transcript display
  - Microphone icon with pulsing animation
  - Wire onClick to Stream's microphone toggle
  - Display real-time transcript stream from Deepgram
  - Scrolling panel labeled by speaker (Judge, Witness 1, etc.)
  - **Validates**: Property 48 (Real-time transcript display), Property 51 (Keyboard shortcut support)
  - **Time**: 6:30-9:00 PM

#### 6. M2: Courtroom Processor Implementation
- [x] 6.1 Implement processor.py module
  - Integrate CourtroomProcessor class inheriting from VideoProcessor
  - Load yolov8n-face.pt for lightweight entity tracking at 5 FPS
  - Wire Deepgram STT plugin (diarize=True)
  - **Validates**: Property 6 (Entity detection), Property 12 (Speaker diarization)
  - **Time**: 1:30-4:30 PM

- [x] 6.2 Implement process_audio_chunk()
  - Extract text + speaker_id from Deepgram response
  - Map numeric speaker IDs to string labels
  - Speaker_0 → Judge, Speaker_1 → Witness, etc.
  - Return text/speaker tuples to memory bus
  - **Validates**: Property 13 (Speaker role labeling), Property 16 (Speaker identification latency)
  - **Time**: 4:30-6:30 PM

- [x] 6.3 Implement process_frame()
  - Run YOLO inference
  - Extract entities_detected count
  - Return state dictionary {timestamp, entities_visible, inferred_speaker}
  - Unit test that belief drift is prevented when speakers change
  - **Validates**: Property 9 (Temporal consistency), Property 53 (Belief drift incident logging)
  - **Time**: 6:30-9:00 PM

#### 7. M3: VideoDB and Twelve Labs Integration
- [x] 7.1 Implement index.py - VideoDB connection
  - Establish VideoDB connection using vdb = connect(api_key=...)
  - Implement start_live_indexing()
  - Call vdb.create_live_stream() on mock RTSP URL
  - **Validates**: Property 1 (Frame continuity), Property 8 (Frame-level indexing precision)
  - **Time**: 1:30-4:30 PM

- [x] 7.2 Trigger Twelve Labs Pegasus 1.2 indexing
  - Call rt_stream.index_scenes()
  - Use custom legal domain prompt: 'Monitor the courtroom proceedings. Identify the judge, witnesses, and counsel. Detail legal arguments, objections, and physical evidence presented.'
  - Log scene_index_id to confirm indexing is active
  - **Validates**: Property 6 (Entity detection), Property 7 (Visual event recognition)
  - **Checkpoint**: RTStream Active (Day 1, 5:00 PM)
  - **Time**: 4:30-6:30 PM

- [x] 7.3 Implement query_video_moments()
  - Call vdb.search() with mode='semantic'
  - Parse result payload into list of {start_time, end_time, description, hls_url} dicts
  - Run 3 test queries against mock trial video
  - Verify HLS URLs are valid and playable
  - **Validates**: Property 11 (Multimodal query support), Property 30 (HLS manifest generation)
  - **Time**: 6:30-9:00 PM

#### 8. M4: Hybrid Search and MCP Server
- [x] 8.1 Implement query_transcript()
  - Use memory_rag.search(query, top_k=5, mode='hybrid')
  - Leverage both BM25 keyword matching and vector semantic search
  - Test with 5 diverse transcript queries
  - **Validates**: Property 24 (Hybrid search execution), Property 26 (Legal terminology prioritization)
  - **Time**: 1:30-4:00 PM

- [x] 8.2 Build MCP server architecture
  - Implement @llm.register_function decorator wrappers
  - search_video (routes to M3's query_video_moments)
  - search_transcript (routes to TurboPuffer)
  - Write clear natural-language descriptions for each tool
  - **Validates**: Property 43 (Tool invocation validation), Property 44 (Tool execution sandboxing)
  - **Time**: 4:00-6:30 PM

- [x] 8.3 Test MCP tools in isolation
  - Simulate Gemini intent formulation
  - Manually call each tool with 10 diverse legal queries
  - Verify search_video routes visual/spatial queries correctly
  - Verify search_transcript handles exact quote lookups
  - Document query type ambiguities for M2's prompt engineering
  - **Validates**: Property 45 (Tool discovery)
  - **Checkpoint**: MCP Tools Fire (Day 1, 9:00 PM)
  - **Time**: 6:30-9:00 PM

### Phase 3: Integration & Synchronization (Day 2: 9:00 AM - 2:00 PM)

#### 9. M1 & M2: Frontend-Backend Handshake
- [x] 9.1 Execute frontend-to-backend integration (M1 + M2)
  - M1 fires text query from chat panel
  - Confirm Stream Edge routes to Gemini agent
  - Verify JSON response containing HLS URL is received
  - **Validates**: Property 2 (End-to-end query latency), Property 40 (Query routing)
  - **Checkpoint**: UI ↔️ Agent Handshake (Day 2, 11:00 AM)
  - **Time**: 9:00-11:00 AM

- [x] 9.2 Parse and display query results (M1)
  - Parse structured JSON payload from agent
  - On receiving HLS URL, pass to secondary HLS player canvas
  - Auto-play the clip
  - Show loading spinner while agent processes
  - **Validates**: Property 47 (Query result display completeness), Property 49 (Query match highlighting)
  - **Time**: 11:00 AM-1:00 PM

#### 10. M2: Agent Orchestration Wiring
- [x] 10.1 Wire agent orchestration in agent.py
  - Call start_live_indexing() from M3's CourtroomIndexer
  - Instantiate gemini.Realtime(fps=5)
  - Attach CourtroomProcessor
  - Attach M4's MCP tool registrations
  - **Validates**: Property 40 (Query routing), Property 41 (Result aggregation)
  - **Time**: 9:00-11:00 AM

- [x] 10.2 Implement Gemini system prompt
  - Refine prompt to enforce concise, factual responses
  - Agent must ONLY use results returned by MCP tools
  - Add explicit instruction: 'If no MCP tool result is found, say so clearly'
  - Prevent hallucinations
  - **Validates**: Property 23 (Conversation context maintenance)
  - **Time**: 11:00 AM-1:00 PM

#### 11. M3 & M4: Timestamp Synchronization
- [x] 11.1 Address timestamp synchronization (M3 + M4)
  - Vision Agent's local frame processor timecodes
  - Twelve Labs index timecodes
  - TurboPuffer text timestamps must align precisely
  - Implement shared epoch offset variable in constants.py
  - Apply linear drift-correction if clocks diverge over 20+ minutes
  - **Validates**: Property 15 (Video-transcript timestamp synchronization), Property 38 (Periodic timestamp validation)
  - **Checkpoint**: Timestamp Sync (Day 2, 1:00 PM)
  - **Time**: 9:00-11:00 AM

- [x] 11.2 Verify timestamp alignment (M4)
  - Ensure each add_transcript_chunk() uses same epoch as Twelve Labs
  - Test: if user queries 'what was said at 4:15 PM'
  - Both TurboPuffer text result AND VideoDB video clip return same moment
  - **Validates**: Property 10 (Visual-transcript correlation accuracy)
  - **Time**: 11:00 AM-1:00 PM

### Phase 4: Testing & Optimization (Day 2: 2:00 PM - 6:00 PM)

#### 12. All Members: Mock Trial Stress Test
- [x] 12.1 Run 20-minute Mock Trial Stress Test (All)
  - Feed complex mock trial into RTSP stream
  - Multiple overlapping speakers
  - Physical evidence presentations
  - Objections
  - Verify Pegasus indexes all critical legal events
  - **Validates**: Property 3 (95th percentile latency under load), Property 56 (Concurrent session support)
  - **Checkpoint**: Full Stress Test Pass (Day 2, 4:00 PM)
  - **Time**: 2:00-4:00 PM

- [x] 12.2 Fix UI bugs from stress test (M1)
  - Ensure diarized transcript panel scrolls smoothly
  - No layout reflow
  - Confirm playback renders exact requested timestamp
  - No buffering
  - **Validates**: Property 48 (Real-time transcript display)
  - **Time**: 2:00-5:00 PM

#### 13. M2: Edge Case Testing
- [x] 13.1 Run edge case tests
  - Simultaneous speakers
  - Overlapping objections
  - Silence segments
  - Confirm diarization labels remain stable
  - YOLO entity count doesn't spike on camera movement
  - **Validates**: Property 17 (Overlapping speech attribution), Property 52 (Motion detection)
  - **Time**: 2:00-4:00 PM

#### 14. M3: Pegasus Prompt Optimization
- [x] 14.1 Iteratively optimize Pegasus prompt
  - Based on stress test results
  - If queries return irrelevant clips, tighten prompt
  - Add domain-specific keywords (Miranda rights, physical exhibit, cross-examination)
  - **Validates**: Property 7 (Visual event recognition), Property 27 (Semantic search for conceptual queries)
  - **Time**: 2:00-4:00 PM

#### 15. M4: Hybrid Search Tuning
- [x] 15.1 Tune Reciprocal Rank Fusion weighting
  - Balance BM25 and vector components
  - For legal proceedings, exact statute/name recall (BM25) often more important
  - Run A/B comparison of 5 test queries with different alpha weights
  - Document findings
  - **Validates**: Property 26 (Legal terminology prioritization), Property 28 (Search result completeness)
  - **Time**: 2:00-4:00 PM

### Phase 5: Finalization & Submission (Day 2: 4:00 PM - Deadline)

#### 16. M1: Demo Video Production
- [x] 16.1 Finalize UI polish
  - Professional dark-mode aesthetic
  - Consistent typography
  - Animated latency badge showing sub-500ms ping
  - Test responsiveness on 1080p screen
  - **Validates**: Property 47 (Query result display completeness)
  - **Time**: 5:00-7:00 PM

- [x] 16.2 Record 2-minute demo video
  - 1080p resolution
  - Follow Section 6 script from blueprint
  - Narrate problem statement
  - Show live system in action
  - Highlight sub-500ms response
  - Upload to YouTube/Vimeo
  - Embed in README
  - **Validates**: All properties (comprehensive demo)
  - **Time**: 7:00 PM - Deadline

#### 17. M2: Documentation
- [x] 17.1 Author comprehensive README.md
  - Include architecture diagram
  - Install steps (uv/pip)
  - Required env vars
  - Latency metrics with terminal screenshot evidence
  - Tech Stack Decision Matrix from blueprint
  - **Validates**: Property 42 (Comprehensive logging)
  - **Time**: 6:00 PM - Deadline

#### 18. M3: Repository Finalization
- [x] 18.1 Polish and finalize GitHub repository
  - Verify commit history shows parallel activity from all 4 members
  - Confirm all 4 members have meaningful commits
  - Write descriptive commit messages
  - **Validates**: Property 46 (API version backward compatibility)
  - **Time**: 4:00-6:00 PM

- [x] 18.2 Security scan and tagging
  - Verify .gitignore is airtight
  - Run: `git log --all --full-history -- '*.env'`
  - Confirm zero API keys in history
  - Tag final release commit as v1.0.0-hackathon
  - **Validates**: Property 44 (Tool execution sandboxing)
  - **Time**: 6:00 PM - Deadline

#### 19. M4: Technical Blog and Submission
- [x] 19.1 Write and publish technical blog post
  - Platform: Dev.to/Medium/Hashnode
  - Title: 'Building a Real-Time Multimodal Legal Agent with Vision Agents SDK and the Model Context Protocol'
  - Cover: belief drift problem, MCP as contextual immune system, Pegasus RTStream integration, hybrid RAG for legal precision
  - Minimum 1,000 words
  - **Validates**: Property 42 (Comprehensive logging)
  - **Time**: 4:00-6:00 PM

- [x] 19.2 Complete hackathon submissions
  - Verify registration at forms.gle/b8YS4J4jcR2mSnnf7
  - Complete final submission at forms.gle/oG7hWZ1tgbSwbcie8
  - Confirm all 4 team member emails and GitHub handles listed
  - **Validates**: All properties (project completion)
  - **Time**: 6:00 PM - Deadline

## Critical Integration Checkpoints

| Checkpoint | Time | Owner(s) | Success Criteria | Fallback |
|------------|------|----------|------------------|----------|
| Echo Agent Live | Day 1, 12:30 PM | M2 | Voice echoes within 500ms in Stream room | Use text-only fallback |
| RTStream Active | Day 1, 5:00 PM | M3 | Twelve Labs logs scene_index_id | Use pre-uploaded test video |
| MCP Tools Fire | Day 1, 9:00 PM | M4 | Both tools return valid results in isolation | Hard-code mock response for demo |
| UI ↔️ Agent Handshake | Day 2, 11:00 AM | M1 + M2 | Query in UI → HLS plays in secondary player | Direct API call bypassing Stream |
| Timestamp Sync | Day 2, 1:00 PM | M3 + M4 | Video clip matches transcript moment exactly | Accept ±2s tolerance for demo |
| Full Stress Test Pass | Day 2, 4:00 PM | All Members | 20-min trial queryable with <500ms latency | Use 5-min clip for demo |

## Submission Artifacts Checklist

| Artifact | Owner | Deadline | Status |
|----------|-------|----------|--------|
| GitHub repo (public, new, all 4 members committed) | M3 | Day 2, 6 PM | ☐ |
| .gitignore active — ZERO API keys in any commit | M3 | Day 2, 6 PM | ☐ |
| 2-3 min demo video (1080p, YouTube/Vimeo) | M1 | Day 2, 7 PM | ☐ |
| README.md with arch diagram, setup guide, latency metrics | M2 | Day 2, 7 PM | ☐ |
| Technical blog post published (Dev.to / Medium) | M4 | Day 2, 6 PM | ☐ |
| Registration form submitted | M4 | Pre-hackathon | ☐ |
| Final submission form (all 4 GitHub handles) | M4 | March 1, 2026 | ☐ |

## Property Validation Matrix

Each task validates specific correctness properties from the design document. The 61 properties cover:

- **Latency**: Properties 2, 3, 16, 18, 36 (sub-500ms end-to-end, component-level, storage)
- **Multimodal Understanding**: Properties 6, 7, 9, 10, 11 (entity detection, visual events, temporal consistency, correlation)
- **Search Precision**: Properties 24, 25, 26, 27, 28 (hybrid search, dual indexing, legal terminology, semantic search)
- **Timestamp Sync**: Properties 4, 8, 15, 37, 38 (microsecond precision, frame-level, video-transcript sync, unified clock)
- **Speaker Diarization**: Properties 12, 13, 16, 17 (identification, role labeling, latency, overlapping speech)
- **Query Processing**: Properties 19, 20, 21, 22, 23 (temporal, speaker, content interpretation, decomposition, context)
- **Playback**: Properties 30, 31, 32, 33, 34, 35, 36 (HLS generation, duration range, context, accuracy, concurrent, navigation)
- **Security**: Properties 43, 44, 45, 46 (validation, sandboxing, discovery, backward compatibility)
- **Fault Tolerance**: Properties 40, 41, 42 (routing, aggregation, logging)
- **Scalability**: Properties 56, 57, 58, 59, 60, 61 (concurrent sessions, latency under load, isolation, performance)

## Notes

- All tasks follow the 48-hour hackathon timeline
- Team members work in parallel with defined integration checkpoints
- Each task references specific correctness properties it validates
- Fallback strategies are defined for critical checkpoints
- The project emphasizes sub-500ms latency as the primary success metric
