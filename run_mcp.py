#!/usr/bin/env python3
"""
Run the ESP BOM MCP Server

Usage:
    python run_mcp.py              # Run with stdio transport (default)
    python run_mcp.py --port 8080  # Run with StreamableHttp transport on port 8080
    python run_mcp.py --port 3001  # Run on port 3001 for MCP App wrapper
"""

import argparse
from starlette.middleware import Middleware
from mcp_server import mcp
from version import APP_VERSION


class VersionHeaderMiddleware:
    """Starlette ASGI middleware that injects X-App-Version on every HTTP response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        async def send_with_version(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-app-version", APP_VERSION.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_version)


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
        # Run MCP server with StreamableHttp transport and version header middleware
        mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port, middleware=[Middleware(VersionHeaderMiddleware)])
    else:
        # Run with stdio transport (default)
        mcp.run()


if __name__ == "__main__":
    main()
