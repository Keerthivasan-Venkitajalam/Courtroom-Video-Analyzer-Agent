# Frontend-to-Backend Integration Guide

## Overview

This guide covers the frontend-to-backend integration for the Courtroom Video Analyzer, implementing Task 9.1 from the specification.

**Validates:**

- Property 2: End-to-end query latency (≤500ms)
- Property 40: Query routing to appropriate components

## Architecture

```
Frontend (React)          Backend (FastAPI)           Agent Layer
    |                           |                          |
    | POST /api/query           |                          |
    |-------------------------->|                          |
    |   { query: "..." }        |                          |
    |                           | invoke_tool()            |
    |                           |------------------------->|
    |                           |   search_transcript      |
    |                           |   search_video           |
    |                           |<-------------------------|
    |                           |   results + HLS URLs     |
    |<--------------------------|                          |
    |   JSON response           |                          |
    |   { videoClips: [...] }   |                          |
```

## Components

### 1. API Server (`api_server.py`)

FastAPI server that handles query requests from the frontend.

**Key Features:**

- CORS enabled for frontend communication
- Async query processing
- Latency tracking and logging
- MCP tool integration
- HLS URL generation

**Endpoints:**

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/query` - Process natural language queries
- `GET /api/tools` - List available MCP tools
- `GET /api/stats` - Get MCP server statistics

### 2. Frontend Integration (`frontend/src/App.tsx`)

React component that sends queries to the backend.

**Key Features:**

- Async query submission
- Latency measurement
- Error handling with fallback
- HLS URL handling for video playback

### 3. MCP Server Integration

The API server uses the existing MCP server to route queries to:

- `search_transcript` - TurboPuffer hybrid search
- `search_video` - Twelve Labs video intelligence

## API Contract

### Request Format

```typescript
POST /api/query
Content-Type: application/json

{
  "query": "What did the witness say about the contract?",
  "session_id": "courtroom-session-1",
  "user_id": "attorney-user"
}
```

### Response Format

```typescript
{
  "query_id": "query_1234567890",
  "transcript_results": [
    {
      "segment_id": "seg_1234567890",
      "text": "The witness stated...",
      "speaker": "Witness",
      "timestamp_us": 1234567890,
      "relevance_score": 0.95
    }
  ],
  "video_results": [
    {
      "frame_id": "frame_1234567890",
      "timestamp_us": 1234567890,
      "start_time": 123.45,
      "end_time": 145.67,
      "description": "Witness pointing at document",
      "relevance_score": 0.88
    }
  ],
  "video_clips": [
    {
      "clip_id": "clip_0_1234567890",
      "start_timestamp_us": 1234567890,
      "end_timestamp_us": 1456789012,
      "duration_ms": 22200,
      "hls_url": "https://stream.io/clips/..."
    }
  ],
  "total_latency_ms": 450,
  "component_latencies": {
    "transcript_search": 150,
    "video_search": 200
  }
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
uv pip install -r requirements.txt

# Install frontend dependencies
cd frontend
pnpm install
cd ..
```

### 2. Configure Environment

Ensure `.env` file contains:

```
STREAM_API_KEY=your_stream_api_key
STREAM_SECRET=your_stream_secret
TWELVE_LABS_API_KEY=your_twelve_labs_key
DEEPGRAM_API_KEY=your_deepgram_key
TURBOPUFFER_API_KEY=your_turbopuffer_key
```

### 3. Start the Backend

```bash
# Option 1: Using the startup script
./scripts/start_api_server.sh

# Option 2: Direct Python execution
python api_server.py
```

The API server will start on `http://localhost:8000`

### 4. Start the Frontend

```bash
cd frontend
pnpm run dev
```

The frontend will start on `http://localhost:5173`

## Testing

### Manual Testing

1. Start the API server
2. Start the frontend
3. Open browser to `http://localhost:5173`
4. Type a query in the chat panel
5. Verify:
   - Query is sent to backend
   - Response is received within 500ms
   - Video clips with HLS URLs are displayed
   - Latency is shown in the UI

### Automated Testing

Run the integration test suite:

```bash
# Make sure API server is running first
python test_integration.py
```

The test suite validates:

- API server health
- Query endpoint functionality
- Response format correctness
- HLS URL format
- Query routing to appropriate components
- Latency measurement

## Latency Optimization

The system is designed to meet the sub-500ms latency requirement:

| Component | Budget | Optimization |
|-----------|--------|--------------|
| Frontend → Backend | 50ms | Local network, CORS pre-flight cached |
| Transcript Search | 150ms | TurboPuffer hybrid search, indexed |
| Video Search | 200ms | Twelve Labs pre-computed embeddings |
| Response Assembly | 50ms | Parallel execution, minimal processing |
| Backend → Frontend | 50ms | JSON serialization, compression |
| **Total** | **500ms** | Parallel component execution |

### Latency Monitoring

The system logs latency at multiple levels:

1. **Client-side**: Measures round-trip time from query submission to response
2. **Server-side**: Measures total processing time
3. **Component-level**: Tracks individual component latencies

Latency warnings are logged when:

- Total latency exceeds 500ms
- Any component exceeds its budget
- Network latency is unusually high

## Query Routing

The system routes queries to appropriate components based on query type:

### Multimodal Queries

Queries that require both transcript and video search:

- "What did the witness say about the contract?"
- "Show me when the judge mentioned the evidence"

**Routing**: Both `search_transcript` and `search_video`

### Visual Queries

Queries focused on visual content:

- "Show me when the judge entered"
- "Find the moment the document was presented"

**Routing**: Primarily `search_video`

### Transcript Queries

Queries focused on spoken content:

- "Find the objection from the defense"
- "What did the prosecutor say about intent?"

**Routing**: Primarily `search_transcript`

## Error Handling

### Backend Errors

The API server handles errors gracefully:

1. **Initialization Errors**: Returns 503 status until fully initialized
2. **Query Processing Errors**: Returns 500 with error details
3. **Component Failures**: Continues with partial results
4. **Timeout Errors**: Logs latency breakdown for debugging

### Frontend Errors

The frontend handles errors with fallback behavior:

1. **Network Errors**: Shows error message, allows retry
2. **Timeout Errors**: Shows loading indicator, logs warning
3. **Invalid Responses**: Falls back to empty results
4. **Connection Refused**: Shows "Server not available" message

## Troubleshooting

### API Server Won't Start

**Issue**: `ModuleNotFoundError` or import errors

**Solution**: Install dependencies

```bash
uv pip install -r requirements.txt
```

### Frontend Can't Connect

**Issue**: CORS errors or connection refused

**Solution**:

1. Verify API server is running on port 8000
2. Check CORS configuration in `api_server.py`
3. Ensure frontend is using correct API URL

### High Latency

**Issue**: Queries exceed 500ms threshold

**Solution**:

1. Check component latencies in logs
2. Verify indexer is initialized
3. Check network latency
4. Review MCP tool performance

### No Results Returned

**Issue**: Empty transcript_results and video_results

**Solution**:

1. Verify indexer has indexed content
2. Check MCP tool invocation logs
3. Test MCP tools directly: `GET /api/tools`
4. Review query parsing logic

## Next Steps

After completing this integration:

1. **Task 9.2**: Implement real-time transcript streaming
2. **Task 9.3**: Add video clip playback with HLS
3. **Task 9.4**: Implement keyboard shortcuts
4. **Task 9.5**: Add timeline visualization

## References

- **Design Document**: `.kiro/specs/courtroom-video-analyzer/design.md`
- **Requirements**: `.kiro/specs/courtroom-video-analyzer/requirements.md`
- **MCP Server**: `mcp_server.py`
- **Agent Orchestrator**: `agent.py`
- **API Documentation**: `http://localhost:8000/docs` (when server is running)
