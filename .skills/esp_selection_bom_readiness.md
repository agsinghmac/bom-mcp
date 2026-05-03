---
name: esp-selection-bom-readiness
description: Evaluate ESP model fit and BOM completeness based on operational requirements and return ranked recommendations with BOM analysis.
version: 1.0.0

tools:
  - list_esps
  - get_esp
  - get_esp_bom
  - get_bom_summary

inputs:
  required_flow_m3d:
    type: number
    required: true
    description: Target flow rate in cubic meters per day

  max_power_kw:
    type: number
    required: true
    description: Maximum available power budget

  frequency_hz:
    type: number
    required: true
    description: Operating frequency in Hz
---

# ESP Selection & BOM Readiness Assessment

## Purpose
Use this skill to evaluate ESP model fit and BOM completeness from a single operational requirement set.

This skill orchestrates MCP tools and returns:
- Ranked ESP recommendations
- BOM completeness report

**Limitations**
- No availability, lead time, or sourcing data
- Field readiness cannot be determined


---

## Input Validation Rules

- Reject missing values
- Reject non-numeric values
- Reject zero/negative values
- Reject non-physical values

Example:
- `required_flow_m3d must be a positive number`

---

## Tool Orchestration Flow

1. Call `list_esps`
2. Enrich with `get_esp`
3. Rank candidates
4. For each recommendation:
   - Call `get_esp_bom`
   - Call `get_bom_summary`

Do NOT call tools outside the declared list.

---

## Ranking Logic

Primary:
- Flow delta

Secondary:
- Power headroom

Tertiary:
- Frequency compatibility

Tie breaker:
- ESP ID ordering


---

## BOM Completeness Logic

Compute:
- bom_complete = total_parts > 0 AND assembly_count > 0
- critical_parts_percent

Report:
- Critical parts list
- BOM completeness
- Summary metrics

---

## Alerts

Generate only:
- BOM_INCOMPLETE
- CRITICAL_PARTS_UNDEFINED

Always include:
- esp_id
- alert_type
- detail

---

## Output Format

Return structured JSON:
- recommendations
- bom_completeness_reports
- bom_alerts
- summary

---

## Important Rules

- Do NOT infer availability or sourcing
- Do NOT fabricate missing data
- Always state limitations clearly