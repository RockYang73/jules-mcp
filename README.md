# Gemini CLI x Jules MCP Integration

This project provides a Model Context Protocol (MCP) server that seamlessly bridges Gemini CLI (using Gemini AI Pro) with the Google Jules cloud execution environment.

## Features

The MCP server exposes the following ADK-based Tools, allowing the Gemini LLM to autonomously orchestrate vibe coding and code reviews:

1. **`jules_create_task`**: Dispatches a codebase modification task to the Jules cloud sandbox.
2. **`jules_check_status`**: Provides asynchronous task status tracking (`PENDING`, `IN_PROGRESS`, `PR_READY`, `FAILED`) and live logs.
3. **`jules_get_result`**: Implements diff truncation and pagination to fit within the Gemini Context Window, returning the file structure and truncated modifications.
4. **`jules_apply_patch`**: A localized Tool that fetches the cloud-generated patch and seamlessly executes `git apply` against your local target directory, bridging the 20% gap of cloud-to-local synchronization.

## Setup & Dependencies

Make sure you are running Python 3.9+ and have Node.js/npx installed (if interacting with community NPM MCP servers, though this repository strictly uses Python ADK tools).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the MCP Server

Because this MCP server communicates via `stdio` (Standard Input/Output) to ensure a lightweight and highly secure execution environment, you do not launch it as a standalone HTTP server. Instead, configure your Gemini CLI (or any MCP-compatible client like Claude Desktop) to invoke this Python script:

```json
{
  "mcpServers": {
    "jules_mcp_server": {
      "command": "python",
      "args": ["/absolute/path/to/this/repo/main.py"],
      "env": {
        "JULES_API_TOKEN": "your-secure-token-here"
      }
    }
  }
}
```

## Agentic Workflows

This server supports advanced agent skills integration:
*   **Error Handling & Graceful Degradation:** When a task fails, structured error schemas (`error_code`, `suggested_action`) are returned so the LLM can auto-correct or ask for human intervention.
*   **Context Window Limits:** Diffs are paginated, preventing token overflow when Jules refactors massive codebases.
