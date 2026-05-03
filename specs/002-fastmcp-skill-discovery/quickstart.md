# Quickstart: Manual Validation for Skill Discovery Refactor

## Goal

Manually verify dynamic skill discovery, index publication, runtime refresh, cache behavior, and error isolation while confirming existing tool business logic is unchanged.

## Prerequisites

- Python dependencies installed from [requirements.txt](../../../requirements.txt)
- MCP server runnable via [run_mcp.py](../../../run_mcp.py)
- At least two markdown files available in `.skills/`

## Validation Steps

1. Start MCP server.
2. List MCP resources and confirm:
   - one entry per `.skills/*.md` file as `skill://<filename>`
   - `skill://index` exists
3. Read each skill resource and verify markdown content, name, and description are populated.
4. Read `skill://index` and verify listed skills, descriptions, and status summary match discovery state.
5. Add a new markdown file under `.skills/`; trigger runtime refresh (or wait for periodic refresh), then confirm new skill appears.
6. Edit an existing skill description; refresh and confirm updated metadata is visible.
7. Delete one skill file; refresh and confirm its URI is removed from list and index.
8. Introduce one malformed markdown file; refresh and confirm:
   - diagnostics are produced
   - unaffected skills remain listable/readable
   - index indicates degraded/failed entry handling
9. Execute baseline manual checks for existing non-skill MCP tools and confirm behavior is unchanged.

## Runtime Refresh and Recovery Operations

1. Startup refresh: automatically runs when `mcp_server.py` is imported.
2. Runtime refresh: automatic periodic refresh every 30 seconds.
3. Recovery behavior: if one skill file fails to parse, the server keeps unaffected skill resources available and uses last-known-good content for previously valid files.
4. Operator diagnostics: read `skill://index` to inspect refresh status, changed/failed counters, and per-file diagnostics.

## Manual Validation Log (2026-05-04)

- [x] Startup discovery exposes `skill://index`.
- [x] Startup discovery exposes `skill://esp_selection_bom_readiness` from `.skills/esp_selection_bom_readiness.md`.
- [x] Dynamic skill resource content is readable through MCP resource reads.
- [x] Index resource includes refresh status and diagnostics section support.
- [x] Non-skill tool regression checks succeeded:
   - `get_stats()` returned expected keys.
   - `list_esps()` returned 10 records.
   - `get_esp('ESP-001')` returned a populated object.
   - `list_parts()` returned 30 records.
   - `list_assemblies()` returned 10 records.
   - `get_bom_summary('ESP-001')` returned expected summary keys.

## Expected Outcomes

- Dynamic `skill://` resources reflect `.skills/` filesystem state.
- `skill://index` is accurate and current after refresh cycles.
- Caching avoids repeated parsing for unchanged files.
- Single-file failures do not break unaffected skill resources.
- Existing tool business logic remains unchanged.
