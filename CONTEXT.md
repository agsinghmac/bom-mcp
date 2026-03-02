# ESP Motor — MCP Server Context

## MCP Server

- **Name**: `esp-motor`
- **Description**: Electric Submersible Pump (ESP) Parts and Bill of Materials database
- **Transport**: stdio

## Available Tools

### ESP
| Tool | Key Params |
|------|------------|
| `list_esps` | — |
| `get_esp` | `esp_id` |
| `get_esps_by_series` | `series` |
| `create_esp` | `esp_id`, `model_name`, `series`, `power_rating_kw`, `voltage_v`, `frequency_hz`, `flow_rate_m3d`, `stages`, `cable_length_m` |
| `update_esp` | `esp_id` + any fields |
| `delete_esp` | `esp_id` |
| `add_assembly_to_esp` | `esp_id`, `assembly_code` |
| `remove_assembly_from_esp` | `esp_id`, `assembly_code` |

### BOM
| Tool | Key Params |
|------|------------|
| `get_esp_bom` | `esp_id` → flat parts list with `quantity` |
| `get_bom_summary` | `esp_id` → `{ total_parts, total_weight_kg, critical_count }` |

### Parts
| Tool | Key Params |
|------|------------|
| `list_parts` | — |
| `get_part` | `part_number` |
| `get_parts_by_category` | `category` |
| `get_critical_parts` | — |
| `get_part_assemblies` | `part_number` |
| `search_parts` | `query` |
| `create_part` | `part_number`, `name`, `category`, `material`, `weight_kg`, `is_critical?` |
| `update_part` | `part_number` + any fields |
| `delete_part` | `part_number`, `force?` |

### Assemblies
| Tool | Key Params |
|------|------------|
| `list_assemblies` | — |
| `get_assembly` | `assembly_code` |
| `get_assembly_esps` | `assembly_code` |
| `create_assembly` | `assembly_code`, `name` |
| `delete_assembly` | `assembly_code`, `force?` |
| `add_part_to_assembly` | `assembly_code`, `part_number` |
| `remove_part_from_assembly` | `assembly_code`, `part_number` |
| `update_assembly_part_quantity` | `assembly_code`, `part_number`, `quantity` |

### System
| Tool | Key Params |
|------|------------|
| `get_stats` | — → `{ total_esps, total_parts, total_assemblies, critical_parts }` |
| `get_server_info` | — |

## Data Model

```typescript
interface ESP {
  esp_id: string;         // "ESP-010"
  model_name: string;     // "DeepWell 1500"
  series: string;         // "DeepWell"
  power_rating_kw: number;
  voltage_v: number;
  frequency_hz: number;
  flow_rate_m3d: number;
  stages: number;
  cable_length_m: number;
}

interface Part {
  part_number: string;    // "ESP-MTR-001"
  name: string;
  category: string;
  material: string;
  weight_kg: number;
  is_critical: boolean;
  uom: string;            // "ea" | "set" | "m"
  quantity?: number;      // present in BOM context
}

interface Assembly {
  assembly_code: string;  // "ASM-MTR-001"
  name: string;
  parts: Part[];
}
```

## Reference Data

**Series**: RedZone Pro · AquaMax · HydroLift · PowerPump · DeepWell

**Part categories**: Motor · Pump · Seal · Cable · Sensor · Fitting · Bearing · Valve

**Baseline counts**: 10 ESPs · 10 Assemblies · 30 Parts · 23 Critical Parts