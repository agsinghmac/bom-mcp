# Implementation Plan: FastMCP Skill Discovery and Resource Index Refactor

**Branch**: `002-create-feature-branch` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fastmcp-skill-discovery/spec.md`

## Summary

Refactor skill resource handling in the Python FastMCP server from a single hardcoded skill into filesystem-based discovery from `.skills/`, publish one `skill://<filename>` resource per markdown file plus `skill://index`, remove MCP App metadata coupling, and add refresh, caching, and fault-isolated error handling while preserving existing tool business logic.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: FastMCP, standard library filesystem/time/parsing modules  
**Storage**: File-based markdown skills in `.skills/`; existing SQLite remains unchanged  
**Target Platform**: Local/server MCP runtime on Windows/Linux/macOS  
**Project Type**: Python MCP server refactor with resource-discovery behavior  
**Performance Goals**: Resource list/read remains interactive for normal skill counts; repeated reads should avoid reparsing unchanged files  
**Constraints**: No business logic changes to existing MCP tools; zero-testing policy (manual verification only); no new framework dependencies  
**Scale/Scope**: Multiple markdown skills in `.skills/` (dozens expected), one index resource, startup refresh plus runtime refresh support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Clean Code First**: PASS. Work is scoped to resource plumbing with explicit separation (discovery, parsing, cache, publication).
- **II. Simple Responsive Design & Minimal Dependencies**: PASS. Uses existing stack and standard library only.
- **III. Zero-Testing Policy**: PASS. Validation strategy is manual verification via MCP resource list/read flows.
- **IV. Tech Stack Lock**: PASS. Remains Python + FastMCP + existing MCP Apps context.

Post-Design Re-check: PASS. Research/design artifacts do not introduce principle violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-fastmcp-skill-discovery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── skill-discovery-resource-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server.py
run_mcp.py
skills/                         # legacy location to be replaced
.skills/                        # target skill source directory
.github/copilot-instructions.md # plan reference consumed by agent context
specs/002-fastmcp-skill-discovery/
mcp_app/
```

**Structure Decision**: Keep the single Python MCP server architecture and implement discovery/index/cache/refresh in the existing server resource layer without changing tool logic paths.

## Phase 0: Research Results Applied

1. Discovery model: scan `.skills/*.md`, normalize names, and register deterministic `skill://<filename>` URIs.
2. Metadata extraction: parse markdown title/lead description with safe fallback when content is incomplete.
3. Refresh model: mandatory startup discovery plus runtime refresh trigger (polling or event-driven depending on runtime support).
4. Error model: isolate file-level failures; preserve serving of unaffected and last-known-good skills.
5. Cache model: keep parsed metadata/content with freshness checks based on file stat changes.

## Phase 1: Design Output Mapping

1. Data model captured in [data-model.md](./data-model.md).
2. Resource and behavior contract captured in [contracts/skill-discovery-resource-contract.md](./contracts/skill-discovery-resource-contract.md).
3. Manual validation flow captured in [quickstart.md](./quickstart.md).
4. Agent context marker updated in [.github/copilot-instructions.md](../../.github/copilot-instructions.md) to this plan.

## Phase 2 Preview (for /speckit.tasks)

1. Build skill discovery manager and cache state container.
2. Replace hardcoded single resource registration with dynamic per-skill registration.
3. Implement `skill://index` generation and publication.
4. Add startup and runtime refresh orchestration with diagnostics.
5. Migrate legacy skill folder usage from `skills/` to `.skills/`.
6. Manually verify no regressions in existing MCP tools.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Summary (2026-05-04)

- Added `skill_resource_manager.py` to handle discovery, markdown metadata extraction, caching, refresh cycles, and diagnostics.
- Replaced hardcoded single skill resource registration with dynamic concrete resource registration from `.skills/*.md`.
- Added aggregated index resource at `skill://index` with status counters and diagnostics.
- Added startup refresh plus periodic runtime refresh worker (30-second interval).
- Implemented file-level failure isolation with last-known-good fallback behavior.
- Removed all MCP App UI tool metadata assignments (`tool._meta`) from the Python MCP server.
- Preserved existing non-skill tool business logic and manually validated representative tool calls.
