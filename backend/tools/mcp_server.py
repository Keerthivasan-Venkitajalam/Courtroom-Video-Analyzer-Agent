"""
mcp_server.py
Model Context Protocol (MCP) server for secure tool integration.
Exposes search_video and search_transcript tools to the Gemini agent.
"""
import time
import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from backend.core.logging_config import get_logger
from backend.indexing.indexer import CourtroomIndexer

logger = get_logger(__name__)


class ToolCategory(Enum):
    VIDEO_SEARCH = "video_search"
    TRANSCRIPT_SEARCH = "transcript_search"
    PLAYBACK = "playback"
    METADATA = "metadata"


@dataclass
class ToolParameter:
    """Specification for a single tool parameter."""
    name: str
    type: str
    required: bool
    description: str
    default: Any = None


@dataclass
class Tool:
    """An MCP tool with metadata and an async handler."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    handler: Callable
    version: str = "1.0.0"


@dataclass
class ToolResult:
    """Result of a single tool invocation."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: int = 0


class MCPServer:
    """
    Model Context Protocol server.

    Provides:
    - Tool registration and discovery
    - Parameter validation
    - Audit logging (last 1 000 invocations kept in memory)
    """

    MAX_LOG_ENTRIES: int = 1_000

    def __init__(self, indexer: CourtroomIndexer) -> None:
        self.indexer = indexer
        self.tools: Dict[str, Tool] = {}
        self.invocation_log: List[Dict[str, Any]] = []

        logger.info("Initialising MCP Server")
        self._register_default_tools()
        logger.info("MCP Server ready | tools=%d", len(self.tools))

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_default_tools(self) -> None:
        self.register_tool(Tool(
            name="search_video",
            description=(
                "Search the live courtroom video for specific semantic moments, "
                "visual evidence, or actions. Use when the user asks about physical events."
            ),
            category=ToolCategory.VIDEO_SEARCH,
            parameters=[
                ToolParameter("query",       "string",  True,  "Natural language query describing the visual moment"),
                ToolParameter("max_results", "integer", False, "Maximum number of results to return", default=5),
            ],
            handler=self._handle_search_video,
        ))

        self.register_tool(Tool(
            name="search_transcript",
            description=(
                "Search the verbatim transcript for exact quotes or keywords using "
                "BM25 + vector hybrid search. Use for specific spoken statements."
            ),
            category=ToolCategory.TRANSCRIPT_SEARCH,
            parameters=[
                ToolParameter("query",          "string",  True,  "Search query for transcript content"),
                ToolParameter("top_k",          "integer", False, "Number of top results to return", default=5),
                ToolParameter("speaker_filter", "string",  False, "Filter by speaker role (Judge / Witness / Prosecution / Defense)", default=None),
            ],
            handler=self._handle_search_transcript,
        ))

    def register_tool(self, tool: Tool) -> bool:
        """Register a tool. Returns True, warns if overwriting an existing tool."""
        if tool.name in self.tools:
            logger.warning("Tool '%s' already registered — overwriting", tool.name)
        self.tools[tool.name] = tool
        logger.info("Registered tool | name=%s category=%s", tool.name, tool.category.value)
        return True

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Return a list of tool descriptors for discovery by the LLM."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "version": t.version,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "required": p.required,
                        "description": p.description,
                        "default": p.default,
                    }
                    for p in t.parameters
                ],
            }
            for t in self.tools.values()
        ]

    # ------------------------------------------------------------------
    # Validation & Invocation
    # ------------------------------------------------------------------

    def validate_invocation(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a tool invocation before executing it.

        Returns (is_valid, error_message_or_None).
        """
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not found"

        tool = self.tools[tool_name]

        for param in tool.parameters:
            if param.required and param.name not in parameters:
                return False, f"Required parameter '{param.name}' is missing"

        for param_name, param_value in parameters.items():
            spec = next((p for p in tool.parameters if p.name == param_name), None)
            if spec:
                if spec.type == "string" and not isinstance(param_value, str):
                    return False, f"Parameter '{param_name}' must be a string"
                elif spec.type == "integer" and not isinstance(param_value, int):
                    return False, f"Parameter '{param_name}' must be an integer"

        return True, None

    async def invoke_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> ToolResult:
        """
        Invoke a tool with validation. Records the call in the audit log.

        Returns a ToolResult with success status, data, and execution time.
        """
        start = time.monotonic()

        is_valid, error_msg = self.validate_invocation(tool_name, parameters)
        if not is_valid:
            elapsed = int((time.monotonic() - start) * 1000)
            self._log_invocation(tool_name, parameters, False, elapsed, error_msg)
            return ToolResult(success=False, data=None, error=error_msg, execution_time_ms=elapsed)

        tool = self.tools[tool_name]
        try:
            result_data = await tool.handler(parameters)
            elapsed = int((time.monotonic() - start) * 1000)
            self._log_invocation(tool_name, parameters, True, elapsed)
            return ToolResult(success=True, data=result_data, execution_time_ms=elapsed)

        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            error_msg = f"Tool execution failed: {exc}"
            logger.exception("Tool '%s' raised an exception", tool_name)
            self._log_invocation(tool_name, parameters, False, elapsed, error_msg)
            return ToolResult(success=False, data=None, error=error_msg, execution_time_ms=elapsed)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _handle_search_video(self, parameters: Dict[str, Any]) -> str:
        query = parameters["query"]
        max_results: int = parameters.get("max_results", 5)

        results = await self.indexer.query_video_moments(query)
        if not results:
            return "No matching video moments found in the Twelve Labs index."

        results = results[:max_results]
        lines = [f"Found {len(results)} relevant video clip(s):\n"]
        for i, r in enumerate(results, 1):
            duration = r.end_time - r.start_time
            lines.append(
                f"{i}. {r.start_time:.1f}s – {r.end_time:.1f}s ({duration:.1f}s)\n"
                f"   {r.description}\n"
                f"   ▶  {r.stream_url}\n"
            )
        return "\n".join(lines)

    async def _handle_search_transcript(self, parameters: Dict[str, Any]) -> str:
        query = parameters["query"]
        top_k: int = parameters.get("top_k", 5)
        speaker_filter: Optional[str] = parameters.get("speaker_filter")

        results = await self.indexer.query_transcript(query, top_k=top_k)

        if speaker_filter:
            results = [r for r in results if r["speaker"] == speaker_filter]

        if not results:
            return "No matching transcript segments found."

        lines = [f"Found {len(results)} relevant segment(s):\n"]
        for r in results:
            ts = r["timestamp_us"] / 1_000_000
            lines.append(
                f"{r['rank']}. [{r['speaker']} @ {ts:.1f}s] score={r['relevance_score']:.3f}\n"
                f"   {r['text']}\n"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def _log_invocation(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        success: bool,
        execution_time_ms: int,
        error: Optional[str] = None,
    ) -> None:
        entry = {
            "timestamp_ms": int(time.time() * 1000),
            "tool_name": tool_name,
            "parameters": parameters,
            "success": success,
            "execution_time_ms": execution_time_ms,
            "error": error,
        }
        self.invocation_log.append(entry)
        if len(self.invocation_log) > self.MAX_LOG_ENTRIES:
            self.invocation_log = self.invocation_log[-self.MAX_LOG_ENTRIES:]

    def get_invocation_stats(self) -> Dict[str, Any]:
        """Return aggregated statistics for monitoring dashboards."""
        total = len(self.invocation_log)
        successful = sum(1 for e in self.invocation_log if e["success"])
        tool_usage: Dict[str, int] = {}
        for e in self.invocation_log:
            tool_usage[e["tool_name"]] = tool_usage.get(e["tool_name"], 0) + 1

        avg_exec = (
            sum(e["execution_time_ms"] for e in self.invocation_log) / total
            if total > 0 else 0.0
        )
        return {
            "total_invocations": total,
            "successful": successful,
            "failed": total - successful,
            "tool_usage": tool_usage,
            "avg_execution_time_ms": avg_exec,
        }
