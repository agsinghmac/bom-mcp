# Tasks: FastMCP Skill Discovery and Resource Index Refactor

**Input**: Design documents from `/specs/002-fastmcp-skill-discovery/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/skill-discovery-resource-contract.md`, `quickstart.md`

**Tests**: FORBIDDEN - Per BOM-MCP Constitution (Principle III: Zero-Testing Policy), no unit, integration, or end-to-end test tasks are included.

**Organization**: Tasks are grouped by user story to allow independent implementation and manual verification.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository structure and configuration for skill discovery refactor.

- [x] T001 Create target skill directory scaffold in .skills/.gitkeep
- [x] T002 Add skill discovery configuration constants in mcp_server.py
- [x] T003 [P] Add migration note from skills/ to .skills/ in README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared discovery/cache primitives required by all user stories.

**⚠️ CRITICAL**: No user story implementation starts before this phase is complete.

- [x] T004 Create skill catalog and cache state models in skill_resource_manager.py
- [x] T005 Implement URI normalization and filename collision guards in skill_resource_manager.py
- [x] T006 Implement markdown load and base parsing helpers in skill_resource_manager.py
- [x] T007 Implement refresh cycle and diagnostic result types in skill_resource_manager.py
- [x] T008 Wire skill resource manager initialization into server startup in mcp_server.py

**Checkpoint**: Foundation ready - user story work can begin.

---

## Phase 3: User Story 1 - Discover All Skills Automatically (Priority: P1) 🎯 MVP

**Goal**: Discover `.skills/*.md` files and expose each as a dynamic `skill://<filename>` resource.

**Independent Test**: With at least two markdown files in `.skills/`, server startup lists both URIs and each resource can be read.

### Implementation for User Story 1

- [x] T009 [US1] Implement filesystem discovery for .skills/*.md in skill_resource_manager.py
- [x] T010 [US1] Implement active skill registry build from discovered files in skill_resource_manager.py
- [x] T011 [US1] Implement dynamic skill resource listing registration in mcp_server.py
- [x] T012 [US1] Implement dynamic skill resource read routing for skill://<filename> in mcp_server.py
- [x] T013 [P] [US1] Move existing skill file from skills/esp_selection_bom_readiness.md to .skills/esp_selection_bom_readiness.md
- [x] T014 [US1] Remove hardcoded single-skill resource registration from mcp_server.py

**Checkpoint**: User Story 1 is independently functional and manually verifiable.

---

## Phase 4: User Story 2 - Consume Accurate Skill Metadata (Priority: P2)

**Goal**: Publish robust name/description metadata per skill and expose aggregated `skill://index`.

**Independent Test**: Resource list and `skill://index` show extracted descriptions for all valid skills with fallback behavior for incomplete markdown.

### Implementation for User Story 2

- [x] T015 [US2] Implement description extraction with fallback strategy in skill_resource_manager.py
- [x] T016 [US2] Implement display-name extraction with safe fallback in skill_resource_manager.py
- [x] T017 [US2] Build index resource payload generator for skill://index in skill_resource_manager.py
- [x] T018 [US2] Register and serve skill://index resource in mcp_server.py
- [x] T019 [US2] Remove mcp_app UI metadata usage from skill resource publication in mcp_server.py
- [x] T020 [P] [US2] Align resource contract metadata fields in specs/002-fastmcp-skill-discovery/contracts/skill-discovery-resource-contract.md

**Checkpoint**: User Story 2 is independently functional and manually verifiable.

---

## Phase 5: User Story 3 - Keep Skill Catalog Fresh and Safe (Priority: P3)

**Goal**: Add runtime refresh, cache invalidation, and fault-isolated error handling.

**Independent Test**: Add/edit/delete malformed skill files and confirm refresh reflects changes while unaffected skills remain available.

### Implementation for User Story 3

- [x] T021 [US3] Implement cache invalidation keyed by file freshness metadata in skill_resource_manager.py
- [x] T022 [US3] Implement startup refresh execution and periodic runtime refresh trigger in mcp_server.py
- [x] T023 [US3] Implement per-file parse/read fault isolation with last-known-good fallback in skill_resource_manager.py
- [x] T024 [US3] Implement structured refresh diagnostics emission in mcp_server.py
- [x] T025 [US3] Include degraded/failed status reporting in skill://index output in skill_resource_manager.py
- [x] T026 [P] [US3] Document refresh and recovery operations in specs/002-fastmcp-skill-discovery/quickstart.md

**Checkpoint**: User Story 3 is independently functional and manually verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation and manual regression checks across stories.

- [x] T027 [P] Update implementation summary and operational notes in specs/002-fastmcp-skill-discovery/plan.md
- [x] T028 Run end-to-end manual validation checklist updates in specs/002-fastmcp-skill-discovery/quickstart.md
- [x] T029 Perform non-skill MCP tool regression walkthrough and record notes in specs/002-fastmcp-skill-discovery/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion; blocks all story work.
- **Phase 3 (US1)**: Depends on Phase 2 completion; defines MVP.
- **Phase 4 (US2)**: Depends on Phase 2 and US1 dynamic resource flow.
- **Phase 5 (US3)**: Depends on Phase 2 and benefits from US1/US2 resource pipeline.
- **Phase 6 (Polish)**: Depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational work; no dependency on other user stories.
- **US2 (P2)**: Depends on US1 dynamic skill registration being available.
- **US3 (P3)**: Depends on US1 registry and US2 index output path for degraded status reporting.

### Within Each User Story

- Discovery/parsing primitives before resource publication.
- Resource publication before manual verification/docs updates.
- Story checkpoint validation before moving to next priority.

### Parallel Opportunities

- T003 can run in parallel with T001-T002.
- T013 can run in parallel with T011-T012 after T009-T010.
- T020 can run in parallel with T018-T019.
- T026 can run in parallel with T021-T025 once refresh design is stable.
- T027 can run in parallel with T028-T029.

---

## Parallel Example: User Story 1

- T011 [US1] Implement dynamic skill resource listing registration in mcp_server.py
- T013 [US1] Move existing skill file from skills/esp_selection_bom_readiness.md to .skills/esp_selection_bom_readiness.md

---

## Parallel Example: User Story 2

- T018 [US2] Register and serve skill://index resource in mcp_server.py
- T020 [US2] Align resource contract metadata fields in specs/002-fastmcp-skill-discovery/contracts/skill-discovery-resource-contract.md

---

## Parallel Example: User Story 3

- T024 [US3] Implement structured refresh diagnostics emission in mcp_server.py
- T026 [US3] Document refresh and recovery operations in specs/002-fastmcp-skill-discovery/quickstart.md

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Manually verify startup discovery + dynamic read behavior.
5. Demo/deploy MVP.

### Incremental Delivery

1. Setup + Foundational → discovery infrastructure ready.
2. Deliver US1 (MVP) → validate manually.
3. Deliver US2 (metadata + index) → validate manually.
4. Deliver US3 (refresh + caching + resilience) → validate manually.
5. Polish and regression checks.

### Parallel Team Strategy

1. One developer handles `skill_resource_manager.py` internals.
2. One developer handles `mcp_server.py` integration points.
3. One developer maintains feature docs/quickstart updates in parallel.

---

## Notes

- All tasks use strict checklist format: `- [x] T### [P?] [US?] Description with file path`.
- No automated test tasks are included due repository constitution policy.
- Preserve existing non-skill MCP tool business logic during implementation.

