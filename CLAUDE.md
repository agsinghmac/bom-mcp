# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Electric Submersible Pump (ESP) Parts and Bill of Materials (BOM) database with REST API, CLI, and MCP interface.

## Commands

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for MCP Apps UI
cd mcp_app && npm install

# Run the REST API server
python api.py [port]  # Default port: 5000

# Use CLI commands
python cli.py esp list
python cli.py esp get ESP-001
python cli.py esp bom ESP-001
python cli.py parts get ESP-MTR-001
python cli.py assemblies get ASM-MTR-001

# Run Python MCP server (stdio transport)
python run_mcp.py

# Run Python MCP server (HTTP transport on port 3001)
python run_mcp.py --port 3001

# Run MCP Apps UI server (wraps Python server)
cd mcp_app && npm run serve
# Or with custom port: PORT=8081 npm run serve

# Get help
python cli.py --help
```

## Architecture

- `esp_db.py` - Self-contained SQLite database module
  - `ESPDatabase` class manages all CRUD operations
  - Tables: `parts`, `assemblies`, `assembly_parts`, `esp_units`, `esp_assemblies`
  - Includes 10 sample ESPs with realistic specifications

- `api.py` - Flask REST API
  - Endpoints for parts, assemblies, and ESP/BOM queries
  - Run `python api.py` to start server on port 5000

- `cli.py` - Command-line interface for database queries

- `mcp_server.py` - FastMCP server providing tools for AI assistants
  - Run `python run_mcp.py` to start

- `mcp_app/` - Node.js MCP Apps UI layer
  - TypeScript server that wraps the Python MCP server
  - Provides 5 interactive UI views for Claude Desktop/Claude.ai
  - Resources in `mcp_app/resources/`

## MCP Apps UI Views

Five interactive views render inside Claude Desktop/Claude.ai:

| View | Tool | Description |
|------|------|-------------|
| Dashboard | `view_dashboard` | Stats tiles, critical parts alert, series summary |
| ESP Catalogue | `view_esp_catalogue` | ESP cards with filter, create, delete |
| BOM Viewer | `view_esp_bom` | BOM table with sorting, CSV export |
| Parts Manager | `manage_parts` | Parts table with search, filters, CRUD |
| Assembly Manager | `manage_assemblies` | Assembly cards with parts management |

Trigger views by asking:
- "Show me the ESP dashboard"
- "Show ESP catalogue"
- "Show BOM for ESP-001"
- "Manage parts"
- "Manage assemblies"

## Data Model

- **Parts**: Individual components with part_number, name, category, material, weight, critical flag
- **Assemblies**: Groups of parts (e.g., "Main Motor Assembly")
- **ESP Units**: Top-level pumps linking assemblies (10 sample models across 5 series)

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/esp/<id>` | Full ESP with assemblies and all parts |
| `GET /api/esp/<id>/bom` | Flat BOM parts list |
| `GET /api/esp/<id>/summary` | BOM summary (counts, weights) |
| `GET /api/parts/<pn>` | Single part details |
| `GET /api/assemblies/<code>` | Assembly with nested parts |

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_esps` | List all ESP pump models |
| `get_esp` | Get complete ESP with assemblies and parts |
| `get_esp_bom` | Get flat BOM parts list for an ESP |
| `get_bom_summary` | Get BOM summary (weight, counts, critical) |
| `get_esps_by_series` | Filter ESPs by series name |
| `list_parts` | List all parts |
| `get_part` | Get part details by part number |
| `search_parts` | Search parts by query |
| `get_parts_by_category` | Filter parts by category |
| `get_critical_parts` | List all critical parts |
| `list_assemblies` | List all assemblies |
| `get_assembly` | Get assembly with its parts |
| `get_stats` | Get database statistics |

Plus full CRUD tools for creating, updating, and deleting ESPs, parts, and assemblies.
