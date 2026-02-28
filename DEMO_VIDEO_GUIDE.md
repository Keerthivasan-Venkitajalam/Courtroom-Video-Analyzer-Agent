# Demo Video Production Guide

## Overview

This guide provides a comprehensive script and instructions for recording the 2-minute demo video for the Courtroom Video Analyzer Agent. The video should demonstrate the system's key capabilities, particularly the sub-500ms query latency and multimodal understanding.

## Video Specifications

- **Duration**: 2-3 minutes (target: 2 minutes)
- **Resolution**: 1080p (1920x1080) minimum
- **Format**: MP4 (H.264 codec recommended)
- **Frame Rate**: 30fps
- **Audio**: Clear narration with system audio
- **Platform**: YouTube or Vimeo (unlisted or public)

## Recording Setup

### Screen Recording Tools

**Recommended Options**:
- **OBS Studio** (Free, cross-platform): https://obsproject.com/
- **Loom** (Easy, web-based): https://loom.com/
- **QuickTime** (Mac): Built-in screen recording
- **Windows Game Bar** (Windows): Win + G

### OBS Studio Configuration (Recommended)

1. **Video Settings**:
   - Base Resolution: 1920x1080
   - Output Resolution: 1920x1080
   - FPS: 30

2. **Audio Settings**:
   - Desktop Audio: Enabled (for system sounds)
   - Microphone: Enabled (for narration)
   - Audio Bitrate: 160 kbps

3. **Output Settings**:
   - Recording Format: MP4
   - Encoder: x264
   - Rate Control: CBR
   - Bitrate: 6000 Kbps

### Pre-Recording Checklist

- [ ] Close unnecessary applications and browser tabs
- [ ] Disable notifications (Do Not Disturb mode)
- [ ] Test microphone audio levels
- [ ] Ensure system is running smoothly (no lag)
- [ ] Have mock trial video ready in RTSP stream
- [ ] Backend agent running (`python agent.py`)
- [ ] Frontend running (`npm run dev` in frontend/)
- [ ] Browser window at 1080p resolution
- [ ] Prepare test queries in advance

## Demo Script

### Section 1: Introduction (0:00 - 0:20)

**Visual**: Title slide or system overview

**Narration**:
> "Introducing the Courtroom Video Analyzer Agent - a real-time multimodal AI system that enables attorneys to query live courtroom proceedings using natural language with sub-500 millisecond latency.
>
> During active trials, attorneys need instant access to specific moments - what the witness said, when evidence was presented, or who made an objection. Traditional methods require manual review of hours of footage. Our system solves this problem."

**On-Screen Text**:
- "Courtroom Video Analyzer Agent"
- "Sub-500ms Query Latency"
- "Multimodal AI for Legal Proceedings"

---

### Section 2: System Architecture (0:20 - 0:35)

**Visual**: Show architecture diagram or system overview

**Narration**:
> "The system combines cutting-edge technologies: WebRTC for video ingestion, Twelve Labs Pegasus for video understanding, Deepgram for real-time transcription with speaker diarization, TurboPuffer for hybrid search, and Gemini Live API for natural language processing - all orchestrated through the Vision Agents SDK."

**On-Screen Text**:
- "WebRTC Video Ingestion"
- "Twelve Labs Pegasus 1.2"
- "Deepgram STT + Diarization"
- "TurboPuffer Hybrid Search"
- "Gemini Live API"

---

### Section 3: Live System Demo - Real-Time Transcription (0:35 - 0:50)

**Visual**: Show the frontend interface with live courtroom stream playing

**Narration**:
> "Here's the system in action. On the left, we have the live courtroom stream. On the right, real-time transcription with automatic speaker identification - the judge, witness, and attorneys are all labeled automatically."

**Actions**:
- Point to live video feed
- Point to transcript panel showing speaker labels
- Show transcript updating in real-time

**On-Screen Highlight**:
- Circle or arrow pointing to speaker labels (Judge, Witness, Prosecution, Defense)
- Highlight transcript text appearing in real-time

---

### Section 4: Natural Language Query - Text Mode (0:50 - 1:10)

**Visual**: Focus on chat interface

**Narration**:
> "Now, let's query the proceedings. I'll ask: 'What did the witness say about the contract?' Watch the latency indicator."

**Actions**:
1. Type query in chat: "What did the witness say about the contract?"
2. Click send
3. **Show latency badge displaying sub-500ms response time**
4. Results appear with transcript excerpt and video clip

**On-Screen Highlight**:
- **Latency badge showing: "Response: 387ms" or similar**
- Highlight matching transcript text
- Show video clip thumbnail

**Narration (continued)**:
> "In under 400 milliseconds, the system returns the exact moment with a timestamped video clip and transcript excerpt."

---

### Section 5: Video Clip Playback (1:10 - 1:25)

**Visual**: Click on video clip to play in secondary player

**Narration**:
> "Clicking the result instantly plays the video clip with 5 seconds of context before and after the matching moment. The system uses HLS manifests for instant playback with frame-accurate timestamps."

**Actions**:
- Click video clip result
- Show video playing in secondary player
- Highlight timestamp display
- Show smooth playback without buffering

**On-Screen Highlight**:
- Timestamp indicator on video player
- "HLS Instant Playback" label

---

### Section 6: Multimodal Query - Visual + Audio (1:25 - 1:45)

**Visual**: Return to chat interface

**Narration**:
> "The system understands multimodal queries. Let me ask: 'When was physical evidence presented to the judge?' This requires understanding both visual elements and speaker context."

**Actions**:
1. Type query: "When was physical evidence presented to the judge?"
2. Send query
3. **Show latency badge again: sub-500ms**
4. Results show moment when evidence was shown

**On-Screen Highlight**:
- **Latency badge: "Response: 412ms"**
- Video thumbnail showing evidence presentation
- Transcript showing relevant dialogue

**Narration (continued)**:
> "Again, sub-500 millisecond response. The system identified the visual event of evidence presentation and correlated it with the transcript."

---

### Section 7: Voice Mode Demo (1:45 - 2:00)

**Visual**: Click microphone icon to enable voice mode

**Narration**:
> "For hands-free operation during trials, attorneys can use voice mode powered by Gemini Live API."

**Actions**:
1. Click microphone icon (show pulsing animation)
2. Speak query: "Show me all objections from the defense attorney"
3. **Show latency badge: sub-500ms**
4. Results appear with multiple clips

**On-Screen Highlight**:
- Microphone icon with pulsing animation
- **Latency badge: "Response: 445ms"**
- Multiple result cards displayed

---

### Section 8: Key Features Summary (2:00 - 2:15)

**Visual**: Split screen or quick montage of features

**Narration**:
> "Key features: Sub-500 millisecond latency for real-time courtroom use. Hybrid search combining exact legal terminology with semantic understanding. Automatic speaker diarization and role labeling. And instant HLS video playback with frame-accurate timestamps."

**On-Screen Text** (bullet points appearing):
- ⚡ Sub-500ms Query Latency
- 🔍 Hybrid BM25 + Vector Search
- 🎤 Automatic Speaker Diarization
- 📹 Instant HLS Video Playback
- 🎯 Frame-Accurate Timestamps
- 🛡️ Belief Drift Prevention

---

### Section 9: Technology Stack & Closing (2:15 - 2:30)

**Visual**: Technology logos or architecture diagram

**Narration**:
> "Built with Stream's WebRTC infrastructure, Twelve Labs Pegasus for video intelligence, VideoDB for real-time indexing, Deepgram for transcription, TurboPuffer for hybrid search, and orchestrated through Vision Agents SDK with Model Context Protocol for secure tool integration.
>
> The Courtroom Video Analyzer Agent - transforming how attorneys access information during live proceedings."

**On-Screen Text**:
- GitHub repository URL
- "Built for WeMakeDevs + Stream Hackathon"
- "MIT License"

---

## Recording Tips

### Before Recording

1. **Practice the script** 2-3 times to ensure smooth delivery
2. **Prepare test queries** in advance (copy-paste ready)
3. **Test the system** to ensure all features work
4. **Clear browser cache** for optimal performance
5. **Use a good microphone** for clear narration

### During Recording

1. **Speak clearly and at a moderate pace**
2. **Pause briefly between sections** (easier to edit)
3. **Show the latency badge prominently** - this is a key feature
4. **Keep cursor movements smooth** and deliberate
5. **If you make a mistake**, pause and restart that section

### After Recording

1. **Review the video** for audio/video quality
2. **Check that latency numbers are visible**
3. **Verify all key features are demonstrated**
4. **Trim any dead air** at beginning/end
5. **Add captions** if possible (improves accessibility)

## Video Editing (Optional)

### Basic Editing Tools

- **DaVinci Resolve** (Free, professional): https://www.blackmagicdesign.com/products/davinciresolve
- **iMovie** (Mac, free)
- **Windows Video Editor** (Windows, built-in)
- **Shotcut** (Free, cross-platform): https://shotcut.org/

### Editing Checklist

- [ ] Trim beginning/end for clean start/finish
- [ ] Add title card with project name
- [ ] Add on-screen text annotations for key features
- [ ] Highlight latency badge with circle/arrow overlay
- [ ] Add background music (optional, keep volume low)
- [ ] Add closing card with GitHub URL
- [ ] Export at 1080p, 30fps, MP4 format

## Upload Instructions

### YouTube Upload

1. Go to https://studio.youtube.com/
2. Click "Create" → "Upload videos"
3. Select your video file
4. **Title**: "Courtroom Video Analyzer Agent - Real-Time Multimodal AI for Legal Proceedings"
5. **Description**:
```
A real-time multimodal AI system that enables attorneys to query live courtroom proceedings using natural language with sub-500ms latency.

🔗 GitHub: [Your Repository URL]
🏆 Built for WeMakeDevs + Stream Hackathon

Key Features:
⚡ Sub-500ms query latency
🎥 Multimodal video understanding
🔍 Hybrid BM25 + vector search
🎤 Automatic speaker diarization
📹 Instant HLS video playback

Tech Stack:
- Stream WebRTC & Video SDK
- Twelve Labs Pegasus 1.2
- VideoDB Real-Time Indexing
- Deepgram STT + Diarization
- TurboPuffer Hybrid Search
- Gemini Live API
- Vision Agents SDK
- Model Context Protocol (MCP)

#AI #LegalTech #VideoAnalysis #RealtimeAI #Hackathon
```
6. **Visibility**: Unlisted or Public
7. **Thumbnail**: Create custom thumbnail with project name and key feature
8. Click "Publish"

### Vimeo Upload

1. Go to https://vimeo.com/upload
2. Upload your video file
3. **Title**: "Courtroom Video Analyzer Agent - Real-Time Multimodal AI"
4. **Description**: (Same as YouTube description above)
5. **Privacy**: Anyone or Public
6. Click "Save"

## Embedding in README

After uploading, add to the top of your README.md:

### YouTube Embed

```markdown
## 🎥 Demo Video

[![Courtroom Video Analyzer Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

*Click to watch the 2-minute demo showcasing sub-500ms query latency and multimodal understanding*
```

### Vimeo Embed

```markdown
## 🎥 Demo Video

[![Courtroom Video Analyzer Demo](https://i.vimeocdn.com/video/YOUR_VIDEO_ID_1920x1080.jpg)](https://vimeo.com/YOUR_VIDEO_ID)

*Click to watch the 2-minute demo showcasing sub-500ms query latency and multimodal understanding*
```

## Test Queries for Demo

Use these pre-tested queries during recording:

### Text Queries
1. "What did the witness say about the contract?"
2. "When was physical evidence presented to the judge?"
3. "Show me all objections from the defense attorney"
4. "Find mentions of fraud"
5. "What happened during the opening statement?"

### Voice Queries
1. "Show me all objections from the defense attorney"
2. "When did the judge rule on the motion?"
3. "Find discussions about criminal intent"

## Latency Badge Visibility

**CRITICAL**: The latency badge must be clearly visible in the demo video. Ensure:

- Badge is positioned prominently (top-right or near query results)
- Font size is large enough to read at 1080p
- Color contrasts well with background (gold/yellow on dark navy)
- Badge updates immediately when query completes
- Latency number is clearly under 500ms

Example badge design:
```
┌─────────────────────┐
│  ⚡ Response: 387ms │
└─────────────────────┘
```

## Quality Checklist

Before finalizing the video, verify:

- [ ] Video is 1080p resolution
- [ ] Duration is 2-3 minutes
- [ ] Audio is clear and audible
- [ ] Latency badge is visible in all query demos
- [ ] All latency measurements show sub-500ms
- [ ] System demonstrates multimodal understanding
- [ ] Video clips play smoothly without buffering
- [ ] Speaker diarization labels are visible
- [ ] Real-time transcript updates are shown
- [ ] GitHub repository URL is displayed at end
- [ ] No API keys or sensitive information visible
- [ ] Video uploaded to YouTube or Vimeo
- [ ] Video embedded in README.md

## Troubleshooting

### Issue: Latency exceeds 500ms during recording

**Solution**: 
- Ensure backend is running without other heavy processes
- Use a simpler/shorter mock trial video
- Pre-warm the system with a few test queries before recording
- If necessary, record multiple takes and use the best one

### Issue: Video playback stutters during recording

**Solution**:
- Close other applications to free up resources
- Reduce OBS encoding settings temporarily
- Use a lower bitrate for recording
- Record in segments and edit together

### Issue: Audio quality is poor

**Solution**:
- Use an external microphone if available
- Record in a quiet environment
- Adjust microphone gain in OBS settings
- Consider recording narration separately and overlaying

### Issue: Screen recording is laggy

**Solution**:
- Lower OBS output resolution temporarily to 720p
- Reduce frame rate to 24fps
- Use hardware encoding if available (NVENC for NVIDIA GPUs)
- Close unnecessary background applications

## Final Notes

- **Authenticity matters**: Show the real system working, not a mock-up
- **Highlight the latency**: This is the key differentiator
- **Keep it concise**: 2 minutes is ideal, 3 minutes maximum
- **Show, don't just tell**: Demonstrate features in action
- **Professional presentation**: Clean UI, smooth narration, clear audio

Good luck with your demo video! 🎬
