# Contract: Skill Discovery Resources for FastMCP Server

## Scope

Defines the externally visible MCP resource behavior for discovered skill files and index publication.

## Resource Identity

- Scheme: `skill://`
- Dynamic resources: `skill://<filename-without-extension>` for each valid `.skills/*.md` file
- Index resource: `skill://index`

## Discovery Contract

When MCP resources are listed:

1. Each valid discovered skill MUST appear as one resource entry.
2. Each entry MUST include:
   - `uri` following `skill://<filename>`
   - `name`
   - `description` extracted from markdown or fallback text
   - `mimeType` compatible with markdown rendering
3. `skill://index` MUST appear as a discoverable resource.
4. Skill resources MUST NOT include MCP App UI metadata coupling used by legacy implementation.

## Read Contract: Dynamic Skill Resource

Reading `skill://<filename>` MUST return:

1. Markdown content for that skill.
2. Content type compatible with markdown display.
3. Metadata-consistent identity (URI, name, description).
4. Runtime-resolved content from current cache state (or last-known-good degraded fallback where applicable).

Error behavior:

1. Unknown skill URI returns a not-found resource error.
2. Malformed source file may return degraded metadata/content only for that skill; other skills remain available.
3. Last-known-good content MAY be served when configured and available.

## Read Contract: Index Resource

Reading `skill://index` MUST return a machine- and human-readable catalog containing:

1. Generation timestamp.
2. Total/discovery status summary.
3. Ordered list of active skills with:
   - URI
   - name
   - description
   - status (VALID or DEGRADED)
   - diagnostics section when refresh failures occurred

## Refresh Contract

1. Startup refresh is mandatory before first normal resource serving.
2. Runtime refresh is supported and updates discovery based on filesystem changes.
3. Add/edit/delete skill files in `.skills/` are reflected in discovery after refresh cycle completion.
4. Refresh failures are file-scoped and surfaced as diagnostics without globally disabling unaffected skills.

## Caching Contract

1. Server caches parsed metadata and content for discovered skills.
2. Cache invalidates only entries whose source files changed, were removed, or were newly added.
3. Repeated reads for unchanged skills should not require reparsing source files.

## Compatibility and Non-Regression

1. Existing MCP tool behavior remains unchanged.
2. Contract changes are limited to skill resource discovery/read lifecycle.
3. Existing clients using MCP list/read operations remain compatible.
