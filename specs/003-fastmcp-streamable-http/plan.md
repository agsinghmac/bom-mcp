# Implementation Plan: FastMCP Native Streamable-HTTP Transport

**Branch**: `003-fastmcp-streamable-http` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/003-fastmcp-streamable-http/spec.md`

## Summary

Replace the hand-rolled Flask MCP JSON-RPC layer in `http_server.py` with FastMCP's native `streamable-http` transport. Add health, version, and tool proxy routes as FastMCP custom routes. Add `X-App-Version` ASGI middleware. Update `Dockerfile` to use `run_mcp.py` as entry point. Delete all MCP protocol code from `http_server.py`.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastMCP 3.2.4 (installed; `requirements.txt` under-pinned at `>=0.2.0` — fix required), Flask (retained for `api.py` only), Starlette + Uvicorn (transitive via FastMCP)  
**Storage**: SQLite unchanged  
**Target Platform**: Google Cloud Run (Linux container, port 8080), local dev (stdio or HTTP)  
**Project Type**: Python MCP server — transport/wiring refactor only  
**Performance Goals**: No change; FastMCP native transport is faster than hand-rolled Flask for MCP protocol  
**Constraints**: Zero-Testing Policy (no unit tests); no new external dependencies; Node MCP App must not break  
**Scale/Scope**: Single-file server refactor; ~400 lines removed from `http_server.py`; ~80 lines added to `mcp_server.py` + `run_mcp.py`

## Constitution Check

- **I. Clean Code First**: PASS — removes hand-rolled JSON-RPC; `@mcp.custom_route()` is declarative and self-documenting.
- **II. Simple Design & Minimal Dependencies**: PASS — no new dependencies; FastMCP's own Starlette/uvicorn stack is reused.
- **III. Zero-Testing Policy**: PASS — validation is manual per [quickstart.md](./quickstart.md).
- **IV. Tech Stack Lock**: PASS — Python + FastMCP; Flask retained only for `api.py`.

Post-Design Re-check: PASS — research and design artifacts introduce no violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-fastmcp-streamable-http/
├── plan.md                    ← this file
├── research.md                ← 7 resolved design decisions
├── data-model.md              ← runtime entities and contracts
├── quickstart.md              ← 13-step manual validation checklist
└── contracts/
    └── fastmcp-http-transport-contract.md
```

### Source Code Changes

```text
mcp_server.py          ← ADD: @mcp.custom_route for health, version, tool proxy
run_mcp.py             ← ADD: VersionHeaderMiddleware; pass middleware= to mcp.run()
http_server.py         ← REMOVE: all MCP protocol code; DELETE file or leave empty
Dockerfile             ← UPDATE: CMD + COPY list
requirements.txt       ← UPDATE: fastmcp>=3.2.4
version.py             ← no change (already correct)
skill_resource_manager.py ← no change
.skills/               ← no change
```

## Phase 0: Research Decisions Applied

1. **Health/version routes** → `@mcp.custom_route("/health", ...)`, `@mcp.custom_route("/version", ...)` in `mcp_server.py`. Both `/health` and `/api/health` (and `/version`/`/api/version`) registered as separate routes.
2. **X-App-Version header** → `VersionHeaderMiddleware` Starlette ASGI class in `run_mcp.py`; passed via `middleware=[VersionHeaderMiddleware]` to `mcp.run()`.
3. **Node MCP App `/tool/<name>` proxy** → `@mcp.custom_route("/tool/{tool_name}", methods=["GET", "POST"])` in `mcp_server.py`; uses `ESPDatabase` directly (same pattern as other tools).
4. **`http_server.py` disposal** → Delete after routes migrated. Dockerfile stops referencing it.
5. **Dockerfile** → `CMD ["python", "run_mcp.py", "--port", "8080"]`; expand `COPY` to include `skill_resource_manager.py`, `.skills/`, `version.py`.
6. **Flask** → Retained in `requirements.txt` for `api.py`; no change needed.
7. **fastmcp pin** → Update `requirements.txt` to `fastmcp>=3.2.4`.

## Phase 1: Design Output Mapping

1. Runtime entities captured in [data-model.md](./data-model.md).
2. Full HTTP interface contract in [contracts/fastmcp-http-transport-contract.md](./contracts/fastmcp-http-transport-contract.md).
3. Manual validation steps in [quickstart.md](./quickstart.md).
4. Agent context marker updated in [.github/copilot-instructions.md](../../.github/copilot-instructions.md) to this plan.

## Phase 2 Preview (for /speckit.tasks)

1. Add `@mcp.custom_route` handlers for `/health`, `/api/health`, `/version`, `/api/version` in `mcp_server.py`.
2. Implement `VersionHeaderMiddleware` in `run_mcp.py` and pass via `mcp.run()`.
3. Add `@mcp.custom_route("/tool/{tool_name}", ...)` REST proxy in `mcp_server.py` with full tool dispatch map.
4. Update `requirements.txt`: pin `fastmcp>=3.2.4`.
5. Update `Dockerfile`: fix `COPY` list and change `CMD`.
6. Delete MCP protocol code from `http_server.py` (JSON-RPC framing, tool maps, SSE stub, HTML generators, `/mcp` route). Delete file if empty.
7. Manually validate all 13 checklist items in [quickstart.md](./quickstart.md).
8. Re-check non-skill MCP tool regressions.

## Complexity Tracking

No constitution violations. No complexity justifications required.

## Implementation Summary

*To be filled after /speckit.implement completes.*
