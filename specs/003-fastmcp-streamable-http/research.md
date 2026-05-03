# Research: FastMCP Native Streamable-HTTP Transport Migration

## Decision 1: Health and Version Route Strategy

- **Decision**: Register `/health`, `/api/health`, `/version`, `/api/version` using FastMCP's built-in `@mcp.custom_route()` decorator directly on the `FastMCP` instance in `mcp_server.py`.
- **Rationale**: FastMCP 3.2.4 exposes `@server.custom_route(path, methods)` as the supported public API for adding non-MCP HTTP endpoints to the same process and port. Routes registered this way are automatically included in the Starlette ASGI app built by `.http_app` and served by uvicorn. No additional framework or process is needed.
- **Alternatives considered**:
  - Keep Flask running for health routes on a separate port: rejected — two processes in one container, adds complexity, doesn't match Cloud Run single-port model.
  - Wrap the FastMCP ASGI app manually with a Starlette Router: rejected — `@mcp.custom_route()` is the cleaner and officially supported path.

## Decision 2: X-App-Version Response Header Strategy

- **Decision**: Implement a Starlette ASGI middleware class in `run_mcp.py` that injects `X-App-Version` into every HTTP response, passed via the `middleware=` parameter of `mcp.run()`.
- **Rationale**: FastMCP 3.2.4's `run_http_async()` accepts a `middleware: list[ASGIMiddleware]` parameter that wraps the entire Starlette app. This ensures the header appears on ALL responses (MCP protocol responses, custom route responses, error responses) without per-route repetition.
- **Alternatives considered**:
  - Set header manually in each `@mcp.custom_route` handler: rejected — misses MCP protocol responses from FastMCP's own handlers.
  - Use FastMCP's undocumented `_additional_http_routes` directly: rejected — internal API, prefer `@mcp.custom_route()`.

## Decision 3: Node MCP App REST Proxy (`/tool/<name>`) Strategy

- **Decision**: Re-implement the `/tool/{tool_name}` REST proxy as a `@mcp.custom_route` in `mcp_server.py`, using the existing `ESPDatabase` directly (same pattern as other tools).
- **Rationale**: `mcp_app/server.ts` calls `PYTHON_SERVER_URL/tool/<toolName>` — removing these routes without replacement would break the Node MCP App UI. Registering them as custom routes on the FastMCP server eliminates the need for a separate Flask process while preserving backward compatibility.
- **Alternatives considered**:
  - Keep a minimal `http_server.py` running in Docker alongside `run_mcp.py`: rejected — two processes, two ports, docker-compose required for single Cloud Run deployment.
  - Rewrite Node MCP App to use MCP protocol directly: rejected — out of scope for this feature.
  - Delete the proxy routes and accept Node MCP App breakage: rejected — constitutes a regression.

## Decision 4: Disposal of `http_server.py`

- **Decision**: Delete `http_server.py` entirely after all routes (health, version, tool proxy) are migrated to FastMCP custom routes.
- **Rationale**: `http_server.py` contains ~400 lines of hand-rolled JSON-RPC framing, manual tool dispatch maps, a non-functional SSE stub, and HTML generators. None of these serve a purpose once the FastMCP native transport is the entry point. Complete deletion removes the maintenance liability and the source of protocol drift.
- **Alternatives considered**:
  - Keep `http_server.py` as a stub: rejected — even empty stubs add confusion about what is authoritative.
  - Keep `http_server.py` for local dev: rejected — `run_mcp.py --port 8080` works locally identically to production.

## Decision 5: Dockerfile Update Strategy

- **Decision**: Update `Dockerfile` to (a) expand `COPY` to include `skill_resource_manager.py`, `.skills/` directory, `version.py`, and `run_mcp.py` as the authoritative files, and (b) change `CMD` to `["python", "run_mcp.py", "--port", "8080"]`.
- **Rationale**: The current Dockerfile `COPY` list was tailored to `http_server.py`'s imports and omits `skill_resource_manager.py`, `.skills/`, and other files required by `mcp_server.py`. The `CMD` must point to `run_mcp.py`.
- **Alternatives considered**:
  - Use `COPY . .` to copy everything: acceptable but less precise; may copy dev artifacts. Decided to keep explicit list for clarity.

## Decision 6: `requirements.txt` Update

- **Decision**: Keep `flask>=2.0.0` in `requirements.txt` — it is still used by `api.py` (the optional REST API server). Remove it from Docker image-level concerns only.
- **Rationale**: Flask is a legitimate dependency for local REST API usage (`api.py`). It is not used by the Cloud Run deployment path, but removing it from `requirements.txt` would break `api.py`. No change needed.
- **Alternatives considered**:
  - Remove Flask: rejected — breaks `api.py` which is part of the declared architecture.
  - Split requirements into `requirements.txt` + `requirements-dev.txt`: rejected — over-engineering for current scope.

## Decision 7: FastMCP Version in requirements.txt

- **Decision**: Pin `fastmcp>=3.2.4` in `requirements.txt` to reflect the actual installed version and to ensure `@mcp.custom_route()` (added in 3.x) is always available.
- **Rationale**: The current `requirements.txt` specifies `fastmcp>=0.2.0` which is dangerously under-pinned — it could resolve to a version lacking `custom_route`, `_additional_http_routes`, and the `middleware=` parameter on `run_http_async`. The installed version is 3.2.4.
- **Alternatives considered**:
  - Pin exactly to `fastmcp==3.2.4`: acceptable but overly strict; `>=3.2.4` permits patch/minor upgrades.
