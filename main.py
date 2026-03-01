import asyncio
from src.mcp_server import run_mcp_stdio_server

def main():
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
