# Tasks: FastMCP Native Streamable-HTTP Transport

**Input**: Design documents from `specs/003-fastmcp-streamable-http/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/fastmcp-http-transport-contract.md`, `quickstart.md`

**Tests**: FORBIDDEN — Per BOM-MCP Constitution (Principle III: Zero-Testing Policy), no unit, integration, or end-to-end test tasks are included.

**Organization**: Tasks are grouped by user story to allow independent implementation and manual verification.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies and configuration before any story implementation begins.

- [X] T001 Update fastmcp version pin from `>=0.2.0` to `>=3.2.4` in requirements.txt
- [X] T002 [P] Update Dockerfile COPY list to include `skill_resource_manager.py`, `version.py`, `.skills/` and remove `http_server.py` dependency in Dockerfile
- [X] T003 [P] Update Dockerfile CMD from `http_server.py` to `["python", "run_mcp.py", "--port", "8080"]` in Dockerfile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the `VersionHeaderMiddleware` and wire it into `run_mcp.py` before any story work. All stories depend on the version header working correctly.

**⚠️ CRITICAL**: No user story implementation starts before this phase is complete.

- [X] T004 Implement `VersionHeaderMiddleware` Starlette ASGI class in run_mcp.py that injects `X-App-Version` header on every response
- [X] T005 Pass `middleware=[VersionHeaderMiddleware]` to `mcp.run()` in run_mcp.py streamable-http path

**Checkpoint**: Version header middleware wired — all subsequent routes will emit `X-App-Version` automatically.

---

## Phase 3: User Story 1 — MCP Clients Connect via Native Streamable-HTTP (Priority: P1) 🎯 MVP

**Goal**: Confirm FastMCP native transport handles all MCP protocol operations — `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read` — without `http_server.py` in the path.

**Independent Test**: Start `python run_mcp.py --port 8080`, send `initialize` then `tools/list` via curl; all `mcp_server.py` tools must appear; call `list_esps` and `skill://index` resource; all must respond correctly.

### Implementation for User Story 1

- [X] T006 [US1] Verify `mcp_server.py` `mcp.run(transport="streamable-http", ...)` works end-to-end by starting server on port 8080 and manually calling `initialize` in mcp_server.py / run_mcp.py
- [X] T007 [US1] Confirm `tools/list` returns all tools registered in `mcp_server.py` (list_esps, get_esp, get_esp_bom, get_bom_summary, list_parts, get_part, search_parts, get_parts_by_category, get_critical_parts, list_assemblies, get_assembly, get_stats and all CRUD tools) — document any gap in run_mcp.py
- [X] T008 [US1] Confirm `resources/list` returns `skill://index` and `skill://esp_selection_bom_readiness` via FastMCP transport — no extra wiring needed since `mcp_server.py` already registers these

**Checkpoint**: User Story 1 is independently functional — MCP clients can connect and call all tools/resources via native transport.

---

## Phase 4: User Story 2 — Remove Hand-Rolled Flask MCP Layer (Priority: P2)

**Goal**: Retire all MCP protocol code from `http_server.py` and update `Dockerfile` entry point. Node MCP App `/tool/<name>` proxy must be preserved as a FastMCP custom route before removal.

**Independent Test**: Inspect `http_server.py` — zero lines of JSON-RPC framing, no `/mcp` route, no tool dispatch map, no HTML generators, no SSE stub. `Dockerfile` CMD is `run_mcp.py`.

### Implementation for User Story 2

- [X] T009 [US2] Add `@mcp.custom_route("/tool/{tool_name}", methods=["GET", "POST"])` handler in mcp_server.py with full tool dispatch map matching all tools previously in `http_server.py` tool_map
- [X] T010 [US2] Remove `/mcp` route, JSON-RPC framing (`jsonrpc_id`, method dispatch, `initialize`/`tools/list`/`tools/call`/`resources/list`/`resources/read` handlers) from http_server.py
- [X] T011 [US2] Remove SSE stub endpoint (`/mcp GET` streaming response) from http_server.py
- [X] T012 [US2] Remove HTML resource generators (`get_dashboard_html`, `get_esp_catalogue_html`, `get_esp_bom_html`, `get_parts_html`, `get_assemblies_html`) and `/resources/<resource_name>` route from http_server.py
- [X] T013 [US2] Remove duplicate tool dispatch `tool_map` in `/tool/<tool_name>` Flask route from http_server.py (now served by FastMCP custom route in T009)
- [X] T014 [P] [US2] Delete http_server.py entirely if empty after T010–T013, or confirm it contains only non-MCP code

**Checkpoint**: User Story 2 is independently functional — `http_server.py` has zero MCP protocol code; `Dockerfile` CMD is `run_mcp.py`.

---

## Phase 5: User Story 3 — Health and Version Endpoints Preserved (Priority: P3)

**Goal**: Register `/health`, `/api/health`, `/version`, `/api/version` as FastMCP custom routes so Cloud Run health checks and operator monitoring continue to work after `http_server.py` is removed.

**Independent Test**: `curl -I http://localhost:8080/health` → 200 + `X-App-Version: <sha>`. `curl http://localhost:8080/version` → `{"version":"<sha>"}`. Both `/health` and `/api/health` equivalent.

### Implementation for User Story 3

- [X] T015 [US3] Add `@mcp.custom_route("/health", methods=["GET"])` handler in mcp_server.py returning `{"status": "healthy", "version": APP_VERSION}`
- [X] T016 [US3] Add `@mcp.custom_route("/api/health", methods=["GET"])` alias in mcp_server.py pointing to same health response
- [X] T017 [US3] Add `@mcp.custom_route("/version", methods=["GET"])` handler in mcp_server.py returning `{"version": APP_VERSION}`
- [X] T018 [P] [US3] Add `@mcp.custom_route("/api/version", methods=["GET"])` alias in mcp_server.py pointing to same version response

**Checkpoint**: User Story 3 is independently functional — health and version endpoints return 200 with non-unknown version when `GIT_SHA` is set.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize Docker config, run manual validation checklist, record regression results.

- [X] T019 [P] Verify Dockerfile COPY list includes all required files for `mcp_server.py`: `esp_db.py`, `mcp_server.py`, `run_mcp.py`, `skill_resource_manager.py`, `version.py`, `.skills/` in Dockerfile
- [X] T020 Run manual validation checklist from specs/003-fastmcp-streamable-http/quickstart.md steps 1–10 and mark each item complete
- [X] T021 Record baseline tool regression results (list_esps, get_esp_bom, get_bom_summary, list_parts, get_stats, skill://index) in specs/003-fastmcp-streamable-http/quickstart.md
- [X] T022 [P] Update Implementation Summary section in specs/003-fastmcp-streamable-http/plan.md with what was done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 (fastmcp pin must be correct before running).
- **Phase 3 (US1)**: Depends on Phase 2 (middleware must be wired before verifying header).
- **Phase 4 (US2)**: Depends on Phase 3 (T009 custom route must exist before removing Flask proxy in T013).
- **Phase 5 (US3)**: Depends on Phase 2 (middleware wired); independent of US1/US2 implementation details.
- **Phase 6 (Polish)**: Depends on Phase 4 and 5 completion.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational middleware; verifies FastMCP native transport works.
- **US2 (P2)**: Depends on US1 (T009 tool proxy must be in place before removing Flask proxy).
- **US3 (P3)**: Depends on Foundational phase only; can be implemented in parallel with US1/US2 after T004–T005.

### Within Each User Story

- T009 (tool proxy) MUST complete before T013 (Flask proxy removal) within US2.
- T015–T018 (health/version routes) can all be implemented in parallel within US3.

### Parallel Opportunities

- T002 and T003 (Dockerfile updates) can run in parallel with each other.
- T010, T011, T012 (MCP code removal) can run in parallel after T009.
- T015, T016, T017, T018 (health/version routes) can all run in parallel.
- T019 (Dockerfile verification) can run in parallel with T020–T022.

---

## Parallel Example: Setup Phase

- T002 Update Dockerfile COPY list in Dockerfile
- T003 Update Dockerfile CMD in Dockerfile

---

## Parallel Example: User Story 2

- T010 Remove `/mcp` route and JSON-RPC handlers from http_server.py
- T011 Remove SSE stub from http_server.py
- T012 Remove HTML generators from http_server.py

---

## Parallel Example: User Story 3

- T015 Add `/health` custom route in mcp_server.py
- T016 Add `/api/health` alias in mcp_server.py
- T017 Add `/version` custom route in mcp_server.py
- T018 Add `/api/version` alias in mcp_server.py

---

## Implementation Strategy

### MVP First (User Stories 1 + Foundational Only)

1. Complete Phase 1 (setup).
2. Complete Phase 2 (middleware).
3. Complete Phase 3 (US1 — verify FastMCP native transport works).
4. Manually verify MCP tools/resources respond via `run_mcp.py --port 8080`.
5. Demo/validate MVP: native transport confirmed working.

### Incremental Delivery

1. Setup + Foundational → transport and middleware ready.
2. Deliver US1 (P1) → validate manually; confirm FastMCP native transport handles all tools/resources.
3. Deliver US2 (P2) → migrate tool proxy, remove Flask MCP code; validate no regressions.
4. Deliver US3 (P3) → add health/version routes; validate Cloud Run health check compatibility.
5. Polish → finalize Dockerfile, run full checklist, record regression log.

---

## Notes

- All tasks use strict checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- No automated test tasks are included per Zero-Testing Policy (Constitution Principle III).
- T009 (tool proxy custom route) is a prerequisite for T013 (Flask proxy removal) — do not reorder.
- FastMCP 3.2.4 `@mcp.custom_route()` is the sole public API for adding non-MCP HTTP routes.
- `VersionHeaderMiddleware` must be a proper Starlette ASGI middleware class (not a `@app.after_request` Flask hook).
