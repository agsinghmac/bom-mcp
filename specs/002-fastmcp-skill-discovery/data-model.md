# Data Model: FastMCP Skill Discovery Refactor

## Entity: SkillFile

- Description: Raw markdown file discovered from `.skills/`.
- Fields:
  - `path` (string, required): Absolute canonical file path.
  - `filename` (string, required): Basename without extension.
  - `extension` (string, required): Must be `.md`.
  - `mtime_ns` (integer, required): File last-modified marker for freshness checks.
  - `size_bytes` (integer, required): File size for diagnostics and cache heuristics.
- Validation:
  - File must be readable text.
  - Filename must normalize to a valid resource token.

## Entity: SkillMetadata

- Description: Parsed, publishable metadata extracted from markdown content.
- Fields:
  - `uri` (string, required): `skill://<filename>`.
  - `name` (string, required): Human-readable title (heading or filename fallback).
  - `description` (string, required): Extracted summary/fallback description.
  - `source_path` (string, required): Originating file path.
  - `parse_status` (enum, required): VALID | DEGRADED | INVALID.
  - `errors` (array<string>, optional): Parse/validation issues for diagnostics.
- Validation:
  - URI must be unique in active catalog.
  - Description must be non-empty in published output.

## Entity: SkillContentRecord

- Description: Cached content representation for resource read responses.
- Fields:
  - `uri` (string, required)
  - `content` (string, required): Renderable markdown payload.
  - `content_type` (string, required): `text/markdown`.
  - `etag` (string, optional): Deterministic freshness token.
  - `refreshed_at` (datetime, required)
- Validation:
  - `content` must reflect current file when cache is fresh.

## Entity: SkillCatalog

- Description: In-memory source of truth for all discoverable skills.
- Fields:
  - `entries` (map<string, SkillMetadata>, required): Keyed by URI.
  - `content_cache` (map<string, SkillContentRecord>, required)
  - `source_index` (map<string, string>, required): File path to URI mapping.
  - `last_refresh_at` (datetime, required)
  - `refresh_status` (enum, required): OK | PARTIAL | FAILED.
- Validation:
  - Entry URI set and content cache URI set must remain consistent.
  - PARTIAL status requires at least one diagnostic.

## Entity: SkillIndexResource

- Description: Aggregated resource exposed at `skill://index`.
- Fields:
  - `uri` (string, required): Fixed value `skill://index`.
  - `generated_at` (datetime, required)
  - `skills` (array<SkillIndexItem>, required)
  - `summary` (object, required): counts for total/valid/degraded/invalid.
- Validation:
  - Skills are sorted deterministically by URI.

## Entity: SkillIndexItem

- Description: One row inside the index resource.
- Fields:
  - `uri` (string, required)
  - `name` (string, required)
  - `description` (string, required)
  - `status` (enum, required): VALID | DEGRADED.
  - `source` (string, required): Relative path under `.skills/`.
- Validation:
  - Must reference an active catalog entry.

## Entity: RefreshCycle

- Description: One discovery/refresh operation.
- Fields:
  - `started_at` (datetime, required)
  - `completed_at` (datetime, optional)
  - `mode` (enum, required): STARTUP | PERIODIC | MANUAL.
  - `files_seen` (integer, required)
  - `files_changed` (integer, required)
  - `files_failed` (integer, required)
  - `diagnostics` (array<RefreshDiagnostic>, optional)
- Validation:
  - Completed cycle must include status and counters.

## Entity: RefreshDiagnostic

- Description: Structured issue captured during refresh.
- Fields:
  - `severity` (enum, required): INFO | WARN | ERROR.
  - `file_path` (string, optional)
  - `code` (string, required): Stable diagnostic code.
  - `message` (string, required)
  - `action_hint` (string, optional)
- Validation:
  - ERROR diagnostics should include actionable hints where possible.
