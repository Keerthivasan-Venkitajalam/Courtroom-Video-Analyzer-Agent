# API Keys Setup Guide

This document provides instructions for provisioning all required API keys for the Courtroom Video Analyzer Agent.

## Required API Keys

### 1. Stream API (Video/Audio Infrastructure)
- **Purpose**: WebRTC video ingestion and real-time communication
- **Get Keys**: https://getstream.io/
- **Steps**:
  1. Create a free account at getstream.io
  2. Create a new app in the dashboard
  3. Copy your API Key and Secret
  4. Add to `.env`:
     ```
     STREAM_API_KEY=your_stream_api_key
     STREAM_SECRET=your_stream_secret
     ```

### 2. Twelve Labs API (Video Intelligence)
- **Purpose**: Video understanding with Pegasus 1.2 model
- **Get Keys**: https://playground.twelvelabs.io/
- **Steps**:
  1. Sign up for Twelve Labs Playground
  2. Navigate to API Keys section
  3. Generate a new API key
  4. Add to `.env`:
     ```
     TWELVE_LABS_API_KEY=your_twelve_labs_api_key
     ```

### 3. VideoDB API (Video Indexing)
- **Purpose**: Real-time video stream indexing and storage
- **Get Keys**: https://videodb.io/
- **Steps**:
  1. Create a sandbox account at videodb.io
  2. Access your dashboard
  3. Copy your API key
  4. Add to `.env`:
     ```
     VIDEODB_API_KEY=your_videodb_api_key
     ```

### 4. Deepgram API (Speech-to-Text)
- **Purpose**: Real-time transcription with speaker diarization
- **Get Keys**: https://deepgram.com/
- **Steps**:
  1. Sign up at deepgram.com
  2. Navigate to API Keys in console
  3. Create a new API key
  4. Add to `.env`:
     ```
     DEEPGRAM_API_KEY=your_deepgram_api_key
     ```

### 5. TurboPuffer API (Hybrid Search)
- **Purpose**: BM25 + vector search for transcript retrieval
- **Get Keys**: https://turbopuffer.com/
- **Steps**:
  1. Create account at turbopuffer.com
  2. Generate API key from dashboard
  3. Add to `.env`:
     ```
     TURBOPUFFER_API_KEY=your_turbopuffer_api_key
     ```

### 6. Gemini API (Query Processing)
- **Purpose**: Natural language query understanding via Gemini Live
- **Get Keys**: https://ai.google.dev/
- **Steps**:
  1. Visit Google AI Studio
  2. Create or select a project
  3. Generate API key
  4. Add to `.env`:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     ```

## Setup Instructions

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and replace all placeholder values** with your actual API keys

3. **Verify your setup**:
   ```bash
   python -c "from constants import *; print('✅ All environment variables loaded')"
   ```

4. **IMPORTANT**: Never commit `.env` to git. The `.gitignore` file is configured to exclude it.

## Security Best Practices

- ✅ `.env` files are in `.gitignore`
- ✅ Use `.env.example` with masked values for documentation
- ✅ Never share API keys in public repositories
- ✅ Rotate keys if accidentally exposed
- ✅ Use different keys for development and production

## Verification

To verify no API keys are in git history:
```bash
git log --all --full-history -- '*.env'
```

This should return no results.

## Free Tier Limits

Most services offer free tiers suitable for development and hackathon use:
- **Stream**: Free tier includes video calls
- **Twelve Labs**: Playground offers free credits
- **VideoDB**: Sandbox account available
- **Deepgram**: Free tier with usage limits
- **TurboPuffer**: Free tier available
- **Gemini**: Free tier with rate limits

## Support

If you encounter issues provisioning any API keys, refer to the respective service's documentation or contact their support teams.
