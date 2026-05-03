# Contract: MCP Skill Resource for ESP Selection and BOM Readiness

## Resource Identity

- Scheme: `skill://`
- URI: `skill://esp-selection-bom-readiness`
- Type: `text/markdown` or structured text payload served through MCP resource read API

## Discovery Contract

When resources are listed, the server MUST include an entry with:

- `uri`: `skill://esp-selection-bom-readiness`
- `name`: `ESP Selection & BOM Readiness Assessment`
- `description`: Instruction resource guiding agent workflow for recommendation and readiness reporting

## Read Contract

Reading `skill://esp-selection-bom-readiness` MUST return instruction content with these sections:

1. Purpose and scope
2. Required inputs (`required_flow_m3d`, `max_power_kw`, `frequency_hz`)
3. Input validation and bounds handling
4. ESP ranking logic (flow -> power -> frequency)
5. BOM readiness logic (critical availability >= 80%)
6. Availability flag taxonomy (GREEN/YELLOW/RED/BLOCKED)
7. Procurement alert mapping and urgency
8. Required MCP tools and orchestration order
9. Output template for final report

## Agent Output Contract (as defined by skill instructions)

The generated assessment output MUST include:

- `recommendations`: ranked ESP list with fit summaries
- `bom_readiness_reports`: per-recommendation readiness details with critical percentage and field-ready status
- `procurement_alerts`: part-level alerts including flag, reason, and urgency

## Error and Edge Handling Contract

Instruction content MUST specify handling for:

- No matching ESP candidates
- Missing BOM data for recommended ESP
- Invalid input values (non-physical or out-of-bounds)
- Tie-breaking when candidates have equal rank factors

## Compatibility

- Must work with existing MCP server tools; no new assessment tool endpoint required.
- Must remain readable by generic MCP clients capable of resource list/read operations.
