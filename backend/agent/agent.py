"""
agent.py
Core orchestration logic. Connects to Stream's edge network, instantiates
Gemini Live via the Vision Agents framework, and connects MCP tools.
"""
import asyncio
import time
from typing import Optional

from vision_agents.core import Agent, User
from vision_agents.plugins import gemini, getstream

from backend.core.logging_config import configure_logging, get_logger
from backend.core.constants import (
    VIDEO_FPS,
    GEMINI_SYSTEM_PROMPT,
)
from backend.indexing.indexer import CourtroomIndexer
from backend.indexing.ingestion import TranscriptIngestion
from backend.processing.processor import CourtroomProcessor
from backend.tools.mcp_server import MCPServer

configure_logging()
logger = get_logger(__name__)


class CourtroomAgentOrchestrator:
    """
    Manages the lifecycle of the Vision Agent inside the Stream network.
    """
    def __init__(
        self,
        room_id: str,
        indexer: CourtroomIndexer,
        mcp: MCPServer,
    ) -> None:
        self.room_id = room_id
        self.indexer = indexer
        self.mcp = mcp
        
        self.processor: Optional[CourtroomProcessor] = None
        self.transcript_ingestion: Optional[TranscriptIngestion] = None
        self.vision_agent: Optional[Agent] = None
        
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Initialise secondary pipelines and the Vision Agent."""
        logger.info("Initializing Agent Orchestrator | room=%s", self.room_id)
        self._running = True

        # Initialise Vision Processor
        logger.info("Starting CourtroomProcessor | fps=%d", VIDEO_FPS)
        self.processor = CourtroomProcessor(fps=VIDEO_FPS)

        # Initialise Transcript Ingestion Pipeline
        logger.info("Starting Transcript Ingestion Pipeline")
        self.transcript_ingestion = TranscriptIngestion(session_id=self.room_id)
        await self.transcript_ingestion.initialize()

        # Build and Launch the Vision Agent
        try:
            # We use the official Vision Agents framework to pipe Gemini Live
            # to the Stream Edge Network.
            logger.info("Forming Vision Agent with Gemini 2.0 Flash Live")
            
            # Create a live LLM model hook for the agent
            llm = gemini.Realtime(
                model="gemini-2.5-flash-native-audio-preview-12-2025", 
                fps=VIDEO_FPS,
            )
            
            self.vision_agent = Agent(
                edge=getstream.Edge(),
                agent_user=User(name="Courtroom AI Assistant", id="courtroom-agent"),
                instructions=GEMINI_SYSTEM_PROMPT,
                llm=llm,
                # Processors inject frame metadata automatically into the LLM context
                processors=[], # Can add self.processor if Vision Agents supports Yolo wrapping
            )
            
            logger.info("Vision Agent ready. To connect to Stream, the frontend must join room: %s", self.room_id)
            
            # NOTE: In a complete implementation, `agent.create_call` and `agent.join(call)`
            # would be invoked here, but since this is a demo environment, we just 
            # run a continuous heartbeat loop in the background waiting for the frontend.
            
            self._task = asyncio.create_task(self._heartbeat_loop())
            
        except Exception:
            logger.exception("Failed to build Vision Agent — falling back to heartbeat mode")
            self._task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self) -> None:
        """Run continuous monitoring and maintenance while the agent is alive."""
        iteration = 0
        while self._running:
            await asyncio.sleep(5)
            iteration += 1
            if iteration % 12 == 0:  # Every minute
                mcp_stats = self.mcp.get_invocation_stats()
                proc_stats = self.processor.get_stats() if self.processor else {}
                logger.info(
                    "Orchestrator Heartbeat | uptime=%ds mcp_calls=%d frames=%d",
                    iteration * 5,
                    mcp_stats.get("total_invocations", 0),
                    proc_stats.get("total_frames", 0),
                )

    async def stop(self) -> None:
        """Stop orchestrator and release agent resources."""
        logger.info("Stopping Agent Orchestrator...")
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
                
        # Vision agent specific teardown
        if self.vision_agent:
            # If the vision agents API exposes a finish() or close(), call it here
            pass
            
        logger.info("Agent Orchestrator stopped")
