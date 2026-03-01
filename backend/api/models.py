"""
models.py
Pydantic request/response models for the FastAPI REST API.
Centralised here so server.py stays focused on routing logic.
"""
from typing import Dict, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Incoming natural-language query from the frontend chat panel."""
    query: str = Field(..., min_length=1, description="Natural language query string")
    session_id: str = Field(..., description="Active courtroom session ID")
    user_id: str = Field("attorney-user", description="Identifier for the requesting attorney")


# ---------------------------------------------------------------------------
# Result sub-models
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------

class QueryResponse(BaseModel):
    query_id: str
    transcript_results: List[TranscriptResult]
    video_results: List[VideoMatch]
    video_clips: List[VideoClip]
    total_latency_ms: int
    component_latencies: Dict[str, int]
