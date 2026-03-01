import asyncio
import json
import traceback

from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# Import our defined ADK FunctionTools
from src.adk_tools import all_adk_tools

app = Server("jules-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes to Gemini CLI."""
    mcp_tools = []
    for adk_tool in all_adk_tools:
        # Convert ADK definition to MCP format
        mcp_tools.append(adk_to_mcp_tool_type(adk_tool))
    return mcp_tools

@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]:
    """MCP handler to execute a tool call requested by Gemini CLI."""
    target_tool = None
    for tool in all_adk_tools:
        if tool.name == name:
            target_tool = tool
            break

    if not target_tool:
        error_text = json.dumps({
            "error_code": "TOOL_NOT_FOUND",
            "suggested_action": f"Tool '{name}' is not recognized by the Jules MCP Server."
        })
        return [mcp_types.TextContent(type="text", text=error_text)]

    try:
        # Execute the ADK tool asynchronously
        # For simplicity, pass None to tool_context as ADK uses it for inner LLM states
        response = await target_tool.run_async(args=arguments, tool_context=None)

        # Serialize dict to JSON string payload for MCP TextContent format
        response_text = json.dumps(response, indent=2)
        return [mcp_types.TextContent(type="text", text=response_text)]

    except Exception as e:
        error_info = {
            "error_code": "TOOL_EXECUTION_FAILED",
            "suggested_action": f"An unexpected error occurred during execution of {name}.",
            "details": str(e),
            "traceback": traceback.format_exc()
        }
        return [mcp_types.TextContent(type="text", text=json.dumps(error_info, indent=2))]

async def run_mcp_stdio_server():
    """Starts the Jules MCP Server using standard input/output streams."""
    # Use standard stdio interaction defined by modelcontextprotocol/sdk
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        pass
