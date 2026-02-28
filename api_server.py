"""
api_server.py
FastAPI server for frontend-to-backend integration.
Handles query requests from the frontend and routes them to the agent orchestrator.
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import start_courtroom_agent
from mcp_server import MCPServer
from index import CourtroomIndexer
from constants import SESSION_ID, MOCK_CAMERA_STREAM


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    session_id: str
    user_id: str = "attorney-user"


class TranscriptResult(BaseModel):
    segment_id: str
    text: str
    speaker: str
    timestamp_us: int
    relevance_score: float


class VideoMatch(BaseModel):
    frame_id: str
    timestamp_us: int
    start_time: float
    end_time: float
    description: str
    relevance_score: float


class VideoClip(BaseModel):
    clip_id: str
    start_timestamp_us: int
    end_timestamp_us: int
    duration_ms: int
    hls_url: str


class QueryResponse(BaseModel):
    query_id: str
    transcript_results: List[TranscriptResult]
    video_results: List[VideoMatch]
    video_clips: List[VideoClip]
    total_latency_ms: int
    component_latencies: Dict[str, int]


# Initialize FastAPI app
app = FastAPI(title="Courtroom Video Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
indexer: Optional[CourtroomIndexer] = None
mcp_server: Optional[MCPServer] = None
initialization_complete = False


@app.on_event("startup")
async def startup_event():
    """Initialize the agent orchestrator on startup."""
    global indexer, mcp_server, initialization_complete
    
    print("🚀 Starting Courtroom Video Analyzer API Server...")
    
    try:
        # Initialize indexer
        print("[1/2] Initializing indexer...")
        indexer = CourtroomIndexer(stream_url=MOCK_CAMERA_STREAM, session_id=SESSION_ID)
        indexing_success = await indexer.start_live_indexing()
        
        if not indexing_success:
            print("❌ Failed to start indexing")
            return
        
        print(f"✅ Indexer initialized with scene_index_id: {indexer.scene_index_id}")
        
        # Initialize MCP server
        print("[2/2] Initializing MCP server...")
        mcp_server = MCPServer(indexer)
        print(f"✅ MCP Server initialized with {len(mcp_server.tools)} tools")
        
        initialization_complete = True
        print("✅ API Server ready to accept queries")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Courtroom Video Analyzer API",
        "initialized": initialization_complete
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    if not initialization_complete:
        raise HTTPException(status_code=503, detail="Service initializing")
    
    return {
        "status": "healthy",
        "indexer": indexer is not None,
        "mcp_server": mcp_server is not None,
        "scene_index_id": indexer.scene_index_id if indexer else None
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query from the frontend.
    
    This endpoint:
    1. Receives a text query from the chat panel
    2. Routes it through the MCP server to search video and transcript
    3. Returns JSON response with HLS URLs for video playback
    
    Validates: Property 2 (End-to-end query latency), Property 40 (Query routing)
    """
    if not initialization_complete:
        raise HTTPException(status_code=503, detail="Service still initializing")
    
    start_time = time.time()
    component_latencies = {}
    
    try:
        query_id = f"query_{int(time.time() * 1000)}"
        
        # Step 1: Search transcript (parallel with video search)
        transcript_start = time.time()
        transcript_tool_result = await mcp_server.invoke_tool(
            "search_transcript",
            {"query": request.query, "top_k": 5}
        )
        component_latencies["transcript_search"] = int((time.time() - transcript_start) * 1000)
        
        # Step 2: Search video
        video_start = time.time()
        video_tool_result = await mcp_server.invoke_tool(
            "search_video",
            {"query": request.query, "max_results": 5}
        )
        component_latencies["video_search"] = int((time.time() - video_start) * 1000)
        
        # Step 3: Parse results
        transcript_results = []
        if transcript_tool_result.success:
            # Parse transcript results from MCP tool response
            raw_transcript = await indexer.query_transcript(request.query, top_k=5)
            for result in raw_transcript:
                transcript_results.append(TranscriptResult(
                    segment_id=f"seg_{result['timestamp_us']}",
                    text=result['text'],
                    speaker=result['speaker'],
                    timestamp_us=result['timestamp_us'],
                    relevance_score=result['relevance_score']
                ))
        
        video_results = []
        video_clips = []
        if video_tool_result.success:
            # Parse video results from MCP tool response
            raw_video = await indexer.query_video_moments(request.query)
            for i, result in enumerate(raw_video[:5]):
                timestamp_us = int(result.start_time * 1_000_000)
                
                video_match = VideoMatch(
                    frame_id=f"frame_{timestamp_us}",
                    timestamp_us=timestamp_us,
                    start_time=result.start_time,
                    end_time=result.end_time,
                    description=result.description,
                    relevance_score=0.85  # Placeholder
                )
                video_results.append(video_match)
                
                # Generate HLS URL for video clip
                video_clip = VideoClip(
                    clip_id=f"clip_{i}_{timestamp_us}",
                    start_timestamp_us=timestamp_us,
                    end_timestamp_us=int(result.end_time * 1_000_000),
                    duration_ms=int((result.end_time - result.start_time) * 1000),
                    hls_url=result.stream_url
                )
                video_clips.append(video_clip)
        
        # Calculate total latency
        total_latency_ms = int((time.time() - start_time) * 1000)
        
        # Log latency
        print(f"[Query] {request.query[:50]}... | Latency: {total_latency_ms}ms")
        print(f"  - Transcript search: {component_latencies.get('transcript_search', 0)}ms")
        print(f"  - Video search: {component_latencies.get('video_search', 0)}ms")
        
        if total_latency_ms > 500:
            print(f"⚠️  WARNING: Query latency {total_latency_ms}ms exceeds 500ms threshold!")
        
        return QueryResponse(
            query_id=query_id,
            transcript_results=transcript_results,
            video_results=video_results,
            video_clips=video_clips,
            total_latency_ms=total_latency_ms,
            component_latencies=component_latencies
        )
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.get("/api/tools")
async def list_tools():
    """List available MCP tools."""
    if not initialization_complete:
        raise HTTPException(status_code=503, detail="Service still initializing")
    
    return {
        "tools": mcp_server.discover_tools()
    }


@app.get("/api/stats")
async def get_stats():
    """Get MCP server statistics."""
    if not initialization_complete:
        raise HTTPException(status_code=503, detail="Service still initializing")
    
    return mcp_server.get_invocation_stats()


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("COURTROOM VIDEO ANALYZER API SERVER")
    print("=" * 60)
    print("Starting FastAPI server on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
