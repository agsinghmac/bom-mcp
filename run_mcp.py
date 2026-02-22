#!/usr/bin/env python3
"""
Run the ESP BOM MCP Server

Usage:
    python run_mcp.py              # Run with stdio transport (default)
    python run_mcp.py --port 8080  # Run with StreamableHttp transport on port 8080
"""

import argparse
from mcp_server import mcp


def main():
    parser = argparse.ArgumentParser(description="ESP BOM MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for StreamableHttp transport (default: stdio)",
    )
    args = parser.parse_args()

    if args.port:
        # Run MCP server with StreamableHttp transport
        # Note: FastMCP's run() accepts transport, host, and port parameters
        mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port)
    else:
        # Run with stdio transport (default)
        mcp.run()


if __name__ == "__main__":
    main()
