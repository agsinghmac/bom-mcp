# Implementation Plan: ESP Selection and BOM Readiness Assessment Skill Resource

**Branch**: `001-add-esp-readiness-resource` | **Date**: 2026-04-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-esp-selection-readiness/spec.md`

## Summary

Add a new MCP resource type using the `skill://` scheme for ESP Selection and BOM Readiness Assessment. The resource stores executable guidance that agents read and follow to orchestrate existing MCP tools (ESP list/BOM/parts) and produce a combined output: ranked ESP recommendation plus BOM readiness report with critical-part percentage, availability flags, and procurement alerts.

## Technical Context

**Language/Version**: Python 3.x (existing codebase runtime)  
**Primary Dependencies**: FastMCP server implementation, existing ESP/BOM tool layer  
**Storage**: SQLite (existing ESP/BOM data source) + in-repo resource definitions  
**Target Platform**: MCP server runtime (local/desktop integration via Claude/Copilot)  
**Project Type**: MCP server + documentation resource feature  
**Performance Goals**: Skill resource read/discovery should be immediate for agent workflows; assessment workflow target remains aligned with spec outcomes  
**Constraints**: Preserve existing MCP tools; no new assessment tool endpoint; Zero-Testing policy (manual verification only)  
**Scale/Scope**: One new skill resource (`skill://esp-selection-bom-readiness`) plus resource discovery/read integration and guidance content

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Clean Code First**: PASS. Changes are additive and focused (resource registration + explicit instruction payload + minimal branching).
- **II. Simple Responsive Design & Minimal Dependencies**: PASS. No new third-party dependencies required; existing stack only.
- **III. Zero-Testing Policy**: PASS. Validation strategy is manual verification scenarios only.
- **IV. Tech Stack Lock**: PASS. Implementation remains Python + FastMCP + existing MCP Apps surface.

Post-Design Re-check: PASS (no principle violations introduced by research/design artifacts).

## Project Structure

### Documentation (this feature)

```text
specs/001-esp-selection-readiness/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── skill-resource-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server.py
esp_db.py
api.py
cli.py
skills/
  esp_selection_bom_readiness.md
mcp_app/
  server.ts
  resources/
```

**Structure Decision**: Keep single existing Python MCP server architecture. Implement `skill://` resource exposure in current server/resource registration flow and store skill instructions in `skills/esp_selection_bom_readiness.md`.

## Phase 0: Research Plan

1. Confirm MCP resource pattern already used in repository and map how a new URI-based resource is exposed.
2. Define canonical `skill://` URI naming and payload structure for agent-readable instructions.
3. Define agent orchestration pattern that references existing tools only (no new endpoint).
4. Resolve readiness scoring and alert mapping details into implementation-ready guidance.

## Phase 1: Design Plan

1. Define data model for skill resource metadata, instruction sections, and output template entities.
2. Define contract for discovery/read access to `skill://esp-selection-bom-readiness`.
3. Produce quickstart for manual validation in MCP host workflow.
4. Update agent context so future work references this plan.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
