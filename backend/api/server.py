"""
server.py
FastAPI REST server: query processing, health checks, tool discovery.
Now the single-command orchestrator for both HTTP APIs and the continuous Stream Edge Vision Agent.
"""
import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import getstream
from dotenv import load_dotenv

load_dotenv()

from backend.core.logging_config import configure_logging, get_logger
from backend.core.constants import (
    SESSION_ID,
    MOCK_CAMERA_STREAM,
    ALLOWED_ORIGINS,
    STREAM_API_KEY,
    STREAM_API_SECRET,
)
from backend.indexing.indexer import CourtroomIndexer
from backend.tools.mcp_server import MCPServer
from backend.agent.agent import CourtroomAgentOrchestrator
from backend.api.models import (
    QueryRequest,
    QueryResponse,
    TranscriptResult,
    VideoMatch,
    VideoClip,
)

# Initialise logging before anything else
configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------

_indexer: Optional[CourtroomIndexer] = None
_mcp_server: Optional[MCPServer] = None
_agent_orchestrator: Optional[CourtroomAgentOrchestrator] = None
_stream_client: Optional[getstream.Stream] = None


# ---------------------------------------------------------------------------
# Lifespan (Single-Command Entry Point)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application startup and graceful shutdown.
    Initialises the indexer, the MCP tools, AND the Vision Agent orchestration
    so everything runs within a single unified process.
    """
    global _indexer, _mcp_server, _agent_orchestrator, _stream_client

    logger.info("=== Courtroom Video Analyzer Unified Server starting ===")

    try:
        # 1. Initialise Stream Client for Token Generation
        logger.info("[1/4] Initialising Stream Client Endpoint Support…")
        if STREAM_API_KEY and STREAM_API_SECRET:
            try:
                _stream_client = getstream.Stream(
                    api_key=STREAM_API_KEY,
                    api_secret=STREAM_API_SECRET,
                )
                logger.info("Stream Client ready | Tokens endpoint active")
            except Exception:
                logger.warning("Stream client failed — frontend won't be able to connect to stream")
        else:
            logger.warning("STREAM_API_KEY / SECRET not configured — stream tokens disabled")

        # 2. Initialise Indexer (Centralised instance)
        logger.info("[2/4] Initialising CourtroomIndexer…")
        _indexer = CourtroomIndexer(stream_url=MOCK_CAMERA_STREAM, session_id=SESSION_ID)
        if not await _indexer.start_live_indexing():
            logger.error("Failed to start indexing — aborting startup")
            raise RuntimeError("Indexer failed to start")
        logger.info("Indexer ready | scene_index_id=%s", _indexer.scene_index_id)

        # 3. Initialise MCP Server
        logger.info("[3/4] Initialising MCP Server…")
        _mcp_server = MCPServer(_indexer)
        logger.info("MCP Server ready | tools=%d", len(_mcp_server.tools))

        # 4. Launch Background Orchestrator
        logger.info("[4/4] Starting Vision Agent Orchestrator…")
        _agent_orchestrator = CourtroomAgentOrchestrator(
            room_id=SESSION_ID,
            indexer=_indexer,
            mcp=_mcp_server,
        )
        await _agent_orchestrator.start()
        
        logger.info("=== API + Vision Agent Unified Server is LIVE ===")
        yield  # Application runs here

    except Exception:
        logger.exception("Fatal error during startup")
        raise
    finally:
        # Graceful shutdown
        logger.info("Shutting down Unified Server…")
        if _agent_orchestrator:
            await _agent_orchestrator.stop()
        if _indexer:
            await _indexer.stop()
        _indexer = None
        _mcp_server = None
        _agent_orchestrator = None
        _stream_client = None
        logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Courtroom Video Analyzer Unified API",
    description="Backend providing REST tools and real-time Stream Edge Agent orchestration.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency helper
# ---------------------------------------------------------------------------

def _require_ready() -> None:
    """Raise HTTP 503 if the server has not finished initialising."""
    if _indexer is None or _mcp_server is None or _agent_orchestrator is None:
        raise HTTPException(status_code=503, detail="Service is still initialising")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
async def root():
    return {
        "status": "running",
        "service": "Courtroom Video Analyzer Unified Backend",
        "ready": _indexer is not None and _mcp_server is not None,
    }


@app.get("/health", tags=["health"])
async def health_check():
    _require_ready()
    return {
        "status": "healthy",
        "indexer": _indexer is not None,
        "mcp_server": _mcp_server is not None,
        "agent_running": _agent_orchestrator is not None,
        "scene_index_id": _indexer.scene_index_id if _indexer else None,
    }


# Optional request payload for token generation
class TokenRequest(BaseModel):
    user_id: str


@app.post("/api/stream/token", tags=["auth"])
async def get_stream_token(req: TokenRequest):
    """
    Generate a Stream JWT token so the frontend can join the Stream Edge room.
    """
    if not _stream_client:
        raise HTTPException(
            status_code=503, 
            detail="Stream client not configured. Provide STREAM_API_KEY and STREAM_API_SECRET."
        )
        
    try:
        # Stream Python SDK: Generate token for the specific user requested
        token = _stream_client.create_token(req.user_id)
        return {
            "token": token,
            "user_id": req.user_id,
            "room_id": SESSION_ID,
        }
    except Exception as e:
        logger.exception("Failed to generate Stream token")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse, tags=["queries"])
async def process_query(request: QueryRequest):
    _require_ready()
    start_time = time.monotonic()
    query_id = f"query_{int(time.time() * 1000)}"

    try:
        component_latencies = {}

        async def timed_indexer_call(coro, key: str):
            start = time.monotonic()
            result = await coro
            duration_ms = int((time.monotonic() - start) * 1000)
            component_latencies[key] = duration_ms
            return result

        raw_transcripts, raw_videos = await asyncio.gather(
            timed_indexer_call(
                _indexer.query_transcript(request.query, top_k=5),
                "transcript_search",
            ),
            timed_indexer_call(
                _indexer.query_video_moments(request.query),
                "video_search",
            ),
        )

        transcript_results: list[TranscriptResult] = [
            TranscriptResult(
                segment_id=f"seg_{r['timestamp_us']}",
                text=r["text"],
                speaker=r["speaker"],
                timestamp_us=r["timestamp_us"],
                relevance_score=r["relevance_score"],
            )
            for r in raw_transcripts
        ]

        video_results: list[VideoMatch] = []
        video_clips: list[VideoClip] = []
        for i, r in enumerate(raw_videos[:5]):
            ts_us = int(r.start_time * 1_000_000)
            video_results.append(
                VideoMatch(
                    frame_id=f"frame_{ts_us}",
                    timestamp_us=ts_us,
                    start_time=r.start_time,
                    end_time=r.end_time,
                    description=r.description,
                    relevance_score=0.85,
                )
            )
            video_clips.append(
                VideoClip(
                    clip_id=f"clip_{i}_{ts_us}",
                    start_timestamp_us=ts_us,
                    end_timestamp_us=int(r.end_time * 1_000_000),
                    duration_ms=int((r.end_time - r.start_time) * 1000),
                    hls_url=r.stream_url,
                )
            )

        total_latency_ms = int((time.monotonic() - start_time) * 1000)

        logger.info(
            "Query processed | id=%s latency=%dms transcript=%d video=%d",
            query_id,
            total_latency_ms,
            len(transcript_results),
            len(video_results),
        )

        return QueryResponse(
            query_id=query_id,
            transcript_results=transcript_results,
            video_results=video_results,
            video_clips=video_clips,
            total_latency_ms=total_latency_ms,
            component_latencies=component_latencies,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Query processing failed")


@app.get("/api/tools", tags=["tools"])
async def list_tools():
    _require_ready()
    return {"tools": _mcp_server.discover_tools()}


@app.get("/api/stats", tags=["monitoring"])
async def get_stats():
    _require_ready()
    return _mcp_server.get_invocation_stats()


# ---------------------------------------------------------------------------
# Local dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Unified API Server on http://0.0.0.0:8000")
    uvicorn.run("backend.api.server:app", host="0.0.0.0", port=8000, reload=True)
