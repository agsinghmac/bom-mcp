# Data Model: FastMCP Native Streamable-HTTP Transport Migration

## Overview

This feature does not introduce new persistent data entities. All changes are in the transport and server wiring layer. The entities below represent the runtime and configuration objects whose structure changes as a result of this migration.

---

## Entity: ServerEntryPoint

- **Description**: The runtime process configuration for the deployed server. Changes from `http_server.py` to `run_mcp.py`.
- **Fields**:
  - `script` (string, required): Python entry point script. After migration: `run_mcp.py`.
  - `transport` (enum, required): `streamable-http` for HTTP deployments, `stdio` for local/Claude Desktop.
  - `host` (string, required): Bind host. `0.0.0.0` for container deployments.
  - `port` (integer, required): Bind port. `8080` for Cloud Run.
  - `middleware` (list\<ASGIMiddleware\>, optional): Starlette middleware stack applied to all HTTP responses.
- **Validation**:
  - `script` must be `run_mcp.py` in Docker/Cloud Run deployments.
  - `transport` must be `streamable-http` when `port` is set.

---

## Entity: VersionHeaderMiddleware

- **Description**: ASGI middleware that injects `X-App-Version` header into every HTTP response using `APP_VERSION` from `version.py`.
- **Fields**:
  - `app_version` (string, required): Resolved at startup from `version.APP_VERSION`.
  - `header_name` (string, constant): `X-App-Version`.
- **Behavior**:
  - Intercepts every response passing through the ASGI stack.
  - Sets `X-App-Version: <sha>` unconditionally.
  - Transparent to all other response properties.
- **Validation**:
  - `app_version` may be `unknown` if no SHA/revision env var is set; this is a valid but degraded state.

---

## Entity: HealthResponse

- **Description**: Response body for `/health` and `/api/health` endpoints.
- **Fields**:
  - `status` (string, required): Fixed value `"healthy"`.
  - `version` (string, required): Current `APP_VERSION`.
- **HTTP contract**:
  - Status: `200 OK`
  - `Content-Type: application/json`
  - `X-App-Version: <sha>` (injected by middleware)

---

## Entity: VersionResponse

- **Description**: Response body for `/version` and `/api/version` endpoints.
- **Fields**:
  - `version` (string, required): Current `APP_VERSION`.
- **HTTP contract**:
  - Status: `200 OK`
  - `Content-Type: application/json`
  - `X-App-Version: <sha>` (injected by middleware)

---

## Entity: ToolProxyRequest

- **Description**: Incoming REST request to `/tool/{tool_name}` from the Node MCP App (`mcp_app/server.ts`).
- **Fields**:
  - `tool_name` (string, required): One of the registered ESP/BOM tool names (e.g., `list_esps`, `get_part`).
  - `args` (map\<string, string\>, optional): Tool arguments from query parameters (GET) or JSON body (POST).
- **Validation**:
  - `tool_name` must match a known tool in the dispatch map.
  - Unknown tool names return `{"error": "Unknown tool: <name>"}` with status 404.

---

## Entity: ToolProxyResponse

- **Description**: Response body returned by `/tool/{tool_name}` to the Node MCP App.
- **Fields**:
  - On success: the raw JSON result of the database operation (list, dict, or scalar).
  - On error: `{"error": "<message>"}` with status 4xx/5xx.
- **HTTP contract**:
  - `Content-Type: application/json`
  - `X-App-Version: <sha>` (injected by middleware)

---

## Entity: DockerImageConfig

- **Description**: Container build and runtime configuration for the Cloud Run deployment.
- **Fields**:
  - `base_image` (string, required): `python:3.11-slim`
  - `build_args` (map\<string, string\>): `GIT_SHA` → git commit short SHA.
  - `env_vars` (map\<string, string\>): `GIT_SHA` baked from build arg.
  - `copied_files` (list\<string\>): All Python source files and `.skills/` directory required by `mcp_server.py` and `run_mcp.py`.
  - `cmd` (list\<string\>, required): `["python", "run_mcp.py", "--port", "8080"]`
  - `expose_port` (integer, required): `8080`
- **Validation**:
  - `copied_files` MUST include: `esp_db.py`, `mcp_server.py`, `run_mcp.py`, `skill_resource_manager.py`, `version.py`, `.skills/`.
  - `http_server.py` MUST NOT be the `CMD` target.
  - `api.py` and `http_server.py` may be omitted from the image if no longer needed at runtime.
