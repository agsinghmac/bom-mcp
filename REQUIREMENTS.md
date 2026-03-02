# ESP Motor BOM Manager — Requirements Specification

## 1. Purpose & Context

An **MCP Apps UI** layer on top of the `esp-motor` MCP server. UI panels render **inline inside the chat conversation** in Claude Desktop / Claude.ai — not as a separate web application.

Target users: Petroleum/mechanical engineers and procurement teams who interact with the LLM to inspect, configure, and manage ESP pump compositions.

---

## 2. MCP Apps (Views) to Build

### 2.1 Dashboard View (`view_dashboard` tool)

**Trigger**: User asks "show me the ESP dashboard" or "give me an overview"

**Content:**
- Stats tiles: Total ESPs, Total Parts, Total Assemblies, Critical Parts count (from `get_stats`)
- Critical parts alert panel: red-highlighted list of all critical parts (from `get_critical_parts`)
- Quick search bar: search parts by name/category/material (calls `search_parts`, results shown inline)
- ESP series summary: count of ESPs per series with color-coded badges

**Tool calls available from this View:**
- `search_parts` (search bar)
- `get_critical_parts` (refresh button)
- `get_stats` (refresh button)

---

### 2.2 ESP Catalogue View (`view_esp_catalogue` tool)

**Trigger**: User asks "show ESP catalogue", "list all ESPs", "show pumps"

**Content:**
- ESP cards or table: ESP ID, Model Name, Series (badge), Power (kW), Flow Rate (m³/d), Stages, Voltage, Frequency, Cable Length
- Filter by series: dropdown using `get_esps_by_series`
- Create ESP button: opens inline form modal with all required fields
- Delete ESP: confirm dialog per row

**Tool calls available from this View:**
- `list_esps` (initial load + refresh)
- `get_esps_by_series` (series filter)
- `create_esp` (create form submission)
- `delete_esp` (delete confirmation)
- `view_esp_bom` (navigate to BOM view for a selected ESP)

**Create ESP Form Fields:**

| Field | Type | Required |
|-------|------|----------|
| ESP ID | text (ESP-XXX) | ✅ |
| Model Name | text | ✅ |
| Series | text | ✅ |
| Power Rating (kW) | number | ✅ |
| Voltage (V) | number | ✅ |
| Frequency (Hz) | number | ✅ |
| Flow Rate (m³/d) | number | ✅ |
| Stages | integer | ✅ |
| Cable Length (m) | number | ✅ |

---

### 2.3 BOM Viewer View (`view_esp_bom` tool)

**Trigger**: User asks "show BOM for ESP-010", "what parts are in ESP-003"

**Content:**
- ESP selector (if esp_id not provided by tool input)
- BOM summary card: total parts, total weight (kg), critical part count (from `get_bom_summary`)
- Full BOM table:
  - Columns: Part Number, Name, Category (badge), Material, Qty, UOM, Weight (kg), Critical (badge)
  - Totals row: sum of weight
  - Sort by any column
  - Highlight critical rows in red/amber
- Export CSV button (client-side generation from displayed data)
- Print layout option

**Tool calls available from this View:**
- `get_esp_bom` (load/refresh)
- `get_bom_summary` (summary card)

---

### 2.4 Parts Manager View (`manage_parts` tool)

**Trigger**: User asks "manage parts", "show parts catalogue", "add a new part"

**Content:**
- Searchable, filterable parts table:
  - Columns: Part Number, Name, Category (badge), Material, Weight (kg), UOM, Critical
  - Search via `search_parts`
  - Category filter (multi-select) via `get_parts_by_category`
  - "Critical only" toggle via `get_critical_parts`
- Expandable row or detail panel: shows which assemblies use this part (`get_part_assemblies`)
- Create part: slide-in form panel
- Edit part: inline edit on row
- Delete part: confirm dialog with option to force-remove from assemblies

**Create/Edit Part Form Fields:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Part Number | text | ✅ | Format: ESP-XXX-000 |
| Name | text | ✅ | |
| Category | select | ✅ | Motor, Pump, Seal, Cable, Sensor, Fitting, Bearing, Valve |
| Material | text | ✅ | |
| Weight (kg) | number | ✅ | |
| Is Critical | toggle | ❌ | Default: false |

**Tool calls available from this View:**
- `list_parts`, `search_parts`, `get_parts_by_category`, `get_critical_parts`
- `get_part_assemblies` (expandable row)
- `create_part`, `update_part`, `delete_part`

---

### 2.5 Assembly Manager View (`manage_assemblies` tool)

**Trigger**: User asks "manage assemblies", "show assemblies", "add part to assembly"

**Content:**
- Assembly cards/list: code, name, part count, total weight
- Expand assembly: show parts table with quantity
  - Edit part quantity (`update_assembly_part_quantity`)
  - Remove part button (`remove_part_from_assembly`)
  - Add part: searchable part picker (`add_part_to_assembly`)
- "Used in ESPs" indicator per assembly: shows which ESPs reference this assembly (`get_assembly_esps`)
- Create assembly: form with code + name fields
- Delete assembly: confirm dialog; if used in ESPs, show a warning listing affected ESPs (from `get_assembly_esps`) with optional force-delete

**Create Assembly Form Fields:**

| Field | Type | Required |
|-------|------|----------|
| Assembly Code | text (ASM-XXX-000) | ✅ |
| Name | text | ✅ |

**Tool calls available from this View:**
- `list_assemblies`, `get_assembly`, `get_assembly_esps`
- `create_assembly`, `delete_assembly`
- `add_part_to_assembly`, `remove_part_from_assembly`, `update_assembly_part_quantity`
- `list_parts` (part picker search)

---

## 3. Visual Design

### Aesthetic Direction
Industrial/engineering aesthetic — this is a tool for field engineers, not a SaaS dashboard.

- **Theme**: Dark by default (charcoal backgrounds, not pure black)
- **Typography**: Monospace font (`font-mono`) for all IDs, part numbers, codes; clean sans-serif for labels
- **Density**: Compact; engineers need to see data, not whitespace
- **Color system**:
  - Critical: `#ef4444` (red) — always visible, never subtle
  - Assembly: `#22c55e` (green)
  - ESP: `#3b82f6` (blue)
  - Series badges: RedZone Pro=red, AquaMax=cyan, HydroLift=teal, PowerPump=amber, DeepWell=violet

### Constraints (MCP Apps iframe context)
- Views render in a sandboxed iframe — **no external API calls** except through `app.callTool()`
- No `localStorage` or `sessionStorage` — use React state only
- Self-contained HTML: all CSS and JS bundled into the single HTML file
- Keep bundle size reasonable — avoid heavy charting libraries unless needed
- Views should be **responsive within the iframe width** — not full-page layouts

---

## 4. UX Standards

| Pattern | Requirement |
|---------|-------------|
| Loading states | Skeleton loaders on initial data fetch; spinner on mutations |
| Error states | Inline error message with retry button (not just console.log) |
| Empty states | Helpful message + CTA when no data |
| DELETE | Always confirm with modal showing what will be deleted |
| Mutations | Show success toast after create/update/delete |
| Sort | Columns sortable client-side after data loads |
| Critical rows | Always visually distinct (red left border or background tint) |
| IDs | Part numbers, ESP IDs, assembly codes always in monospace |
| Weights | Always displayed to 1 decimal place with "kg" suffix |
| Graceful degradation | Tool returns plain text summary if host doesn't support MCP Apps |

---

## 5. Graceful Degradation (Text Fallback)

Each UI-enabled tool must also return a meaningful text result for hosts that don't support MCP Apps. Example for `view_esp_bom`:

```
BOM for ESP-010 (DeepWell 1500)
Total parts: 29 | Total weight: 397.8 kg | Critical parts: 20

Part Number    | Name                  | Qty | Weight
ESP-MTR-001   | Main Motor Housing    |  1  | 45.0 kg [CRITICAL]
...
Use Claude Desktop or Claude.ai to view the interactive BOM table.
```

---

## 6. Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| Node.js | v18 or higher |
| Build output | Each View is a single self-contained HTML file in `dist/` |
| Transport | Supports both stdio (Claude Desktop) and StreamableHTTP |
| TypeScript | Strict mode throughout |
| Error handling | All `app.callTool()` calls wrapped in try/catch with UI error states |

---

## 7. Out of Scope (v1)

- User authentication
- Real-time collaborative editing
- 3D model visualization of pump assemblies
- Inventory / stock level tracking
- Procurement / ordering workflows
- Audit log / change history