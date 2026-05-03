# Research: ESP Selection and BOM Readiness Skill Resource

## Decision 1: Expose Skill as MCP Resource (`skill://`) Instead of Tool

- Decision: Implement a discoverable/readable MCP resource with URI `skill://esp-selection-bom-readiness`.
- Rationale: User clarified agents must discover and read skills from MCP resources rather than `SKILL.md` files. Resource model fits instruction delivery and keeps execution with existing tools.
- Alternatives considered:
  - New parameterized MCP tool endpoint: rejected because requirement is resource-first instruction pattern.
  - Static markdown outside MCP: rejected because agents must source instructions from MCP resources.

## Decision 2: Resource Payload Format

- Decision: Use structured instruction payload that includes purpose, required inputs, validation rules, ranking logic, readiness rules, availability taxonomy, procurement alerts, and output template.
- Rationale: Agents need deterministic guidance and consistent output shape. Structured sections reduce ambiguity during orchestration.
- Alternatives considered:
  - Unstructured prose-only payload: rejected due higher interpretation variance.
  - External schema dependency: rejected to avoid additional dependencies/complexity.

## Decision 3: Tool Orchestration Strategy

- Decision: Skill guidance instructs agents to orchestrate existing MCP tools (`list_esps`, `get_esp`, `get_esp_bom`, `get_bom_summary`, `get_part`) for data retrieval.
- Rationale: Reuses validated data pathways and avoids introducing a duplicate compute endpoint.
- Alternatives considered:
  - Add aggregate assessment API/tool: rejected by scope and would duplicate logic.

## Decision 4: Readiness Rule and Risk Mapping

- Decision: Field-ready criterion is critical-part availability >= 80%; RED/BLOCKED critical parts count against threshold. Availability taxonomy: GREEN, YELLOW, RED, BLOCKED.
- Rationale: Clarified in spec and provides deterministic pass/fail readiness status.
- Alternatives considered:
  - 100% critical-part availability: rejected as overly strict for operational reality.
  - Overall-BOM percentage-only metric: rejected because criticality must drive readiness.

## Decision 5: Recommendation Ranking Method

- Decision: Rank candidates by flow match (primary), then power headroom, then frequency compatibility.
- Rationale: Clarified in spec; matches practical ESP selection priority and produces explainable ranking.
- Alternatives considered:
  - Weighted aggregate score with configurable weights: deferred as unnecessary complexity for v1 skill guidance.
