# Feature Specification: FastMCP Native Streamable-HTTP Transport

**Feature Branch**: `003-fastmcp-streamable-http`
**Created**: 2026-05-04
**Status**: Draft
**Input**: User description: "Switch to FastMCP native streamable-http instead of current use of current 'hand-implementing' MCP JSON-RPC in Flask"

## User Scenarios & Manual Verification *(mandatory)*

### User Story 1 - MCP Clients Connect via Native Streamable-HTTP (Priority: P1)

As an MCP client (Claude Desktop, Claude.ai, or any compliant agent runtime), I need to connect to the ESP BOM server over HTTP using the standard MCP Streamable-HTTP transport so I can invoke all tools and read all resources without any hand-rolled protocol shim in between.

**Why this priority**: This is the core migration goal. Without it, all other stories have nothing to build on. The FastMCP native transport is the correct protocol carrier and removes a large layer of custom code that duplicates FastMCP's own implementation.

**Independent Verification**: Can be fully verified by pointing any MCP client at the deployed URL and calling at least `list_esps`, `get_esp_bom`, and `skill://index` — all should work without needing `http_server.py` to be running.

**Acceptance Scenarios**:

1. **Given** the server is started with `python run_mcp.py --port 8080`, **When** an MCP client sends an `initialize` request to `/mcp`, **Then** the server responds with a valid MCP protocol handshake and server info including the current `APP_VERSION`.
2. **Given** a connected MCP client, **When** it calls `tools/list`, **Then** all tools registered in `mcp_server.py` are returned — no tools are missing compared to the current `http_server.py` tool list.
3. **Given** a connected MCP client, **When** it calls `resources/list`, **Then** `skill://index` and all discovered `skill://<filename>` resources are returned.
4. **Given** the server is deployed to Cloud Run via `run_mcp.py`, **When** `curl /api/health` or `curl /version` is called, **Then** the response includes `APP_VERSION` (not `unknown`).

---

### User Story 2 - Remove Hand-Rolled Flask MCP Layer (Priority: P2)

As a maintainer, I need the hand-implemented JSON-RPC/MCP layer in `http_server.py` to be retired so there is a single authoritative MCP protocol path and no duplicate tool dispatch code to keep in sync.

**Why this priority**: The Flask `http_server.py` is a large maintenance liability — it manually re-implements tool routing, JSON-RPC framing, `initialize`/`tools/list`/`tools/call`/`resources/list`/`resources/read` methods, and an SSE stub that does not actually implement SSE. Removing it eliminates drift risk and reduces codebase surface area by ~400 lines.

**Independent Verification**: Can be verified by confirming `http_server.py` is removed (or reduced to a health/version-only shim) and that Cloud Run Dockerfile points to `run_mcp.py` instead.

**Acceptance Scenarios**:

1. **Given** the refactored deployment, **When** the repository is inspected, **Then** `http_server.py` no longer contains any `/mcp` endpoint, JSON-RPC framing, tool dispatch maps, or HTML resource generators.
2. **Given** the Dockerfile used by Cloud Run, **When** it is read, **Then** `CMD` points to `python run_mcp.py --port 8080` and not to `http_server.py`.

---

### User Story 3 - Health and Version Endpoints Preserved (Priority: P3)

As an operator monitoring Cloud Run, I need `/health`, `/api/health`, and `/version` endpoints to remain accessible after the migration so I can confirm a healthy deployment and verify the deployed git SHA.

**Why this priority**: These endpoints are already in use for monitoring and debug verification. They must survive the migration regardless of which server handles them.

**Independent Verification**: Can be verified with `curl -I https://<cloudrun-url>/health` and `curl https://<cloudrun-url>/version` returning 200 with correct `X-App-Version` header.

**Acceptance Scenarios**:

1. **Given** the FastMCP-native deployment, **When** `GET /health` or `GET /api/health` is called, **Then** the response is `200 OK` with `{"status": "healthy", "version": "<sha>"}` and `X-App-Version` response header.
2. **Given** the server is deployed with `GIT_SHA` set in environment, **When** `GET /version` is called, **Then** the response contains the exact SHA and `x-app-version` header is not `unknown`.

---

### Edge Cases

- What happens if a request arrives at `/mcp` before startup refresh of skill resources completes?
- How does the server behave when FastMCP's streamable-http transport receives a non-MCP HTTP request (e.g., a browser `GET /mcp`)?
- What happens if `GIT_SHA` is not set and `K_REVISION` is also absent at runtime (version stays `unknown`)?
- How does Cloud Run handle long-lived SSE/streaming connections from MCP clients — does the default request timeout need adjusting?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST serve all MCP tool and resource operations exclusively through FastMCP's native `streamable-http` transport.
- **FR-002**: System MUST NOT maintain a separate hand-implemented JSON-RPC MCP layer in Flask after migration.
- **FR-003**: `run_mcp.py` MUST be the single entry point for all HTTP-based MCP communication in production and Cloud Run deployments.
- **FR-004**: All tools currently registered in `mcp_server.py` MUST remain fully accessible to MCP clients after migration.
- **FR-005**: All skill resources (`skill://index`, `skill://<filename>`) MUST remain discoverable and readable via the FastMCP transport.
- **FR-006**: The deployed Docker image MUST start `run_mcp.py --port 8080` as its entry point, not `http_server.py`.
- **FR-007**: Health check endpoint (`/health` or `/api/health`) MUST return `200 OK` with version information after migration.
- **FR-008**: `X-App-Version` response header MUST be present with a non-`unknown` value when `GIT_SHA` or `K_REVISION` is available in the runtime environment.
- **FR-009**: `http_server.py` duplicate MCP protocol code (JSON-RPC framing, tool dispatch maps, `/mcp` route, SSE stub, HTML generators) MUST be removed or isolated to a minimal non-MCP helper if still needed for health checks.
- **FR-010**: The `Dockerfile` (Cloud Run) MUST include `skill_resource_manager.py`, `.skills/` content, and `version.py` in the image — not just the files listed for `http_server.py`.

### Key Entities

- **FastMCP Server** (`mcp_server.py`): Authoritative MCP server instance with all tool/resource registrations; now the only protocol entry point.
- **Entry Point** (`run_mcp.py`): The production startup script that selects stdio or streamable-http transport; becomes the Docker `CMD`.
- **Health Shim** (optional, simplified `http_server.py` or inline route in `run_mcp.py`): Lightweight `/health` and `/version` routes that satisfy Cloud Run health checks and monitoring without re-implementing MCP.
- **Dockerfile** (Cloud Run image): Container build config — must be updated to copy all required files and use `run_mcp.py` as entrypoint.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of MCP tool calls made by a connected MCP client succeed via the FastMCP native transport with no manual dispatch code in the path.
- **SC-002**: `http_server.py` reduces from ~400 lines to zero MCP-related lines (all JSON-RPC framing, tool maps, and protocol method handlers removed).
- **SC-003**: Cloud Run health check at `/health` returns 200 within 2 seconds of container startup.
- **SC-004**: `x-app-version` response header is non-`unknown` on every deployed revision where `GIT_SHA` or `K_REVISION` is set.
- **SC-005**: No regressions in existing tools: `list_esps`, `get_esp_bom`, `get_bom_summary`, `list_parts`, `get_stats`, and `skill://index` all respond correctly after migration.

## Assumptions

- FastMCP's `streamable-http` transport already works correctly for `mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)` — this is confirmed in `run_mcp.py`.
- Cloud Run can reach the FastMCP HTTP endpoint directly without a Node proxy layer between the client and the Python process.
- The MCP App Node.js server (`mcp_app/server.ts`) is a separate concern and is NOT being changed in this feature — it calls the Python server's `/tool/<name>` REST proxy routes, which may need to remain or be re-evaluated as a follow-on.
- Health check and version endpoints not provided natively by FastMCP will be handled by a minimal ASGI/WSGI middleware or an additional lightweight route registered on the same process.
- `GIT_SHA` will be injected as a build argument or environment variable during Cloud Run deployment.

## Technical Design

- Replace `http_server.py` as the Cloud Run entry point with `run_mcp.py --port 8080`.
- Register health and version routes directly on FastMCP's underlying ASGI app or via a simple middleware wrapper around the FastMCP app, so no separate Flask process is needed.
- Update the `Dockerfile` `COPY` and `CMD` to include all required files (`mcp_server.py`, `run_mcp.py`, `esp_db.py`, `skill_resource_manager.py`, `version.py`, `.skills/`) and launch `run_mcp.py`.
- Keep `http_server.py` as a minimal stub (or delete entirely if health routes can be added to the FastMCP app) to avoid breaking the Node MCP App proxy calls in the short term — scope this decision in planning.
- Preserve `X-App-Version` header injection through FastMCP middleware or startup configuration.

## Acceptance Criteria

1. MCP client successfully calls all tools and reads all resources through the FastMCP `streamable-http` transport at the deployed Cloud Run URL.
2. `http_server.py` contains no JSON-RPC framing, `/mcp` route, tool dispatch maps, HTML generators, or SSE stub code.
3. Cloud Run `Dockerfile` `CMD` is `python run_mcp.py --port 8080`.
4. `curl /health` and `curl /version` return 200 with correct version after deployment.
5. `x-app-version` header is present and non-`unknown` when `GIT_SHA` is injected at build/deploy time.
6. All baseline tool calls return expected results (no regressions).

## Implementation Tasks

1. Investigate how FastMCP's streamable-http transport exposes hooks for adding health/version middleware routes.
2. Add health and version endpoints to the FastMCP app or its ASGI wrapper in `run_mcp.py` or `mcp_server.py`.
3. Update the `Dockerfile` COPY list and CMD to use `run_mcp.py`.
4. Remove all MCP-protocol code from `http_server.py` (JSON-RPC, tool maps, SSE stub, HTML generators).
5. Verify Node MCP App proxy calls (`/tool/<name>`) are not broken — decide to keep minimal REST proxy in `http_server.py` or migrate those calls.
6. Run baseline MCP tool and resource validation against the FastMCP-only deployment.
