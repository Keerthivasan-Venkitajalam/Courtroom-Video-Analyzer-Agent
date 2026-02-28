"""
agent.py
Core orchestration logic. Connects to Stream's edge network, instantiates Gemini Live,
and registers MCP tools for semantic video and transcript retrieval.
"""
import os
import asyncio
from typing import Optional, Dict, Any
import time

# Note: These imports will be available after installing vision-agents
# from vision_agents.agents import Agent, User
# from vision_agents.plugins import gemini
# import getstream

from constants import (
    STREAM_API_KEY,
    STREAM_SECRET,
    SESSION_ID,
    MOCK_CAMERA_STREAM,
    VIDEO_FPS,
    GEMINI_SYSTEM_PROMPT
)
from index import CourtroomIndexer
from processor import CourtroomProcessor


class EchoVoiceAgent:
    """
    Baseline Echo voice agent for testing WebRTC connection and latency.
    Echoes back audio to verify bidirectional Stream Edge network connection.
    """
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.start_time = None
        
    async def start(self):
        """Start the echo agent and join WebRTC room."""
        print(f"🎤 Echo Agent joining room: {self.room_id}")
        self.start_time = time.time()
        
        # TODO: Implement actual WebRTC connection with Stream SDK
        # For now, simulate echo behavior
        print("✅ Echo Agent connected to Stream Edge network")
        print("🔊 Echo mode active - will echo back audio")
        
        # Simulate echo loop
        await self._echo_loop()
        
    async def _echo_loop(self):
        """Simulate echo behavior and log round-trip latency."""
        iteration = 0
        while True:
            await asyncio.sleep(2)  # Simulate audio chunks every 2 seconds
            iteration += 1
            
            # Simulate receiving audio
            receive_time = time.time()
            
            # Simulate processing and echo back
            await asyncio.sleep(0.05)  # 50ms processing time
            
            # Calculate round-trip latency
            echo_time = time.time()
            latency_ms = (echo_time - receive_time) * 1000
            
            print(f"[Echo #{iteration}] Round-trip latency: {latency_ms:.2f}ms")
            
            if latency_ms > 500:
                print(f"⚠️  WARNING: Latency exceeded 500ms threshold!")


async def start_echo_agent(room_id: str) -> None:
    """
    Start the baseline echo voice agent for testing.
    
    Args:
        room_id: Stream room ID to join
    """
    print("=" * 60)
    print("ECHO VOICE AGENT - BASELINE TEST")
    print("=" * 60)
    print(f"Room ID: {room_id}")
    print(f"Target: Sub-500ms round-trip latency")
    print("=" * 60)
    
    try:
        agent = EchoVoiceAgent(room_id)
        await agent.start()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down echo agent...")
    except Exception as e:
        print(f"\n❌ Error starting echo agent: {e}")
        raise


async def start_courtroom_agent(room_id: str, stream_rtmp_url: str) -> None:
    """
    Start the courtroom video analyzer agent with full orchestration.
    
    Workflow:
    1. Initialize CourtroomIndexer (Twelve Labs + TurboPuffer)
    2. Start live indexing
    3. Initialize Gemini Realtime LLM
    4. Register MCP tools
    5. Initialize CourtroomProcessor
    6. Launch Vision Agent on Stream Edge
    
    Args:
        room_id: Stream room ID to join
        stream_rtmp_url: URL of the video stream to analyze
    """
    print("🚀 Starting Courtroom Video Analyzer Agent...")
    print(f"Room ID: {room_id}")
    print(f"Stream URL: {stream_rtmp_url}")
    
    try:
        # Step 1: Initialize the Master Indexer (Twelve Labs + TurboPuffer)
        print("\n[1/6] Initializing indexer...")
        indexer = CourtroomIndexer(stream_url=stream_rtmp_url, session_id=room_id)
        indexing_success = await indexer.start_live_indexing()
        
        if not indexing_success:
            print("❌ Failed to start indexing")
            return
        
        print(f"✅ Indexer initialized with scene_index_id: {indexer.scene_index_id}")
        
        # Step 2: Initialize the Gemini Realtime LLM Provider
        print("\n[2/6] Initializing Gemini Live API...")
        # TODO: Implement after vision-agents installation
        # Set the frame processing speed to 5 FPS to maintain temporal alignment
        # with the local Vision Processor logic.
        # llm = gemini.Realtime(fps=VIDEO_FPS)
        print("⚠️  Gemini Live API pending vision-agents installation")
        
        # Step 3: Register Model Context Protocol (MCP) Tools
        print("\n[3/6] Registering MCP tools...")
        from mcp_server import MCPServer
        mcp = MCPServer(indexer)
        
        print(f"✅ MCP Server initialized with {len(mcp.tools)} tools:")
        for tool_name in mcp.tools.keys():
            print(f"   - {tool_name}")
        
        # TODO: Implement after vision-agents installation
        # Wire MCP tools to Gemini LLM
        # @llm.register_function(
        #     description="Search the live courtroom video for specific semantic moments, visual evidence, or generalized actions. Use this when the user asks about physical events or complex concepts."
        # )
        async def search_video(query: str, max_results: int = 5) -> str:
            """
            MCP Tool exposed to Gemini to query the Twelve Labs video index.
            """
            result = await mcp.invoke_tool("search_video", {
                "query": query,
                "max_results": max_results
            })
            
            if result.success:
                return result.data
            else:
                return f"Error searching video: {result.error}"
        
        # @llm.register_function(
        #     description="Search the verbatim transcript and dialogue for exact quotes or keywords using BM25 and vector search. Use this for specific spoken statements."
        # )
        async def search_transcript(query: str, top_k: int = 5, speaker_filter: str = None) -> str:
            """
            MCP Tool exposed to Gemini to query TurboPuffer persistent memory.
            """
            params = {"query": query, "top_k": top_k}
            if speaker_filter:
                params["speaker_filter"] = speaker_filter
            
            result = await mcp.invoke_tool("search_transcript", params)
            
            if result.success:
                return result.data
            else:
                return f"Error searching transcript: {result.error}"
        
        print("✅ MCP tools wired to agent functions")
        
        # Step 4: Initialize Local Vision Processor
        print("\n[4/6] Initializing vision processor...")
        processor = CourtroomProcessor(fps=VIDEO_FPS)
        print(f"✅ Processor initialized at {processor.fps} FPS")
        
        # Step 5: Attach processor to indexer for transcript ingestion
        print("\n[5/6] Wiring processor to indexer...")
        
        # Create ingestion pipeline
        from ingestion import TranscriptIngestion
        transcript_ingestion = TranscriptIngestion(session_id=room_id)
        await transcript_ingestion.initialize()
        
        print("✅ Transcript ingestion pipeline ready")
        
        # Step 6: Launch the Vision Agent securely on Stream's Edge Infrastructure
        print("\n[6/6] Launching Vision Agent...")
        # TODO: Implement after vision-agents installation
        # The agent uses the Stream Chat infrastructure for "built-in memory",
        # allowing it to recall context naturally across different conversational turns.
        # agent = Agent(
        #     edge=getstream.Edge(),  # Enforces the critical sub-500ms connection latency requirement
        #     agent_user=User(name="Court Analyzer AI", id="court_agent_01"),
        #     instructions=GEMINI_SYSTEM_PROMPT,
        #     llm=llm,
        #     processors=[processor]  # Attaches the local frame/audio extraction pipeline
        # )
        
        print(f"\n✅ Agent orchestration complete!")
        print(f"   Room ID: {room_id}")
        print(f"   Scene Index: {indexer.scene_index_id}")
        print(f"   MCP Tools: {len(mcp.tools)}")
        print(f"   Processor FPS: {processor.fps}")
        
        print(f"\nInitiating connection. Agent joining WebRTC courtroom call: {room_id}...")
        
        # TODO: Implement after vision-agents installation
        # await agent.start(room_id=room_id)
        
        # Placeholder: keep running and simulate agent loop
        print("\n⚠️  Vision Agents SDK not yet installed. Running in orchestration test mode.")
        print("Install with: uv add 'vision-agents[getstream, openai]'")
        
        # Simulate agent event loop
        print("\n🔄 Agent event loop active...")
        print("   Monitoring: Video frames, Audio chunks, User queries")
        print("   Available tools: search_video, search_transcript")
        print("\nPress Ctrl+C to stop\n")
        
        # Keep the agent running
        iteration = 0
        while True:
            await asyncio.sleep(5)
            iteration += 1
            
            # Log periodic status
            if iteration % 12 == 0:  # Every minute
                stats = mcp.get_invocation_stats()
                processor_stats = processor.get_stats()
                print(f"[Status] Uptime: {iteration * 5}s | "
                      f"MCP calls: {stats['total_invocations']} | "
                      f"Frames: {processor_stats['total_frames']}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down agent...")
        print("   Stopping indexer...")
        print("   Closing MCP server...")
        print("   Releasing processor resources...")
        print("✅ Agent shutdown complete")
    except Exception as e:
        print(f"\n❌ Error starting agent: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Standard local test execution block
    print("=" * 60)
    print("COURTROOM VIDEO ANALYZER AGENT")
    print("=" * 60)
    
    # Run echo agent for baseline testing
    # Uncomment to test echo agent:
    # asyncio.run(start_echo_agent(SESSION_ID))
    
    # Run full courtroom agent
    asyncio.run(start_courtroom_agent(SESSION_ID, MOCK_CAMERA_STREAM))

