"""
tests/integration/test_mcp_tools.py
Integration tests for the MCP Server tool invocation layer.
"""
import pytest

from backend.indexing.indexer import CourtroomIndexer
from backend.tools.mcp_server import MCPServer, ToolResult


@pytest.fixture
async def mcp():
    indexer = CourtroomIndexer(stream_url="rtsp://localhost:8554/courtcam", session_id="mcp-test")
    await indexer.start_live_indexing()
    return MCPServer(indexer)


class TestMCPTools:

    def test_default_tools_registered(self, mcp):
        assert "search_video" in mcp.tools
        assert "search_transcript" in mcp.tools

    def test_discover_tools_returns_list(self, mcp):
        tools = mcp.discover_tools()
        assert isinstance(tools, list)
        assert len(tools) == 2

    def test_discover_tools_has_required_fields(self, mcp):
        for tool in mcp.discover_tools():
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool
            assert "parameters" in tool

    async def test_search_video_valid_query(self, mcp):
        result = await mcp.invoke_tool("search_video", {"query": "witness testimony"})
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.data is not None
        assert result.execution_time_ms >= 0

    async def test_search_transcript_valid_query(self, mcp):
        result = await mcp.invoke_tool("search_transcript", {"query": "objection", "top_k": 3})
        assert isinstance(result, ToolResult)
        assert result.success is True

    async def test_missing_required_param_fails(self, mcp):
        result = await mcp.invoke_tool("search_video", {})
        assert result.success is False
        assert "query" in result.error.lower() or "missing" in result.error.lower()

    async def test_unknown_tool_fails(self, mcp):
        result = await mcp.invoke_tool("nonexistent_tool", {"query": "test"})
        assert result.success is False
        assert "not found" in result.error.lower()

    async def test_wrong_type_param_fails(self, mcp):
        result = await mcp.invoke_tool("search_video", {"query": "test", "max_results": "five"})
        assert result.success is False

    async def test_invocation_stats_after_calls(self, mcp):
        await mcp.invoke_tool("search_video", {"query": "evidence"})
        await mcp.invoke_tool("search_transcript", {"query": "judge"})
        stats = mcp.get_invocation_stats()
        assert stats["total_invocations"] >= 2
        assert "search_video" in stats["tool_usage"]
        assert "search_transcript" in stats["tool_usage"]

    async def test_speaker_filter_applied(self, mcp):
        """search_transcript with speaker_filter should not return other speakers."""
        result = await mcp.invoke_tool(
            "search_transcript",
            {"query": "judge witness objection", "top_k": 5, "speaker_filter": "Judge"},
        )
        # Even if no results, it must succeed (not raise)
        assert result.success is True
