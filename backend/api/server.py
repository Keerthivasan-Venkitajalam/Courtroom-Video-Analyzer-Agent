"""
server.py
FastAPI REST server: query processing, health checks, tool discovery.
"""
import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.logging_config import configure_logging, get_logger
from backend.core.constants import SESSION_ID, MOCK_CAMERA_STREAM, ALLOWED_ORIGINS
from backend.indexing.indexer import CourtroomIndexer
from backend.tools.mcp_server import MCPServer
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


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application startup and graceful shutdown.
    Resources initialised here are available for the full lifetime of the app.
    """
    global _indexer, _mcp_server

    logger.info("=== Courtroom Video Analyzer API Server starting ===")

    try:
        # 1. Initialise indexer
        logger.info("[1/2] Initialising CourtroomIndexer…")
        _indexer = CourtroomIndexer(stream_url=MOCK_CAMERA_STREAM, session_id=SESSION_ID)
        if not await _indexer.start_live_indexing():
            logger.error("Failed to start indexing — aborting startup")
            raise RuntimeError("Indexer failed to start")
        logger.info("Indexer ready | scene_index_id=%s", _indexer.scene_index_id)

        # 2. Initialise MCP Server
        logger.info("[2/2] Initialising MCP Server…")
        _mcp_server = MCPServer(_indexer)
        logger.info("MCP Server ready | tools=%d", len(_mcp_server.tools))

        logger.info("=== API Server ready to accept requests ===")
        yield  # Application runs here

    except Exception:
        logger.exception("Fatal error during startup")
        raise
    finally:
        # Graceful shutdown
        logger.info("Shutting down API server…")
        _indexer = None
        _mcp_server = None
        logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Courtroom Video Analyzer API",
    description="Real-time multimodal AI for legal proceedings.",
    version="0.1.0",
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
    if _indexer is None or _mcp_server is None:
        raise HTTPException(status_code=503, detail="Service is still initialising")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
async def root():
    """Basic health check — always available even before full init."""
    return {
        "status": "running",
        "service": "Courtroom Video Analyzer API",
        "ready": _indexer is not None and _mcp_server is not None,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check — returns 503 while initialising."""
    _require_ready()
    return {
        "status": "healthy",
        "indexer": _indexer is not None,
        "mcp_server": _mcp_server is not None,
        "scene_index_id": _indexer.scene_index_id if _indexer else None,
    }


@app.post("/api/query", response_model=QueryResponse, tags=["queries"])
async def process_query(request: QueryRequest):
    """
    Process a natural-language query from the frontend chat panel.

    Both transcript and video searches run concurrently via asyncio.gather
    to minimise end-to-end latency.
    """
    _require_ready()

    start_time = time.monotonic()
    query_id = f"query_{int(time.time() * 1000)}"

    try:
        # --- Run both searches concurrently -----------------------------------
        (transcript_result, video_result) = await asyncio.gather(
            _mcp_server.invoke_tool("search_transcript", {"query": request.query, "top_k": 5}),
            _mcp_server.invoke_tool("search_video",      {"query": request.query, "max_results": 5}),
        )

        component_latencies = {}

        # --- Parse transcript results -----------------------------------------
        transcript_results: list[TranscriptResult] = []
        if transcript_result.success:
            raw_transcripts = await _indexer.query_transcript(request.query, top_k=5)
            transcript_results = [
                TranscriptResult(
                    segment_id=f"seg_{r['timestamp_us']}",
                    text=r["text"],
                    speaker=r["speaker"],
                    timestamp_us=r["timestamp_us"],
                    relevance_score=r["relevance_score"],
                )
                for r in raw_transcripts
            ]

        # --- Parse video results -----------------------------------------------
        video_results: list[VideoMatch] = []
        video_clips: list[VideoClip] = []
        if video_result.success:
            raw_videos = await _indexer.query_video_moments(request.query)
            for i, r in enumerate(raw_videos[:5]):
                ts_us = int(r.start_time * 1_000_000)
                video_results.append(VideoMatch(
                    frame_id=f"frame_{ts_us}",
                    timestamp_us=ts_us,
                    start_time=r.start_time,
                    end_time=r.end_time,
                    description=r.description,
                    relevance_score=0.85,  # Placeholder until real scores from SDK
                ))
                video_clips.append(VideoClip(
                    clip_id=f"clip_{i}_{ts_us}",
                    start_timestamp_us=ts_us,
                    end_timestamp_us=int(r.end_time * 1_000_000),
                    duration_ms=int((r.end_time - r.start_time) * 1000),
                    hls_url=r.stream_url,
                ))

        total_latency_ms = int((time.monotonic() - start_time) * 1000)
        component_latencies["transcript_search"] = transcript_result.execution_time_ms
        component_latencies["video_search"] = video_result.execution_time_ms

        logger.info(
            "Query processed | id=%s latency=%dms transcript=%d video=%d",
            query_id,
            total_latency_ms,
            len(transcript_results),
            len(video_results),
        )

        if total_latency_ms > 500:
            logger.warning("Query latency %dms exceeds 500ms budget", total_latency_ms)

        return QueryResponse(
            query_id=query_id,
            transcript_results=transcript_results,
            video_results=video_results,
            video_clips=video_clips,
            total_latency_ms=total_latency_ms,
            component_latencies=component_latencies,
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error processing query '%s'", request.query)
        raise HTTPException(status_code=500, detail="Query processing failed")


@app.get("/api/tools", tags=["tools"])
async def list_tools():
    """List all available MCP tools."""
    _require_ready()
    return {"tools": _mcp_server.discover_tools()}


@app.get("/api/stats", tags=["monitoring"])
async def get_stats():
    """Return MCP server invocation statistics."""
    _require_ready()
    return _mcp_server.get_invocation_stats()


# ---------------------------------------------------------------------------
# Local dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server on http://0.0.0.0:8000")
    logger.info("Interactive docs → http://localhost:8000/docs")
    uvicorn.run("backend.api.server:app", host="0.0.0.0", port=8000, reload=True)
