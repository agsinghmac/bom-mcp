#!/usr/bin/env python3
"""
Run the ESP BOM MCP Server

Usage:
    python run_mcp.py              # Run with stdio transport (default)
    python run_mcp.py --port 8080  # Run with SSE transport on port 8080
"""

import argparse
from mcp_server import mcp


def main():
    parser = argparse.ArgumentParser(description="ESP BOM MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for SSE transport (default: stdio)",
    )
    args = parser.parse_args()

    if args.port:
        # Run HTTP with health endpoint using uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import JSONResponse
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        # Health check - respond to root path for Cloud Run
        async def health(request):
            return JSONResponse({"status": "healthy"})

        # Get the MCP HTTP app
        mcp_app = mcp.http_app()

        app = Starlette(
            routes=[
                Route("/", health, methods=["GET", "HEAD"]),
            ],
            middleware=[
                Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
            ],
        )

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        # Run with stdio transport (default)
        mcp.run()


if __name__ == "__main__":
    main()
