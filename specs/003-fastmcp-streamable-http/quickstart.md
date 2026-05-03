# Quickstart: Manual Validation for FastMCP Native Streamable-HTTP Migration

## Goal

Confirm that the FastMCP native `streamable-http` transport correctly serves all MCP tools and resources, that health/version endpoints work, that the Node MCP App tool proxy is functional, and that `http_server.py` MCP code is gone.

## Prerequisites

- Python dependencies installed from `requirements.txt` (with `fastmcp>=3.2.4`)
- `.skills/esp_selection_bom_readiness.md` present in `.skills/`
- `GIT_SHA` set in environment for version validation (or accept `K_REVISION` in Cloud Run)

## Validation Steps

### 1. Start the server via FastMCP native transport

```bash
python run_mcp.py --port 8080
```

Expected: Server starts with no Flask import errors; FastMCP banner visible.

---

### 2. Health check

```bash
curl -I http://localhost:8080/health
curl -I http://localhost:8080/api/health
```

Expected:
- `200 OK`
- `X-App-Version: <sha>` header present (not `unknown` if `GIT_SHA` is set)
- Body: `{"status": "healthy", "version": "<sha>"}`

---

### 3. Version endpoint

```bash
curl http://localhost:8080/version
curl http://localhost:8080/api/version
```

Expected:
- `200 OK`
- `{"version": "<sha>"}`
- `X-App-Version` header matches body version

---

### 4. MCP initialize handshake

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

Expected:
- `200 OK`
- Response includes `serverInfo.version` matching `APP_VERSION`
- `X-App-Version` header present

---

### 5. MCP tools/list — verify all tools present

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

Expected:
- All tools from `mcp_server.py` present in the response (min: `list_esps`, `get_esp`, `get_esp_bom`, `get_bom_summary`, `list_parts`, `get_part`, `get_stats`)
- No duplicate or missing tools vs. the previous `http_server.py` tool list

---

### 6. MCP tools/call — call a representative tool

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_esps","arguments":{}}}'
```

Expected: `200 OK`, `result.content` contains ESP list (10 entries).

---

### 7. MCP resources/list — verify skill resources

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"resources/list","params":{}}'
```

Expected: `skill://index` and `skill://esp_selection_bom_readiness` both present.

---

### 8. Tool REST proxy — verify Node MCP App compatibility

```bash
curl http://localhost:8080/tool/list_esps
curl http://localhost:8080/tool/get_stats
curl "http://localhost:8080/tool/get_part?part_number=ESP-MTR-001"
```

Expected:
- `200 OK` with JSON body (list of ESPs, stats dict, part detail respectively)
- `X-App-Version` header present on all

---

### 9. Verify `http_server.py` has no MCP code

Inspect the file (or confirm it is deleted):

- No `/mcp` route
- No `jsonrpc`, `tools/list`, `tools/call`, `resources/list` method handling
- No `get_dashboard_html()`, `get_esp_catalogue_html()`, etc.

---

### 10. Verify Dockerfile

```bash
cat Dockerfile
```

Expected:
- `CMD` is `["python", "run_mcp.py", "--port", "8080"]`
- `COPY` includes `skill_resource_manager.py`, `.skills/`, `version.py`
- `http_server.py` is absent from `CMD` and ideally from `COPY`

---

## Cloud Run Verification (Post-Deploy)

```bash
$SHA = git rev-parse --short HEAD
gcloud run deploy bom-mcp --source . --region asia-south1 --allow-unauthenticated --set-env-vars GIT_SHA=$SHA

# Then verify
curl -I https://bom-mcp-951509216799.asia-south1.run.app/health
curl https://bom-mcp-951509216799.asia-south1.run.app/version
curl -X POST https://bom-mcp-951509216799.asia-south1.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Expected:
- `/health` → `200 OK`, `X-App-Version: <sha>` (non-unknown)
- `/version` → `{"version": "<sha>"}`
- `/mcp tools/list` → all tools listed

## Manual Validation Log

- [ ] Server starts on port 8080 via `run_mcp.py` without errors
- [ ] `/health` and `/api/health` return 200 with version
- [ ] `/version` and `/api/version` return correct SHA
- [ ] `X-App-Version` header present and non-unknown
- [ ] MCP `initialize` returns `serverInfo.version` = `APP_VERSION`
- [ ] `tools/list` returns all expected tools
- [ ] `tools/call list_esps` returns 10 ESP records
- [ ] `resources/list` returns `skill://index` and `skill://esp_selection_bom_readiness`
- [ ] `/tool/list_esps` REST proxy returns correct JSON
- [ ] `/tool/get_stats` REST proxy returns stats dict
- [ ] `http_server.py` contains no MCP protocol code
- [ ] `Dockerfile` CMD is `run_mcp.py --port 8080`
- [ ] Cloud Run deployment returns non-unknown `x-app-version`
