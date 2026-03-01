COURTROOM VIDEO ANALYZER AGENT
4-Member Team Plan with Detailed Tasks
Vision Possible: Agent Protocol Hackathon  •  48-Hour Sprint  •  Deadline: March 1, 2026

PROJECT OVERVIEW
This plan organizes the 4-member team for building the Courtroom Video Analyzer Agent — a real-time, multimodal AI system that enables attorneys to query live courtroom footage using natural language during active proceedings. The system achieves sub-500ms latency using Stream's edge network, Vision Agents SDK, Gemini Live, Twelve Labs Pegasus 1.2, VideoDB, TurboPuffer RAG, and MCP.

TEAM CONFIGURATION OVERVIEW
Member	Role Title	Primary Domain	Key Deliverables
M1	Frontend & Transport Engineer	React UI / Stream WebRTC	Stream call UI, HLS player, demo video
M2	Agent Orchestrator	Vision Agents / Gemini Live	processor.py, agent.py, README, echo demo
M3	Video Intelligence Engineer	Twelve Labs / VideoDB / RTStream	index.py, Pegasus indexing, GitHub repo
M4	Memory & Data Protocol Engineer	TurboPuffer / Deepgram / MCP	MCP server tools, RAG pipeline, tech blog

M1 — FRONTEND & TRANSPORT ENGINEER
Solely responsible for everything the judges and users SEE — the React client, WebRTC call room, live video canvas, and the final demo recording.
Day 1 Tasks (9:00 AM – 9:00 PM)
#	Task Description
1	TASK 1A (9:00–10:30 AM): Bootstrap React project with Vite. Install Stream Video React SDK and configure .env with Stream API keys. Verify package.json resolves without errors.
2	TASK 1B (10:30 AM–12:30 PM): Create a hardcoded mock WebRTC courtroom room using Stream's useCallStateHooks. Render a basic video tile to confirm A/V transport is working. Open browser Network tab and confirm media transport latency is sub-30ms.
3	TASK 1C (1:30–4:00 PM): Build the dual-canvas Evidentiary Player layout. Primary canvas = live stream feed. Secondary canvas = programmable HLS player (use hls.js) that accepts a URL via state props and instantly mounts/plays the clip.
4	TASK 1D (4:00–6:30 PM): Build the right-side chat panel. Implement text input + send button. Display messages exchanged with the agent. Style with dark-mode, high-contrast legal software aesthetic (deep navy background, white text, gold accents).
5	TASK 1E (6:30–9:00 PM): Add microphone icon with pulsing animation for voice mode. Wire onClick to Stream's microphone toggle. Display real-time transcript stream from Deepgram in a scrolling panel labeled by speaker (Judge, Witness 1, etc.).
Day 2 Tasks (9:00 AM – Deadline)
#	Task Description
1	TASK 2A (9:00–11:00 AM — Integration with M2): Execute the frontend-to-backend handshake. M1 fires a text query from the chat panel; confirm the Stream Edge routes it to the Gemini agent and that a JSON response containing an HLS URL is received back.
2	TASK 2B (11:00 AM–1:00 PM): Parse the structured JSON payload from the agent. On receiving an HLS URL, programmatically pass it to the secondary HLS player canvas and auto-play the clip. Show a loading spinner while the agent processes.
3	TASK 2C (2:00–5:00 PM — Parallel with stress test): Fix any UI bugs from the mock trial stress test. Ensure the diarized transcript panel scrolls smoothly without layout reflow. Confirm playback renders the exact requested timestamp with no buffering.
4	TASK 2D (5:00–7:00 PM): Finalize UI polish — professional dark-mode aesthetic, consistent typography, animated latency badge showing sub-500ms ping. Test responsiveness on 1080p screen.
5	TASK 2E (7:00 PM – Deadline): Record the 2-minute 1080p demo video following Section 6 script. Narrate the problem statement, show the live system in action, highlight the sub-500ms response. Upload to YouTube/Vimeo and embed in README.

M2 — AGENT ORCHESTRATOR
Responsible for the brain of the system — Vision Agents SDK, Gemini Live prompt engineering, the Python event loop, and all inter-module coordination.
Day 1 Tasks (9:00 AM – 9:00 PM)
#	Task Description
1	TASK 1A (9:00–10:30 AM): Install vision-agents SDK with: uv add "vision-agents[getstream, openai]". Authenticate all Stream API credentials. Verify imports are clean.
2	TASK 1B (10:30 AM–12:30 PM): Deploy baseline 'Echo' voice agent using gemini.Realtime() class. Confirm the bidirectional Stream Edge network connection works — agent joins the WebRTC room and echoes back audio. Log round-trip latency to terminal.
3	TASK 1C (1:30–4:30 PM): Implement the full processor.py module. Integrate the CourtroomProcessor class inheriting from VideoProcessor. Load yolov8n-face.pt for lightweight entity tracking at 5 FPS. Wire the Deepgram STT plugin (diarize=True).
4	TASK 1D (4:30–6:30 PM): Implement process_audio_chunk() — extract text + speaker_id from Deepgram response, map numeric speaker IDs to string labels (Speaker_0 → Judge, Speaker_1 → Witness, etc.), and return text/speaker tuples to the memory bus.
5	TASK 1E (6:30–9:00 PM): Implement process_frame() — run YOLO inference, extract entities_detected count, and return the state dictionary {timestamp, entities_visible, inferred_speaker}. Unit test that belief drift is prevented when speakers change.
Day 2 Tasks (9:00 AM – Deadline)
#	Task Description
1	TASK 2A (9:00–11:00 AM — Integration with M1): Lead the frontend-backend handshake. Ensure the Gemini agent receives queries from M1's UI, processes intent via MCP tools from M4, and returns structured JSON with both a spoken summary and HLS URL.
2	TASK 2B (11:00 AM–1:00 PM): Wire the agent orchestration in agent.py — call start_live_indexing() from M3's CourtroomIndexer, instantiate gemini.Realtime(fps=5), attach the CourtroomProcessor, and attach M4's MCP tool registrations.
3	TASK 2C (2:00–4:00 PM — Prompt Optimization): Refine the Gemini system prompt to enforce concise, factual responses. The agent must never hallucinate — it must ONLY use results returned by MCP tools. Add explicit instruction: 'If no MCP tool result is found, say so clearly.'
4	TASK 2D (4:00–6:00 PM): Run edge case tests — simultaneous speakers, overlapping objections, silence segments. Confirm diarization labels remain stable and YOLO entity count doesn't spike on camera movement.
5	TASK 2E (6:00 PM – Deadline): Author the comprehensive README.md. Include architecture diagram, install steps (uv/pip), required env vars, latency metrics with terminal screenshot evidence, and the Tech Stack Decision Matrix from the blueprint.

M3 — VIDEO INTELLIGENCE ENGINEER
Owns everything related to video content understanding — Twelve Labs Pegasus live indexing, VideoDB RTStream connections, HLS manifest retrieval, and the GitHub repository.
Day 1 Tasks (9:00 AM – 9:00 PM)
#	Task Description
1	TASK 1A (9:00–10:30 AM): Provision Twelve Labs Playground API keys and create a sandbox VideoDB account. Store keys in shared .env.example (values masked). Initialize the GitHub repository as public, set up .gitignore to exclude all .env and secret files — verify NO API keys appear in any commit.
2	TASK 1B (10:30 AM–12:30 PM): Install OBS Studio locally. Configure a virtual RTSP camera broadcasting a pre-recorded mock trial video in a continuous loop at rtsp://localhost:8554/courtcam. This is the mock stream for all Day 1 testing.
3	TASK 1C (1:30–4:30 PM): Implement index.py — establish the VideoDB connection using vdb = connect(api_key=...). Implement start_live_indexing() calling vdb.create_live_stream() on the mock RTSP URL.
4	TASK 1D (4:30–6:30 PM): Trigger Twelve Labs Pegasus 1.2 indexing via rt_stream.index_scenes() with the custom legal domain prompt: 'Monitor the courtroom proceedings. Identify the judge, witnesses, and counsel. Detail legal arguments, objections, and physical evidence presented.' Log the scene_index_id to confirm indexing is active.
5	TASK 1E (6:30–9:00 PM): Implement query_video_moments() — call vdb.search() with mode='semantic', parse the result payload into a list of {start_time, end_time, description, hls_url} dicts. Run 3 test queries against the mock trial video and verify the HLS URLs are valid and playable.
Day 2 Tasks (9:00 AM – Deadline)
#	Task Description
1	TASK 2A (9:00–11:00 AM — Sync with M4): Address the timestamp synchronization challenge with M4. The Vision Agent's local frame processor timecodes, Twelve Labs index timecodes, and TurboPuffer text timestamps must align precisely. Implement a shared epoch offset variable in a constants.py file. Apply linear drift-correction if clocks diverge over 20+ minutes.
2	TASK 2B (11:00 AM–1:00 PM): Run the 20-minute Mock Trial Stress Test — feed a complex mock trial (multiple overlapping speakers, physical evidence presentations, objections) into the RTSP stream. Verify Pegasus indexes all critical legal events correctly.
3	TASK 2C (2:00–4:00 PM): Iteratively optimize the Pegasus generative prompt based on stress test results. If queries return irrelevant clips, tighten the prompt with additional domain-specific keywords (e.g., 'Miranda rights', 'physical exhibit', 'cross-examination').
4	TASK 2D (4:00–6:00 PM): Polish and finalize the GitHub repository. Verify commit history shows clear parallel activity from all 4 member accounts across the 48 hours. Confirm all 4 members have made meaningful commits — judges check this. Write descriptive commit messages.
5	TASK 2E (6:00 PM – Deadline): Verify .gitignore is airtight. Do a final security scan using git log --all --full-history -- '*.env' to confirm zero API keys in history. Tag the final release commit as v1.0.0-hackathon.

M4 — MEMORY & DATA PROTOCOL ENGINEER
Owns the intelligence plumbing — TurboPuffer RAG database, Deepgram diarization integration, the MCP server tool definitions, and the $500 bonus technical blog post.
Day 1 Tasks (9:00 AM – 9:00 PM)
#	Task Description
1	TASK 1A (9:00–10:30 AM): Initialize the remote TurboPuffer database namespace (court-session-{session_id}). Configure the turbopuffer.TurboPufferRAG plugin with chunk_size=1000 and chunk_overlap=100 as specified in the architecture.
2	TASK 1B (10:30 AM–12:30 PM): Write the base data ingestion script — parse incoming diarized text strings into the format '[{timestamp}] {speaker}: {text}' and ingest via memory_rag.add_documents(). Test with 10 synthetic court dialogue samples. Verify documents appear in TurboPuffer namespace.
3	TASK 1C (1:30–4:00 PM): Implement query_transcript() using memory_rag.search(query, top_k=5, mode='hybrid') to leverage both BM25 keyword matching (critical for exact legal statute names) and vector semantic search via Gemini embeddings. Test with 5 diverse transcript queries.
4	TASK 1D (4:00–6:30 PM): Build the MCP server architecture. Implement the @llm.register_function decorator wrappers for both search_video (routes to M3's query_video_moments) and search_transcript (routes to TurboPuffer). Write clear natural-language descriptions for each tool — these descriptions are what Gemini uses to select the right tool.
5	TASK 1E (6:30–9:00 PM): Test MCP tools in complete isolation. Simulate Gemini intent formulation by manually calling each tool with 10 diverse legal queries. Verify the search_video tool correctly routes visual/spatial queries and search_transcript handles exact quote lookups. Document any query type ambiguities for M2's prompt engineering.
Day 2 Tasks (9:00 AM – Deadline)
#	Task Description
1	TASK 2A (9:00–11:00 AM — Sync with M3): Collaborate on timestamp synchronization. Ensure each add_transcript_chunk() call uses the same epoch as the Twelve Labs timecodes. Verify that if a user queries 'what was said at 4:15 PM', both the TurboPuffer text result AND the VideoDB video clip return the same moment.
2	TASK 2B (11:00 AM–1:00 PM): Participate in Mock Trial Stress Test. Monitor TurboPuffer ingestion rate during the 20-minute feed. Confirm all 1000-character chunks are indexed with correct speaker labels. Check for any chunk boundary errors that split sentences mid-clause.
3	TASK 2C (2:00–4:00 PM): Tune Reciprocal Rank Fusion weighting between BM25 and vector components. For legal proceedings, exact statute/name recall (BM25) is often more important than semantic similarity. Run A/B comparison of 5 test queries with different alpha weights and document findings.
4	TASK 2D (4:00–6:00 PM): Write and publish the technical blog post on Dev.to/Medium/Hashnode titled: 'Building a Real-Time Multimodal Legal Agent with Vision Agents SDK and the Model Context Protocol.' Cover: belief drift problem, MCP as contextual immune system, Pegasus RTStream integration, hybrid RAG for legal precision. Minimum 1,000 words.
5	TASK 2E (6:00 PM – Deadline): Complete and submit all Hackathon forms. Verify registration at forms.gle/b8YS4J4jcR2mSnnf7 and final submission at forms.gle/oG7hWZ1tgbSwbcie8. Confirm all 4 team member emails and GitHub handles are correctly listed on the submission form for equal prize distribution.

CRITICAL INTEGRATION CHECKPOINTS
Checkpoint	Time	Owner(s)	Success Criteria	Fallback
Echo Agent Live	Day 1, 12:30 PM	M2	Voice echoes within 500ms in Stream room	Use text-only fallback
RTStream Active	Day 1, 5:00 PM	M3	Twelve Labs logs scene_index_id	Use pre-uploaded test video
MCP Tools Fire	Day 1, 9:00 PM	M4	Both tools return valid results in isolation	Hard-code mock response for demo
UI ↔️ Agent Handshake	Day 2, 11:00 AM	M1 + M2	Query in UI → HLS plays in secondary player	Direct API call bypassing Stream
Timestamp Sync	Day 2, 1:00 PM	M3 + M4	Video clip matches transcript moment exactly	Accept ±2s tolerance for demo
Full Stress Test Pass	Day 2, 4:00 PM	All Members	20-min trial queryable with <500ms latency	Use 5-min clip for demo

SUBMISSION ARTIFACTS CHECKLIST
✓	Artifact	Owner	Deadline
☐	GitHub repo (public, new, all 4 members committed)	M3	Day 2, 6 PM
☐	.gitignore active — ZERO API keys in any commit	M3	Day 2, 6 PM
☐	2-3 min demo video (1080p, YouTube/Vimeo)	M1	Day 2, 7 PM
☐	README.md with arch diagram, setup guide, latency metrics	M2	Day 2, 7 PM
☐	Technical blog post published (Dev.to / Medium)	M4	Day 2, 6 PM
☐	Registration form submitted: forms.gle/b8YS4J4jcR2mSnnf7	M4	Pre-hackathon
☐	Final submission form: forms.gle/oG7hWZ1tgbSwbcie8 (all 4 GitHub handles)	M4	March 1, 2026

Build fast. Commit often. Ship by March 1, 2026.