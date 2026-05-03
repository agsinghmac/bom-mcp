# Feature Specification: FastMCP Skill Resource Refactor

**Feature Branch**: `002-create-feature-branch`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Create a specification to refactor a Python FastMCP server. Remove mcp_app metadata, replace skills/ with .skills/, auto-discover .skills/*.md files, expose each as skill://<filename>, extract descriptions from markdown, add skill://index, support refresh (startup minimum, runtime preferred), add caching and error handling, and do not modify tool business logic."

## User Scenarios & Manual Verification *(mandatory)*

### User Story 1 - Discover All Skills Automatically (Priority: P1)

As an AI agent using MCP resources, I need every valid markdown skill document in the configured skill directory to be discoverable without manual registration so I can use available guidance reliably.

**Why this priority**: Skill discovery is the core value of this refactor and enables all other behavior.

**Independent Verification**: Can be fully verified by placing multiple markdown files in the skill directory, restarting the server, and confirming all are listed and readable as MCP resources.

**Acceptance Scenarios**:

1. **Given** multiple valid skill markdown files in the skill directory, **When** the server starts, **Then** each file is exposed as an MCP resource using the `skill://<filename>` URI pattern.
2. **Given** one existing and one newly added skill file, **When** discovery refresh runs, **Then** both skills appear in resource listings without manual code changes.

---

### User Story 2 - Consume Accurate Skill Metadata (Priority: P2)

As an AI agent, I need each skill resource to provide a meaningful description derived from the markdown file so I can choose the correct skill for a task.

**Why this priority**: Correct metadata improves skill selection quality and reduces misuse.

**Independent Verification**: Can be fully verified by checking resource listing metadata for multiple skills and confirming descriptions match source markdown content.

**Acceptance Scenarios**:

1. **Given** a skill file with a title and descriptive section, **When** resources are listed, **Then** the published skill description matches the extracted markdown description.
2. **Given** a skill file with incomplete or malformed descriptive content, **When** resources are listed, **Then** a safe fallback description is published and the server remains operational.

---

### User Story 3 - Keep Skill Catalog Fresh and Safe (Priority: P3)

As an operator, I need skills to refresh reliably and recover gracefully from file errors so the server can remain available while reflecting current skill content.

**Why this priority**: Refresh and resilience reduce maintenance burden and avoid outages from content issues.

**Independent Verification**: Can be fully verified by changing, adding, and removing skill files at runtime, then confirming resources and index update while errors are isolated.

**Acceptance Scenarios**:

1. **Given** a skill file is changed after startup, **When** runtime refresh is triggered, **Then** the corresponding skill resource and index reflect updated content.
2. **Given** one skill file has a read or parse error, **When** refresh runs, **Then** unaffected skill resources continue to be served and the failure is reported with actionable diagnostics.

### Edge Cases

- What happens when two skill files resolve to the same resource name after normalization?
- How does the system behave when the `.skills/` directory is missing, empty, or inaccessible?
- What happens when a skill file is deleted while a refresh is in progress?
- How does the system handle very large markdown files or files that are not valid UTF-8 text?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST stop publishing or relying on MCP App UI-specific metadata for skill resources.
- **FR-002**: System MUST use `.skills/` as the default directory for skill markdown resources.
- **FR-003**: System MUST discover all markdown files directly under `.skills/` at startup and register each valid file as an MCP resource.
- **FR-004**: System MUST publish each discovered skill file using the URI scheme `skill://<filename-without-extension>`.
- **FR-005**: System MUST extract a human-meaningful description from each skill markdown file and publish it as resource metadata.
- **FR-006**: System MUST expose an aggregated index resource at `skill://index` containing discoverable skill names, URIs, and descriptions.
- **FR-007**: System MUST refresh skill discovery at server startup and MUST support runtime refresh so changes in `.skills/` can be reflected without code edits.
- **FR-008**: System MUST include caching for discovered skill content and metadata to reduce repeated file parsing during resource operations.
- **FR-009**: System MUST implement fault-isolated error handling so a failed or malformed skill file does not block other valid skill resources.
- **FR-010**: System MUST provide operator-visible diagnostics for discovery, parse, and refresh failures.
- **FR-011**: Refactor scope MUST preserve existing business logic and behavior of non-skill MCP tools.

### Key Entities *(include if feature involves data)*

- **Skill Document**: A markdown file in `.skills/` representing one agent-usable instruction resource.
- **Skill Resource Entry**: Published MCP resource record containing a stable URI, display name, description, and content reference.
- **Skill Index**: Aggregated resource summarizing all currently discoverable skill resources.
- **Skill Cache Record**: Cached representation of parsed skill metadata and content with freshness state.
- **Refresh Event**: Discovery cycle trigger that updates cache and published resources from current filesystem state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid markdown files present in `.skills/` at startup are discoverable as `skill://` resources in a single server run.
- **SC-002**: 100% of discovered skills include non-empty descriptions in resource metadata and in `skill://index`.
- **SC-003**: Runtime changes (add, edit, delete) to skill files are reflected in resource listings within 60 seconds in normal operating conditions.
- **SC-004**: In error-injection testing with at least one malformed skill file, at least 95% of unaffected valid skills remain readable and listed.
- **SC-005**: No regressions are observed in functional behavior of existing non-skill MCP tools across baseline verification scenarios.

## Assumptions

- Existing skill markdown guidance will be migrated from `skills/` to `.skills/` as part of rollout.
- File naming in `.skills/` will follow a convention that can produce unique skill resource names.
- Runtime refresh can be implemented using a polling or event-driven strategy supported by the deployment environment.
- Existing MCP clients already support reading listed resources via `skill://` URIs.

## Technical Design

- Introduce a dedicated skill resource manager responsible for discovery, metadata extraction, caching, indexing, and refresh orchestration.
- Define a deterministic mapping strategy from skill filename to resource URI to ensure stable references over time.
- Use a markdown metadata extraction strategy with clear fallback behavior when descriptive sections are missing.
- Publish `skill://index` from the same in-memory source of truth used for individual resource publication.
- Isolate refresh and parse failures per file, and continue publishing last known good entries where possible.
- Preserve current non-skill MCP tool interfaces and execution paths, limiting changes to skill resource plumbing.

## Acceptance Criteria

1. Starting from an empty cache and a populated `.skills/` directory, server startup publishes all valid skills plus `skill://index`.
2. Removing MCP App UI-specific metadata from skill resources does not reduce discoverability or readability of those resources through MCP.
3. Updating one skill markdown file updates its published description and index entry after runtime refresh.
4. A malformed skill file produces diagnostics and is excluded or downgraded safely without preventing other skills from loading.
5. Existing tool behavior outside skill-resource handling remains unchanged in pre/post comparison.

## Implementation Tasks

1. Define refactor boundaries and identify skill-resource-only touchpoints in the FastMCP server.
2. Replace static single-skill registration with `.skills/` discovery and per-file resource publication.
3. Implement markdown description extraction with fallback handling for incomplete documents.
4. Add and publish `skill://index` built from discovered skill entries.
5. Add cache lifecycle for discovered content and metadata to minimize repeated file reads.
6. Add startup refresh and runtime refresh mechanism with predictable update semantics.
7. Add structured error handling and operator diagnostics for file, parse, and refresh failures.
8. Execute regression validation to confirm non-skill tool business logic remains unchanged.
