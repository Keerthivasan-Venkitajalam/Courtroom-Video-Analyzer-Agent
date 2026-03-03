"""
conftest.py
Shared pytest fixtures and test configuration for all test tiers.
"""
import asyncio
import pytest

from backend.core.logging_config import configure_logging

# Configure logging once for the entire test run
configure_logging()


# ---------------------------------------------------------------------------
# Async fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def courtroom_indexer():
    """Provide a CourtroomIndexer instance with mock indexing started."""
    from backend.indexing.indexer import CourtroomIndexer
    indexer = CourtroomIndexer(
        stream_url="rtsp://localhost:8554/courtcam",
        session_id="pytest-session",
    )
    await indexer.start_live_indexing()
    return indexer


@pytest.fixture
async def mcp_server(courtroom_indexer):
    """Provide a fully wired MCPServer instance."""
    from backend.tools.mcp_server import MCPServer
    return MCPServer(courtroom_indexer)


@pytest.fixture
def courtroom_processor():
    """Provide a CourtroomProcessor instance."""
    from backend.processing.processor import CourtroomProcessor
    return CourtroomProcessor(fps=5)
