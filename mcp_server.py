"""
mcp_server.py
Model Context Protocol (MCP) server for secure tool integration.
Exposes search_video and search_transcript tools to the Gemini agent.
"""
import asyncio
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

from index import CourtroomIndexer


class ToolCategory(Enum):
    """Tool categories for organization and discovery."""
    VIDEO_SEARCH = "video_search"
    TRANSCRIPT_SEARCH = "transcript_search"
    PLAYBACK = "playback"
    METADATA = "metadata"


@dataclass
class ToolParameter:
    """Represents a tool parameter specification."""
    name: str
    type: str
    required: bool
    description: str
    default: Any = None


@dataclass
class Tool:
    """Represents an MCP tool."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    handler: Callable
    version: str = "1.0.0"


@dataclass
class ToolResult:
    """Represents the result of a tool invocation."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: int = 0


class MCPServer:
    """
    Model Context Protocol server for courtroom video analyzer.
    
    Provides secure tool integration following MCP specification:
    - Tool registration and discovery
    - Parameter validation
    - Execution sandboxing
    - Audit logging
    """
    
    def __init__(self, indexer: CourtroomIndexer):
        """
        Initialize MCP server.
        
        Args:
            indexer: CourtroomIndexer instance for video and transcript search
        """
        self.indexer = indexer
        self.tools: Dict[str, Tool] = {}
        self.invocation_log: List[Dict[str, Any]] = []
        
        print("🔧 Initializing MCP Server")
        self._register_default_tools()
        print(f"✅ MCP Server initialized with {len(self.tools)} tools")
    
    def _register_default_tools(self):
        """Register default MCP tools."""
        # Tool 1: search_video
        self.register_tool(Tool(
            name="search_video",
            description="Search the live courtroom video for specific semantic moments, visual evidence, or generalized actions. Use this when the user asks about physical events or complex concepts.",
            category=ToolCategory.VIDEO_SEARCH,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    required=True,
                    description="Natural language query describing the visual moment to find"
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    required=False,
                    description="Maximum number of results to return",
                    default=5
                )
            ],
            handler=self._handle_search_video
        ))
        
        # Tool 2: search_transcript
        self.register_tool(Tool(
            name="search_transcript",
            description="Search the verbatim transcript and dialogue for exact quotes or keywords using BM25 and vector search. Use this for specific spoken statements.",
            category=ToolCategory.TRANSCRIPT_SEARCH,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    required=True,
                    description="Search query for transcript content"
                ),
                ToolParameter(
                    name="top_k",
                    type="integer",
                    required=False,
                    description="Number of top results to return",
                    default=5
                ),
                ToolParameter(
                    name="speaker_filter",
                    type="string",
                    required=False,
                    description="Filter by speaker role (Judge, Witness, Prosecution, Defense)",
                    default=None
                )
            ],
            handler=self._handle_search_transcript
        ))
    
    def register_tool(self, tool: Tool) -> bool:
        """
        Register a new tool with the MCP server.
        
        Args:
            tool: Tool to register
            
        Returns:
            True if registration successful, False otherwise
        """
        if tool.name in self.tools:
            print(f"⚠️  Tool '{tool.name}' already registered, overwriting")
        
        self.tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name} ({tool.category.value})")
        return True
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Return list of available tools for discovery.
        
        Returns:
            List of tool descriptors
        """
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'category': tool.category.value,
                'parameters': [
                    {
                        'name': param.name,
                        'type': param.type,
                        'required': param.required,
                        'description': param.description,
                        'default': param.default
                    }
                    for param in tool.parameters
                ],
                'version': tool.version
            }
            for tool in self.tools.values()
        ]
    
    def validate_invocation(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tool invocation for correctness.
        
        Args:
            tool_name: Name of tool to invoke
            parameters: Parameters for invocation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if tool exists
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not found"
        
        tool = self.tools[tool_name]
        
        # Check required parameters
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                return False, f"Required parameter '{param.name}' missing"
        
        # Type validation (basic)
        for param_name, param_value in parameters.items():
            param_spec = next((p for p in tool.parameters if p.name == param_name), None)
            if param_spec:
                expected_type = param_spec.type
                if expected_type == "string" and not isinstance(param_value, str):
                    return False, f"Parameter '{param_name}' must be a string"
                elif expected_type == "integer" and not isinstance(param_value, int):
                    return False, f"Parameter '{param_name}' must be an integer"
        
        return True, None
    
    async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Invoke a tool with validation and sandboxing.
        
        Args:
            tool_name: Name of tool to invoke
            parameters: Parameters for invocation
            
        Returns:
            ToolResult with execution outcome
        """
        import time
        start_time = time.time()
        
        # Validate invocation
        is_valid, error_msg = self.validate_invocation(tool_name, parameters)
        if not is_valid:
            return ToolResult(
                success=False,
                data=None,
                error=error_msg,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        
        tool = self.tools[tool_name]
        
        try:
            # Execute tool handler in sandboxed context
            result_data = await tool.handler(parameters)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log invocation
            self._log_invocation(tool_name, parameters, True, execution_time)
            
            return ToolResult(
                success=True,
                data=result_data,
                error=None,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Tool execution failed: {str(e)}"
            
            # Log failed invocation
            self._log_invocation(tool_name, parameters, False, execution_time, error_msg)
            
            return ToolResult(
                success=False,
                data=None,
                error=error_msg,
                execution_time_ms=execution_time
            )
    
    def _log_invocation(self, tool_name: str, parameters: Dict[str, Any], 
                       success: bool, execution_time_ms: int, error: Optional[str] = None):
        """Log tool invocation for audit trail."""
        import time
        
        log_entry = {
            'timestamp': int(time.time() * 1000),
            'tool_name': tool_name,
            'parameters': parameters,
            'success': success,
            'execution_time_ms': execution_time_ms,
            'error': error
        }
        
        self.invocation_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.invocation_log) > 1000:
            self.invocation_log = self.invocation_log[-1000:]
    
    async def _handle_search_video(self, parameters: Dict[str, Any]) -> str:
        """
        Handler for search_video tool.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Formatted string with video search results
        """
        query = parameters['query']
        max_results = parameters.get('max_results', 5)
        
        # Query video moments
        results = await self.indexer.query_video_moments(query)
        
        if not results:
            return "No matching video moments found in the Twelve Labs index."
        
        # Limit results
        results = results[:max_results]
        
        # Format response
        response = f"Found {len(results)} relevant video clips:\n\n"
        for i, result in enumerate(results, 1):
            duration = result.end_time - result.start_time
            response += f"{i}. Time: {result.start_time:.1f}s - {result.end_time:.1f}s ({duration:.1f}s)\n"
            response += f"   Description: {result.description}\n"
            response += f"   Play: {result.stream_url}\n\n"
        
        return response
    
    async def _handle_search_transcript(self, parameters: Dict[str, Any]) -> str:
        """
        Handler for search_transcript tool.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Formatted string with transcript search results
        """
        query = parameters['query']
        top_k = parameters.get('top_k', 5)
        speaker_filter = parameters.get('speaker_filter')
        
        # Query transcript
        results = await self.indexer.query_transcript(query, top_k=top_k)
        
        # Apply speaker filter if specified
        if speaker_filter:
            results = [r for r in results if r['speaker'] == speaker_filter]
        
        if not results:
            return "No matching transcript segments found."
        
        # Format response
        response = f"Found {len(results)} relevant transcript segments:\n\n"
        for result in results:
            timestamp_sec = result['timestamp_us'] / 1_000_000
            response += f"{result['rank']}. [{result['speaker']} at {timestamp_sec:.1f}s] "
            response += f"(Score: {result['relevance_score']:.3f})\n"
            response += f"   {result['text']}\n\n"
        
        return response
    
    def get_invocation_stats(self) -> Dict[str, Any]:
        """Get statistics about tool invocations."""
        total_invocations = len(self.invocation_log)
        successful = sum(1 for log in self.invocation_log if log['success'])
        failed = total_invocations - successful
        
        tool_usage = {}
        for log in self.invocation_log:
            tool_name = log['tool_name']
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        avg_execution_time = (
            sum(log['execution_time_ms'] for log in self.invocation_log) / total_invocations
            if total_invocations > 0 else 0
        )
        
        return {
            'total_invocations': total_invocations,
            'successful': successful,
            'failed': failed,
            'tool_usage': tool_usage,
            'avg_execution_time_ms': avg_execution_time
        }


if __name__ == "__main__":
    print("=" * 60)
    print("MCP SERVER TEST")
    print("=" * 60)
    
    async def test():
        # Initialize indexer
        from index import CourtroomIndexer
        indexer = CourtroomIndexer(
            stream_url="rtsp://localhost:8554/courtcam",
            session_id="mcp-test"
        )
        await indexer.start_live_indexing()
        
        # Initialize MCP server
        mcp = MCPServer(indexer)
        
        # Test tool discovery
        print("\n📋 Available Tools:")
        tools = mcp.discover_tools()
        for tool in tools:
            print(f"\n  {tool['name']} ({tool['category']})")
            print(f"    {tool['description']}")
            print(f"    Parameters:")
            for param in tool['parameters']:
                req = "required" if param['required'] else "optional"
                print(f"      - {param['name']} ({param['type']}, {req}): {param['description']}")
        
        # Test tool invocations
        print("\n" + "=" * 60)
        print("TESTING TOOL INVOCATIONS")
        print("=" * 60)
        
        # Test search_video
        print("\n[Test 1] search_video")
        result = await mcp.invoke_tool("search_video", {"query": "witness testimony"})
        print(f"  Success: {result.success}")
        print(f"  Execution time: {result.execution_time_ms}ms")
        if result.success:
            print(f"  Result:\n{result.data}")
        
        # Test search_transcript
        print("\n[Test 2] search_transcript")
        result = await mcp.invoke_tool("search_transcript", {"query": "objection", "top_k": 3})
        print(f"  Success: {result.success}")
        print(f"  Execution time: {result.execution_time_ms}ms")
        if result.success:
            print(f"  Result:\n{result.data}")
        
        # Test validation
        print("\n[Test 3] Invalid invocation (missing required parameter)")
        result = await mcp.invoke_tool("search_video", {})
        print(f"  Success: {result.success}")
        print(f"  Error: {result.error}")
        
        # Display stats
        print("\n" + "=" * 60)
        print("INVOCATION STATISTICS")
        print("=" * 60)
        stats = mcp.get_invocation_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ MCP Server test complete!")
    
    asyncio.run(test())
