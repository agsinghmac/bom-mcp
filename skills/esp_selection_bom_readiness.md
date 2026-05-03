# ESP Selection & BOM Readiness Assessment

## 1. Purpose and scope

Use this skill to evaluate ESP model fit and BOM completeness from a single operational requirement set. The workflow returns ranked recommendations plus a BOM completeness report based on data available in the database. This skill is instruction-only and must orchestrate existing MCP tools.

> **Data limitation**: The database does not store part availability flags, lead times, or sourcing status. Field readiness in the procurement sense (GREEN/YELLOW/RED/BLOCKED) cannot be determined from database data alone and is excluded from this skill's output.

## 2. Required inputs (`required_flow_m3d`, `max_power_kw`, `frequency_hz`)

- `required_flow_m3d` (number, required): target flow rate in cubic meters per day.
- `max_power_kw` (number, required): maximum available power budget.
- `frequency_hz` (number, required): operating frequency.

Expected units: m3/day, kW, Hz.

## 3. Input validation and bounds handling

Validate inputs before querying tools.

- Reject missing values.
- Reject non-numeric values.
- Reject zero/negative values.
- Reject non-physical values for the deployment context.
- Return corrective guidance with each validation failure.

Example validation message:
- `required_flow_m3d must be a positive number in m3/day`.

## 4. ESP ranking logic (flow -> power -> frequency)

Use existing tools: `list_esps` then `get_esp`.

1. Retrieve all candidate ESPs with `list_esps`.
2. Enrich each candidate with `get_esp` where needed.
3. Exclude candidates that fail mandatory constraints (for example, insufficient power versus `max_power_kw`).
4. Compute ranking factors:
   - `flow_delta = abs(candidate_flow_m3d - required_flow_m3d)`
   - `power_headroom_kw = max_power_kw - candidate_power_kw`
   - `frequency_compatibility = exact match preferred, closest supported frequency next`
5. Rank candidates by:
   - Primary: lowest `flow_delta`
   - Secondary: smallest acceptable positive `power_headroom_kw`
   - Tertiary: best `frequency_compatibility`
6. If still tied, use deterministic alphanumeric ESP ID ordering.

For each recommendation, include fit summary fields:
- primary/binding constraint
- flow delta
- power margin
- frequency status
- rank position

## 5. BOM completeness logic

Use `get_esp_bom` and `get_bom_summary` for each recommended ESP.

1. Fetch the flat BOM parts list with `get_esp_bom`.
2. Fetch the BOM summary with `get_bom_summary`.
3. From the summary, read the available fields:
   - `total_parts` — total unique parts in the BOM
   - `critical_parts_count` — count of parts flagged `is_critical = true`
   - `total_weight_kg` — combined BOM weight
   - `parts_by_category` — part count per category
   - `assembly_count` — number of assemblies
4. Compute:
   - `bom_complete = total_parts > 0 and assembly_count > 0`
   - `critical_parts_percent = (critical_parts_count / total_parts) * 100` if `total_parts > 0` else 0
5. Report:
   - List all critical parts by name and part number from the BOM parts list.
   - State BOM completeness (`bom_complete`).
   - Do NOT report a `field_ready` boolean. State instead: "Field readiness requires external availability and lead-time data not present in the database."

If BOM data is missing or `total_parts = 0`, report BOM as incomplete and flag the ESP for manual BOM review.

## 6. Available part fields (database schema)

The following per-part fields are returned by `get_esp_bom` and `get_part`:

| Field | Type | Description |
|-------|------|-------------|
| `part_number` | string | Unique part identifier |
| `name` | string | Human-readable part name |
| `category` | string | Part category (Motor, Pump, Seal, Cable, Sensor, Fitting, etc.) |
| `material` | string | Material composition |
| `weight_kg` | number | Weight in kilograms |
| `is_critical` | boolean | Whether the part is flagged as critical |
| `uom` | string | Unit of measure (ea, set, m) |

Availability flags, lead times, and sourcing status are **not stored** in the database. Do not infer or fabricate availability status.

## 7. BOM gap alerts

Generate alerts only for conditions that can be determined from database data:

- **Missing BOM**: `total_parts = 0` or `assembly_count = 0` for a recommended ESP. Report as `BOM_INCOMPLETE`.
- **No critical parts defined**: `critical_parts_count = 0` for an ESP that has parts. Report as `CRITICAL_PARTS_UNDEFINED` — this may indicate incomplete data entry.
- **Manual review required**: Always append a note that procurement readiness (availability, lead time) must be verified through external sourcing systems.

Each alert should include:
- `esp_id`
- `alert_type` (`BOM_INCOMPLETE` or `CRITICAL_PARTS_UNDEFINED`)
- `detail`

## 8. Required MCP tools and orchestration order

Use existing tools only:
- `list_esps`
- `get_esp`
- `get_esp_bom`
- `get_bom_summary`

Execution order:

1. Validate input.
2. Build recommendation set:
   - call `list_esps`
   - call `get_esp` as needed
   - compute ranking factors and order recommendations
3. For each recommendation:
   - call `get_esp_bom` — get flat parts list with `is_critical` per part
   - call `get_bom_summary` — get counts, weight, category breakdown
   - evaluate BOM completeness and identify critical parts
4. Produce final output template.

Do not call `get_part` for availability enrichment; the database does not store that data.

## 9. Output template for final report

```json
{
  "recommendations": [
    {
      "esp_id": "ESP-001",
      "fit_rank": 1,
      "flow_delta": 0.0,
      "power_headroom_kw": 5.0,
      "frequency_match": true,
      "fit_summary": "Exact flow match; power within budget; frequency compatible"
    }
  ],
  "bom_completeness_reports": [
    {
      "esp_id": "ESP-001",
      "bom_complete": true,
      "total_parts": 25,
      "critical_parts_count": 17,
      "critical_parts_percent": 68.0,
      "total_weight_kg": 312.5,
      "assembly_count": 9,
      "parts_by_category": {
        "Motor": 7,
        "Pump": 7,
        "Seal": 4,
        "Cable": 3,
        "Sensor": 4
      },
      "critical_parts_list": [
        { "part_number": "ESP-MTR-001", "name": "Main Motor Housing", "category": "Motor" },
        { "part_number": "ESP-PMP-001", "name": "Pump Housing", "category": "Pump" }
      ],
      "field_ready": "UNKNOWN — availability and lead-time data not present in database; external verification required"
    }
  ],
  "bom_alerts": [
    {
      "esp_id": "ESP-XXX",
      "alert_type": "BOM_INCOMPLETE",
      "detail": "No parts found in BOM; manual data entry review required"
    }
  ],
  "summary": "Top recommendation ESP-001 has an exact flow match and complete BOM with 17 critical parts identified. Field readiness requires external availability and lead-time verification."
}
```
