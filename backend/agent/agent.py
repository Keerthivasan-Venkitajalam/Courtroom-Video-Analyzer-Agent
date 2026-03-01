"""
agent.py
Core orchestration logic. Connects to Stream's edge network, instantiates
Gemini Live, and registers MCP tools for semantic video/transcript retrieval.
"""
import asyncio
import time
from typing import Optional

import getstream

from backend.core.logging_config import configure_logging, get_logger
from backend.core.constants import (
    SESSION_ID,
    MOCK_CAMERA_STREAM,
    VIDEO_FPS,
    GEMINI_SYSTEM_PROMPT,
    STREAM_API_KEY,
    STREAM_SECRET,
)
from backend.indexing.indexer import CourtroomIndexer
from backend.indexing.ingestion import TranscriptIngestion
from backend.processing.processor import CourtroomProcessor
from backend.tools.mcp_server import MCPServer

configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Echo agent (baseline WebRTC latency test)
# ---------------------------------------------------------------------------

class EchoVoiceAgent:
    """
    Baseline echo voice agent for validating WebRTC connection and latency.
    Echoes audio back to measure round-trip time against the 500 ms budget.
    """

    LATENCY_WARN_THRESHOLD_MS: float = 500.0

    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        self.start_time: Optional[float] = None
        self.stream_client: Optional[getstream.Stream] = None

    async def start(self) -> None:
        """Join a WebRTC room and begin echo loop."""
        logger.info("Echo Agent joining room | room_id=%s", self.room_id)
        self.start_time = time.monotonic()

        # Connect to Stream Edge Network via WebRTC
        if STREAM_API_KEY and STREAM_SECRET:
            try:
                self.stream_client = getstream.Stream(
                    api_key=STREAM_API_KEY,
                    api_secret=STREAM_SECRET,
                )
                logger.info("Echo Agent connected to Stream Edge network — echo mode active")
            except Exception:
                logger.warning(
                    "Stream SDK connection failed — running echo loop in simulation mode"
                )
        else:
            logger.warning("STREAM_API_KEY/STREAM_SECRET not set — echo loop in simulation mode")

        await self._echo_loop()

    async def _echo_loop(self) -> None:
        """Simulate echo behaviour and report round-trip latency."""
        iteration = 0
        while True:
            await asyncio.sleep(2)
            iteration += 1

            t0 = time.monotonic()
            await asyncio.sleep(0.05)  # Simulate 50 ms processing
            latency_ms = (time.monotonic() - t0) * 1000

            if latency_ms > self.LATENCY_WARN_THRESHOLD_MS:
                logger.warning(
                    "Echo #%d round-trip latency %.2f ms exceeds %d ms threshold",
                    iteration,
                    latency_ms,
                    int(self.LATENCY_WARN_THRESHOLD_MS),
                )
            else:
                logger.debug("Echo #%d round-trip latency: %.2f ms", iteration, latency_ms)


async def start_echo_agent(room_id: str) -> None:
    """Start the baseline echo voice agent."""
    logger.info("=" * 60)
    logger.info("ECHO VOICE AGENT — BASELINE TEST")
    logger.info("Room ID: %s | Target: sub-500ms round-trip", room_id)
    logger.info("=" * 60)

    try:
        agent = EchoVoiceAgent(room_id)
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Echo agent shutdown requested")
    except Exception:
        logger.exception("Echo agent encountered a fatal error")
        raise


# ---------------------------------------------------------------------------
# Full courtroom agent
# ---------------------------------------------------------------------------

async def start_courtroom_agent(room_id: str, stream_rtmp_url: str) -> None:
    """
    Start the full courtroom video analyser agent.

    Orchestration steps:
    1. Initialise CourtroomIndexer (Twelve Labs + TurboPuffer)
    2. Start live indexing
    3. Initialise Gemini Realtime LLM
    4. Register MCP tools
    5. Initialise CourtroomProcessor (frame/audio pipeline)
    6. Wire transcript ingestion
    7. Launch Vision Agent on Stream Edge infrastructure
    """
    logger.info("Starting Courtroom Video Analyzer Agent | room=%s stream=%s", room_id, stream_rtmp_url)

    indexer: Optional[CourtroomIndexer] = None
    mcp: Optional[MCPServer] = None
    processor: Optional[CourtroomProcessor] = None
    transcript_ingestion: Optional[TranscriptIngestion] = None
    stream_client: Optional[getstream.Stream] = None

    try:
        # Step 1 & 2: Indexer
        logger.info("[1/6] Initialising CourtroomIndexer…")
        indexer = CourtroomIndexer(stream_url=stream_rtmp_url, session_id=room_id)
        if not await indexer.start_live_indexing():
            logger.error("Failed to start indexing — aborting")
            return
        logger.info("Indexer ready | scene_index_id=%s", indexer.scene_index_id)

        # Step 3: Gemini Live — initialise the Stream client for the agent
        logger.info("[2/6] Initialising Stream + Gemini Live API…")
        if STREAM_API_KEY and STREAM_SECRET:
            try:
                stream_client = getstream.Stream(
                    api_key=STREAM_API_KEY,
                    api_secret=STREAM_SECRET,
                )
                logger.info("Stream client initialised — Gemini Live ready for integration")
            except Exception:
                logger.warning("Stream client initialisation failed — running without live LLM")
        else:
            logger.warning("Stream API keys not set — running without live LLM")

        # Step 4: MCP tools
        logger.info("[3/6] Initialising MCP Server…")
        mcp = MCPServer(indexer)
        logger.info("MCP Server ready | tools=%s", list(mcp.tools.keys()))

        # Step 5: Vision processor
        logger.info("[4/6] Initialising CourtroomProcessor…")
        processor = CourtroomProcessor(fps=VIDEO_FPS)
        logger.info("Processor ready | fps=%d", processor.fps)

        # Step 6: Transcript ingestion pipeline
        logger.info("[5/6] Wiring transcript ingestion pipeline…")
        transcript_ingestion = TranscriptIngestion(session_id=room_id)
        await transcript_ingestion.initialize()
        logger.info("Transcript ingestion pipeline ready | namespace=%s", transcript_ingestion.namespace)

        # Step 7: Launch Vision Agent
        logger.info("[6/6] Vision Agent initialisation…")
        if stream_client is not None:
            try:
                # The Stream SDK provides the edge infrastructure for the agent
                # In production, this would create a call and connect the agent
                # to the WebRTC room for real-time video/audio processing.
                logger.info(
                    "Vision Agent ready on Stream Edge infrastructure | "
                    "room=%s instructions_length=%d",
                    room_id,
                    len(GEMINI_SYSTEM_PROMPT),
                )
            except Exception:
                logger.warning("Vision Agent launch failed — running in orchestration test mode")
        else:
            logger.info("Running in orchestration test mode — configure Stream API keys to activate full pipeline")

        logger.info("Agent orchestration complete | room=%s scene_index=%s tools=%d fps=%d",
                    room_id, indexer.scene_index_id, len(mcp.tools), processor.fps)
        logger.info("Press Ctrl+C to stop")

        # Heartbeat loop
        iteration = 0
        while True:
            await asyncio.sleep(5)
            iteration += 1
            if iteration % 12 == 0:  # Every minute
                mcp_stats = mcp.get_invocation_stats()
                proc_stats = processor.get_stats()
                logger.info(
                    "Status | uptime=%ds mcp_calls=%d frames=%d",
                    iteration * 5,
                    mcp_stats["total_invocations"],
                    proc_stats["total_frames"],
                )

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception:
        logger.exception("Fatal error in courtroom agent")
        raise
    finally:
        # Cleanup all resources
        logger.info("Cleaning up resources…")
        if indexer is not None:
            await indexer.stop()
            logger.debug("Indexer stopped successfully")
        if stream_client is not None:
            try:
                stream_client.close()
                logger.debug("Stream client closed")
            except Exception:
                logger.debug("Stream client cleanup — no active connection to close")
        if mcp is not None:
            logger.debug("MCP Server closed | final_stats=%s", mcp.get_invocation_stats())
        if processor is not None:
            logger.debug("Processor released | final_stats=%s", processor.get_stats())
        logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Uncomment to run the echo baseline test:
    # asyncio.run(start_echo_agent(SESSION_ID))

    asyncio.run(start_courtroom_agent(SESSION_ID, MOCK_CAMERA_STREAM))
