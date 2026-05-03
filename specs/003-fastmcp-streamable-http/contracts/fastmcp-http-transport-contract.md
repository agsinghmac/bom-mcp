# Contract: FastMCP Native Streamable-HTTP Transport

## Scope

Defines the externally visible HTTP interface of the ESP BOM MCP server after migration to FastMCP's native `streamable-http` transport. Replaces the hand-rolled Flask MCP layer in `http_server.py`.

---

## 1. MCP Protocol Endpoint

**URI**: `POST /mcp` (primary), `GET /mcp` (capability discovery per MCP spec)  
**Transport**: MCP Streamable-HTTP (FastMCP native)

### Contract

- Implements the MCP 2024-11-05 protocol specification.
- Accepts and responds to all standard JSON-RPC 2.0 MCP methods:
  - `initialize` — handshake; `serverInfo.version` MUST reflect `APP_VERSION`.
  - `tools/list` — returns all tools registered in `mcp_server.py`.
  - `tools/call` — invokes a registered tool by name with arguments.
  - `resources/list` — returns `skill://index` and all `skill://<filename>` resources.
  - `resources/read` — returns markdown content for a skill resource URI.
  - `notifications/initialized` — acknowledged without response body.
- All responses include `X-App-Version: <sha>` header (via ASGI middleware).

### Non-Regression Guarantee

All tools and resources previously accessible via `http_server.py`'s hand-rolled MCP layer MUST be accessible via this endpoint with identical semantics.

---

## 2. Health Check Endpoint

**URI**: `GET /health`, `GET /api/health`  
**Auth**: None  
**Response**:
```json
{ "status": "healthy", "version": "<APP_VERSION>" }
```
- Status: `200 OK`
- `Content-Type: application/json`
- `X-App-Version: <sha>`

### Contract

- MUST return `200` within 2 seconds of container startup.
- `version` field MUST match `X-App-Version` header value.
- Both paths (`/health` and `/api/health`) MUST be equivalent and always return `200` when the server is running.

---

## 3. Version Endpoint

**URI**: `GET /version`, `GET /api/version`  
**Auth**: None  
**Response**:
```json
{ "version": "<APP_VERSION>" }
```
- Status: `200 OK`
- `X-App-Version: <sha>`

### Contract

- `version` value is resolved from `GIT_SHA` → `APP_VERSION` → `K_REVISION` → git → `"unknown"` (in that precedence order).
- `"unknown"` is a valid but degraded state when no version source is available.

---

## 4. Tool REST Proxy Endpoint

**URI**: `GET /tool/{tool_name}`, `POST /tool/{tool_name}`  
**Auth**: None  
**Consumers**: `mcp_app/server.ts` (Node MCP App UI layer)

### Contract

- Accepts tool name as path parameter.
- Accepts arguments via query string (GET) or JSON body (POST).
- Returns the raw JSON result of the corresponding database operation.
- Unknown tool names: `404 {"error": "Unknown tool: <name>"}`.
- Runtime errors: `500 {"error": "<message>"}`.
- `X-App-Version: <sha>` present on all responses.

### Supported Tools

All tools registered in `mcp_server.py` that were previously proxied by `http_server.py` MUST remain accessible via this endpoint:

- ESP: `list_esps`, `get_esp`, `get_esp_bom`, `get_bom_summary`, `get_esps_by_series`, `create_esp`, `delete_esp`
- Parts: `list_parts`, `get_part`, `search_parts`, `get_parts_by_category`, `get_critical_parts`, `get_part_assemblies`, `create_part`, `update_part`, `delete_part`
- Assemblies: `list_assemblies`, `get_assembly`, `get_assembly_esps`, `create_assembly`, `delete_assembly`, `add_part_to_assembly`, `remove_part_from_assembly`, `update_assembly_part_quantity`
- Stats: `get_stats`, `view_dashboard`, `view_esp_catalogue`, `view_esp_bom`, `manage_parts`, `manage_assemblies`

---

## 5. X-App-Version Header Contract

**Header**: `X-App-Version: <sha-or-revision>`  
**Scope**: ALL HTTP responses from the server.

### Contract

- Present on every response (MCP protocol, health, version, tool proxy, error responses).
- Value is non-`unknown` when `GIT_SHA` or `K_REVISION` environment variable is set.
- Value truncated to max 32 characters.

---

## 6. Removed Endpoints (Post-Migration)

The following endpoints previously served by `http_server.py` are **removed** and will no longer exist:

| Removed endpoint | Reason |
|-----------------|--------|
| `GET/POST /mcp` (Flask hand-rolled) | Replaced by FastMCP native `/mcp` |
| SSE stub at `/mcp` (GET) | Replaced by FastMCP protocol compliance |
| HTML resource generators (`resources/read` returning `text/html;profile=mcp-app`) | Out of scope; Node MCP App UI uses `/tool/` proxy, not HTML resource reads |

---

## 7. Compatibility and Non-Regression

1. MCP clients previously connecting to `http_server.py`'s `/mcp` endpoint MUST be able to connect to FastMCP's `/mcp` with no configuration change.
2. `mcp_app/server.ts` calling `/tool/{tool_name}` MUST continue to work without modification.
3. Cloud Run health check probe at `/health` or `/api/health` MUST continue to return `200`.
4. `curl -I <url>/api/health` MUST return `X-App-Version` header with non-`unknown` value when `GIT_SHA` is set.
