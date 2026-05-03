# Research: FastMCP Skill Discovery and Index Resources

## Decision 1: Skill Source Directory and Discovery Strategy

- Decision: Use `.skills/` as the canonical skill source and discover files with `*.md` extension at startup.
- Rationale: Matches requirement to replace legacy `skills/` and removes manual skill registration.
- Alternatives considered:
  - Keep `skills/` with backward compatibility aliases: rejected for ambiguity and migration drift.
  - Hardcoded file manifest: rejected because it recreates manual maintenance burden.

## Decision 2: URI Naming and Collision Handling

- Decision: Map each filename (without extension) to `skill://<filename>` using deterministic normalization and explicit collision diagnostics.
- Rationale: Stable URIs are required for agent usage and references.
- Alternatives considered:
  - Hash-based URIs: rejected because non-human-readable and unstable across file renames.
  - Title-based URIs from markdown heading: rejected because heading edits would silently break references.

## Decision 3: Description Extraction from Markdown

- Decision: Extract description from markdown front-matter summary when present, otherwise from first heading-adjacent paragraph, and fallback to a safe default.
- Rationale: Provides meaningful metadata while handling imperfect authoring.
- Alternatives considered:
  - Require strict metadata block in all files: rejected because overly brittle.
  - Use filename only as description: rejected for poor discoverability.

## Decision 4: Skill Index Resource

- Decision: Publish `skill://index` as an aggregated listing of skill URI, name, description, status, and last refresh timestamp.
- Rationale: Enables clients and agents to discover available skills in one read.
- Alternatives considered:
  - Depend only on generic resource listing: rejected because not all clients expose full list metadata consistently.

## Decision 5: Refresh Model

- Decision: Run mandatory startup refresh and support runtime refresh via a lightweight periodic poll with file timestamp checks; allow explicit refresh hook when runtime supports it.
- Rationale: Meets startup minimum and runtime preferred requirement with minimal dependency footprint.
- Alternatives considered:
  - Startup-only refresh: rejected because runtime updates would require restart.
  - Filesystem watcher dependency: rejected as optional due environment variability and extra complexity.

## Decision 6: Caching and Freshness

- Decision: Cache parsed skill content and metadata keyed by canonical file path, invalidating only changed/deleted/new files.
- Rationale: Avoids repeated parsing and supports fast resource reads.
- Alternatives considered:
  - No cache (always parse on read): rejected for unnecessary I/O and latency.
  - Full cache reset on every refresh: rejected because inefficient at scale.

## Decision 7: Error Handling and Isolation

- Decision: Treat each skill file as an isolated unit; failed files are excluded or served from last-known-good cache while logging structured diagnostics.
- Rationale: One malformed file must not take down all skill resources.
- Alternatives considered:
  - Fail-fast on first error: rejected due poor operational resilience.
  - Silent ignore of errors: rejected because operators need actionable diagnostics.

## Decision 8: Tool Logic Preservation Boundary

- Decision: Restrict code changes to resource discovery/publication layers and avoid modifications to existing tool execution paths.
- Rationale: Explicit requirement to keep business logic unchanged.
- Alternatives considered:
  - Refactor tool internals during same feature: rejected as scope risk and regression risk.
