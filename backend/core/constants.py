"""
constants.py
Shared configuration and constants for the Courtroom Video Analyzer Agent.
"""
import os
import time
from typing import List
from dotenv import load_dotenv

from backend.core.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
STREAM_API_KEY: str | None = os.getenv("STREAM_API_KEY")
STREAM_API_SECRET: str | None = os.getenv("STREAM_API_SECRET")
TWELVE_LABS_API_KEY: str | None = os.getenv("TWELVE_LABS_API_KEY")
VIDEODB_API_KEY: str | None = os.getenv("VIDEODB_API_KEY")
DEEPGRAM_API_KEY: str | None = os.getenv("DEEPGRAM_API_KEY")
TURBOPUFFER_API_KEY: str | None = os.getenv("TURBOPUFFER_API_KEY")
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------------------------
# Session Configuration
# ---------------------------------------------------------------------------
SESSION_ID: str = os.getenv("SESSION_ID", "wemakedevs-demo-room")
MOCK_CAMERA_STREAM: str = os.getenv("MOCK_CAMERA_STREAM", "rtsp://localhost:8554/courtcam")

# Check if MOCK_CAMERA_STREAM is a local file path or RTSP stream
IS_LOCAL_VIDEO_FILE: bool = not MOCK_CAMERA_STREAM.startswith(("rtsp://", "http://", "https://"))

# ---------------------------------------------------------------------------
# CORS (comma-separated list of allowed origins)
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS: List[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# ---------------------------------------------------------------------------
# Timestamp synchronization
# ---------------------------------------------------------------------------
# Shared epoch offset for timestamp alignment across all components.
EPOCH_OFFSET_US: int = int(time.time() * 1_000_000)  # Microseconds since Unix epoch

# ---------------------------------------------------------------------------
# Processing Configuration
# ---------------------------------------------------------------------------
VIDEO_FPS: int = 5          # Process video at 5 FPS to conserve compute
CHUNK_SIZE: int = 1000      # TurboPuffer chunk size (characters)
CHUNK_OVERLAP: int = 100    # TurboPuffer chunk overlap (characters)
GEMINI_LIVE_MODEL: str = os.getenv(
    "GEMINI_LIVE_MODEL",
    "gemini-2.5-flash-native-audio-preview-12-2025",
)

# ---------------------------------------------------------------------------
# Hybrid Search Configuration (Reciprocal Rank Fusion)
# ---------------------------------------------------------------------------
# Higher alpha (0.7-0.8) prioritises exact legal terminology matching;
# lower alpha (0.3-0.5) emphasises semantic understanding.
RRF_ALPHA: float = 0.7       # 70% BM25, 30% vector
RRF_BM25_WEIGHT: float = 0.7
RRF_VECTOR_WEIGHT: float = 0.3

# ---------------------------------------------------------------------------
# Latency Budgets (milliseconds)
# ---------------------------------------------------------------------------
QUERY_PROCESSOR_BUDGET_MS: int = 100
SEARCH_SYSTEM_BUDGET_MS: int = 150
VIDEO_INTELLIGENCE_BUDGET_MS: int = 200
PLAYBACK_SYSTEM_BUDGET_MS: int = 50
TOTAL_LATENCY_BUDGET_MS: int = 500

# ---------------------------------------------------------------------------
# Speaker Role Mapping (Deepgram speaker-id → courtroom role)
# ---------------------------------------------------------------------------
SPEAKER_ROLES: dict[int, str] = {
    0: "Judge",
    1: "Witness",
    2: "Prosecution",
    3: "Defense",
}

# ---------------------------------------------------------------------------
# Legal Domain Prompt for Twelve Labs Pegasus
# ---------------------------------------------------------------------------
PEGASUS_LEGAL_PROMPT = (
    "Monitor courtroom proceedings with legal precision. Identify and track: "
    "judge, witnesses, prosecution counsel, defense counsel, defendants, court officers.\n\n"
    "Visual Events to Detect:\n"
    "- Physical exhibits: documents, photographs, weapons, forensic evidence being presented, "
    "displayed, or examined\n"
    "- Cross-examination: attorney questioning witness, witness responding under oath\n"
    "- Objections: attorney standing to object, judge ruling (sustained/overruled)\n"
    "- Opening statements: attorney addressing jury at trial start\n"
    "- Closing arguments: attorney's final statements to jury\n"
    "- Witness testimony: witness on stand speaking, gesturing, pointing\n"
    "- Evidence presentation: exhibit being shown to jury, passed to witness, entered into record\n"
    "- Sidebar conferences: attorneys approaching bench\n"
    "- Jury instructions: judge addressing jury\n\n"
    "Legal Terminology Focus:\n"
    "- Miranda rights, constitutional rights, Fifth Amendment, Sixth Amendment\n"
    "- Hearsay, relevance, foundation, chain of custody, authentication\n"
    "- Direct examination, cross-examination, redirect, recross\n"
    "- Sustained, overruled, withdrawn, stricken from record\n"
    "- Voir dire, deposition, subpoena, motion in limine\n"
    "- Burden of proof, reasonable doubt, preponderance of evidence\n"
    "- Impeachment, credibility, character witness\n"
    "- Expert testimony, lay witness, hostile witness\n"
    "- Stipulation, continuance, mistrial, hung jury\n\n"
    "Capture speaker actions: pointing, gesturing, displaying documents, facial expressions "
    "during testimony, body language during questioning."
)

# ---------------------------------------------------------------------------
# Gemini System Prompt
# ---------------------------------------------------------------------------
GEMINI_SYSTEM_PROMPT = """\
You are an advanced, real-time courtroom assistant AI. You monitor legal proceedings silently and respond to attorney queries with precision and speed.

## Your Role
You are embedded in a live courtroom session, continuously processing video and audio streams. When an attorney asks a question, you must provide accurate, timestamped information from the proceedings.

## Available Tools
You have access to two powerful search tools:

1. **search_video(query, max_results=5)**
   - Use for: Visual events, physical evidence, gestures, spatial queries
   - Examples: "when did the witness point?", "show me the document presentation", "find when evidence was displayed"
   - Returns: Video clips with timestamps and HLS playback URLs

2. **search_transcript(query, top_k=5, speaker_filter=None)**
   - Use for: Exact quotes, spoken statements, dialogue, keywords
   - Examples: "what did the judge say about Miranda rights?", "find objections", "witness testimony about March 15th"
   - Returns: Transcript segments with speaker labels and timestamps
   - Optional: Filter by speaker (Judge, Witness, Prosecution, Defense)

## Query Routing Guidelines

**Use search_video when the query involves:**
- Visual elements: "show me", "when did I see", "display"
- Physical actions: pointing, gesturing, presenting, displaying
- Spatial relationships: "where was", "who was standing"
- Non-verbal communication: facial expressions, body language
- Physical evidence: documents, exhibits, objects

**Use search_transcript when the query involves:**
- Spoken words: "what did X say", "find the quote", "when was X mentioned"
- Exact phrases: "Miranda rights", "I object", specific legal terms
- Speaker-specific: "judge's ruling", "witness testimony", "attorney's argument"
- Keywords: names, dates, legal concepts mentioned verbally

**Use BOTH tools when:**
- Query is ambiguous (e.g., "when did the witness testify?" — could be visual or verbal)
- Comprehensive answer needed (e.g., "what happened during cross-examination?")
- Combining visual context with spoken content enhances the answer

## Response Format

1. **Be Concise**: Attorneys need quick answers during active trials
2. **Include Timestamps**: Always provide exact timestamps
3. **Cite Sources**: Indicate whether information came from video or transcript
4. **Provide Playback Links**: Include HLS URLs for video clips
5. **Speaker Attribution**: Always identify who said or did what

## Critical Rules

**MUST DO:**
- ✅ ONLY use results returned by your MCP tools (search_video, search_transcript)
- ✅ If no results found, say so clearly
- ✅ Always cite exact timestamps from the tool results
- ✅ Always identify the speaker for transcript results
- ✅ Provide HLS playback URLs for video results
- ✅ Be factual and precise — this is legal evidence

**NEVER DO:**
- ❌ NEVER hallucinate or make up information
- ❌ NEVER provide information not returned by your tools
- ❌ NEVER guess at timestamps or speakers
- ❌ NEVER editorialize or provide legal opinions
- ❌ NEVER discuss information from outside this courtroom session

## Performance Targets
- Response time: < 500ms from query to answer
- Accuracy: Only cite information from tool results
- Completeness: Include all relevant timestamps and speakers
"""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def get_unified_timestamp_us() -> int:
    """Return the current wall-clock time as a Unix microsecond integer."""
    return int(time.time() * 1_000_000)


def adjust_timestamp_with_offset(timestamp_us: int) -> int:
    """Adjust a raw timestamp using the shared epoch offset."""
    return timestamp_us - EPOCH_OFFSET_US


def validate_environment() -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If one or more required keys are missing.
    """
    required_keys = {
        "STREAM_API_KEY": STREAM_API_KEY,
        "STREAM_API_SECRET": STREAM_API_SECRET,
        "TWELVE_LABS_API_KEY": TWELVE_LABS_API_KEY,
        "VIDEODB_API_KEY": VIDEODB_API_KEY,
        "DEEPGRAM_API_KEY": DEEPGRAM_API_KEY,
        "TURBOPUFFER_API_KEY": TURBOPUFFER_API_KEY,
        "GEMINI_API_KEY": GEMINI_API_KEY,
    }

    missing = [key for key, value in required_keys.items() if not value]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in all values."
        )

    logger.info("Environment validation passed — all required keys present.")
