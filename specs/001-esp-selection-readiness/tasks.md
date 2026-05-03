# Tasks: ESP Selection and BOM Readiness Assessment Skill Resource

**Input**: Design documents from `/specs/001-esp-selection-readiness/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: FORBIDDEN - Per BOM-MCP Constitution (Principle III: Zero-Testing Policy), no unit/integration/e2e test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and manual verification.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the skill content file and register the `skill://` MCP resource.

- [X] T001 Create the skill content file with the 9 required contract sections in `skills/esp_selection_bom_readiness.md`
- [X] T002 Implement MCP resource registration for `skill://esp-selection-bom-readiness` in `mcp_server.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure resource discovery/read behavior is working before story-specific instruction content is finalized.

- [X] T003 Validate resource discoverability metadata (`uri`, `name`, `description`) against contract in `mcp_server.py`
- [X] T004 Validate resource read behavior returns skill content from `skills/esp_selection_bom_readiness.md` in `mcp_server.py`
- [X] T005 Align plan structure to include the `skills/` directory in `specs/001-esp-selection-readiness/plan.md`

**Checkpoint**: `skill://esp-selection-bom-readiness` is discoverable and readable.

---

## Phase 3: User Story 1 - Recommend Best-Fit ESP (Priority: P1)

**Goal**: Define input, validation, ranking, and orchestration instructions so an agent can produce ranked ESP recommendations.

**Independent Test**: Read `skill://esp-selection-bom-readiness` and execute only recommendation steps to produce ranked candidates with fit summaries.

### Implementation for User Story 1

- [X] T006 [P] [US1] Author section 1 (Purpose and scope) and section 2 (Required inputs) in `skills/esp_selection_bom_readiness.md`
- [X] T007 [P] [US1] Author section 3 (Input validation and bounds handling) in `skills/esp_selection_bom_readiness.md`
- [X] T008 [US1] Author section 4 (ESP ranking logic) using flow as primary criterion, then smallest acceptable positive power headroom, then frequency compatibility in `skills/esp_selection_bom_readiness.md`
- [X] T009 [US1] Update fit summary guidance to explain primary/binding constraints and margins in section 4 of `skills/esp_selection_bom_readiness.md`
- [X] T010 [US1] Author section 8 subset for recommendation orchestration order using `list_esps` and `get_esp` without frequency hard pre-filtering in `skills/esp_selection_bom_readiness.md`

**Checkpoint**: US1 instructions independently support ranking-only workflow.

---

## Phase 4: User Story 2 - Assess BOM Field Readiness (Priority: P2)

**Goal**: Define readiness logic with critical-part thresholds and availability taxonomy.

**Independent Test**: Read skill resource and apply readiness steps for a known ESP to compute field-ready status.

### Implementation for User Story 2

- [X] T011 [P] [US2] Author section 5 (BOM readiness logic) including critical-part density and >=80% critical availability rule in `skills/esp_selection_bom_readiness.md`
- [X] T012 [P] [US2] Author section 6 (Availability flag taxonomy: GREEN/YELLOW/RED/BLOCKED) with risk mapping in `skills/esp_selection_bom_readiness.md`
- [X] T013 [US2] Expand section 8 subset for readiness orchestration using `get_esp_bom` and `get_bom_summary` in `skills/esp_selection_bom_readiness.md`

**Checkpoint**: US2 instructions independently support readiness workflow.

---

## Phase 5: User Story 3 - Support Procurement Review (Priority: P3)

**Goal**: Define procurement alerts, part-level retrieval, edge-case handling, and final output template.

**Independent Test**: Read skill resource and produce procurement-focused output with flagged parts and urgency levels.

### Implementation for User Story 3

- [X] T014 [P] [US3] Author section 7 (Procurement alert mapping and urgency) in `skills/esp_selection_bom_readiness.md`
- [X] T015 [P] [US3] Expand section 8 subset for part detail retrieval using `get_part` for flagged BOM items in `skills/esp_selection_bom_readiness.md`
- [X] T016 [US3] Author section 9 (Output template) with `recommendations`, `bom_readiness_reports`, and `procurement_alerts` aligned to `specs/001-esp-selection-readiness/data-model.md` in `skills/esp_selection_bom_readiness.md`
- [X] T017 [US3] Add edge-case handling guidance (no candidates, missing BOM, invalid inputs, ranking ties) in section 5 and section 9 of `skills/esp_selection_bom_readiness.md`

**Checkpoint**: US3 instructions independently support procurement review output.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep repository documentation synchronized and run end-to-end manual verification.

- [X] T018 [P] Update MCP resource documentation to include `skill://esp-selection-bom-readiness` in `README.md`
- [X] T019 [P] Update runtime guidance for resource-backed skills in `CLAUDE.md`
- [X] T020 [P] Update feature context notes for `skill://` resource usage in `CONTEXT.md`
- [X] T021 Execute manual end-to-end quickstart validation from `specs/001-esp-selection-readiness/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1: No dependencies.
- Phase 2: Depends on Phase 1 and blocks all user stories.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2.
- Phase 5 (US3): Depends on Phase 2.
- Phase 6: Depends on completion of Phases 3-5.

### User Story Dependencies

- US1: Independent after foundational completion.
- US2: Independent after foundational completion.
- US3: Independent after foundational completion; references outputs from US1/US2 schema but can be authored in parallel.

### Parallel Opportunities

- Setup/Foundational: T001 with T002 can proceed in parallel once file paths are agreed; T003 and T004 can run in parallel after T002.
- US1: T006 and T007 can run in parallel.
- US2: T011 and T012 can run in parallel.
- US3: T014 and T015 can run in parallel.
- Polish: T018, T019, and T020 can run in parallel.

---

## Parallel Execution Examples

### User Story 1

- Run T006 and T007 together (different sections in `skills/esp_selection_bom_readiness.md`).
- Then run T008, T009, and T010 sequentially.

### User Story 2

- Run T011 and T012 together.
- Then run T013.

### User Story 3

- Run T014 and T015 together.
- Then run T016 and T017.

---

## Implementation Strategy

### MVP First

- Deliver Phases 1-5 for a complete, independently useful skill resource that satisfies recommendation + readiness + procurement output requirements.

### Incremental Delivery

- Increment 1: Resource registration and discovery/read behavior (T001-T004).
- Increment 2: Recommendation guidance (US1, T006-T010).
- Increment 3: Readiness guidance (US2, T011-T013).
- Increment 4: Procurement/output guidance (US3, T014-T017).
- Increment 5: Documentation sync and manual validation (T018-T021).
