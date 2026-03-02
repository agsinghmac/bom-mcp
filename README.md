# BOM-MCP

Electric Submersible Pump (ESP) Parts and Bill of Materials (BOM) database with MCP server for AI assistants.

## Features

- SQLite database with ESP parts, assemblies, and units
- MCP server (SSE transport) for AI assistants
- **MCP Apps UI** - Interactive views that render inside Claude Desktop/Claude.ai
- Command-line interface
- REST API server (optional)

## Installation

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies for MCP Apps UI
cd mcp_app && npm install
```

## Usage

### Architecture

The system consists of two parts:
1. **Python MCP Server** - Core database and tools
2. **Node.js MCP App Server** - UI layer that wraps Python server

### Full Stack (Recommended)

```bash
# Terminal 1: Start Python MCP server on port 3001
python run_mcp.py --port 3001

# Terminal 2: Start MCP App UI server on port 8080
cd mcp_app && npm run serve
# Or with custom port: PORT=8081 npm run serve
```

### Python MCP Server Only (CLI/REST)

```bash
# SSE transport (default for MCP)
python run_mcp.py --port 8080

# REST API (optional)
python api.py [port]  # Default port: 5000
```

### CLI Commands

```bash
python cli.py esp list
python cli.py esp get ESP-001
python cli.py esp bom ESP-001
python cli.py parts get ESP-MTR-001
python cli.py assemblies get ASM-MTR-001
```

## MCP Apps UI Views

The MCP Apps layer provides 5 interactive views that render inside Claude Desktop/Claude.ai:

| View | Tool | Description |
|------|------|-------------|
| Dashboard | `view_dashboard` | Stats tiles, critical parts alert, series summary |
| ESP Catalogue | `view_esp_catalogue` | ESP cards with filter, create, delete |
| BOM Viewer | `view_esp_bom` | BOM table with sorting, export CSV |
| Parts Manager | `manage_parts` | Parts table with search, filters, CRUD |
| Assembly Manager | `manage_assemblies` | Assembly cards with parts management |

### Using Views

Trigger views by asking Claude:
- "Show me the ESP dashboard"
- "Show ESP catalogue"
- "Show BOM for ESP-001"
- "Manage parts"
- "Manage assemblies"

## MCP Tools

### ESP Tools
| Tool | Description |
|------|-------------|
| `list_esps` | List all ESP pump models |
| `get_esp` | Get complete ESP with assemblies and parts |
| `get_esp_bom` | Get flat BOM parts list for an ESP |
| `get_bom_summary` | Get BOM summary (weight, counts, critical) |
| `get_esps_by_series` | Filter ESPs by series |
| `create_esp`, `update_esp`, `delete_esp` | ESP CRUD operations |

### Parts Tools
| Tool | Description |
|------|-------------|
| `list_parts` | List all parts |
| `get_part` | Get part details |
| `search_parts` | Search parts by query |
| `get_parts_by_category` | Filter by category |
| `get_critical_parts` | List critical parts |
| `create_part`, `update_part`, `delete_part` | Parts CRUD |

### Assembly Tools
| Tool | Description |
|------|-------------|
| `list_assemblies` | List all assemblies |
| `get_assembly` | Get assembly with parts |
| `get_assembly_esps` | Find ESPs using assembly |
| `add_part_to_assembly`, `remove_part_from_assembly` | Manage assembly parts |
| `update_assembly_part_quantity` | Update part quantities |

### System Tools
| Tool | Description |
|------|-------------|
| `get_stats` | Database statistics |
| `get_server_info` | Server information |

## Data Model

- **Parts**: Individual components (part_number, name, category, material, weight_kg, is_critical, uom)
- **Assemblies**: Groups of parts
- **ESP Units**: Top-level pumps linking assemblies

## Docker

### Local Development

```bash
# Build and run both services
docker-compose up --build

# Python MCP server: http://localhost:3001
# MCP App UI: http://localhost:8080
```

### Google Cloud Run Deployment

```bash
# Deploy Python MCP server
gcloud run deploy bom-mcp-server \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## License

MIT