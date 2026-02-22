# BOM-MCP

Electric Submersible Pump (ESP) Parts and Bill of Materials (BOM) database with MCP server for AI assistants.

## Features

- SQLite database with ESP parts, assemblies, and units
- MCP server (SSE transport) for AI assistants
- Command-line interface
- REST API server (optional)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### MCP Server (SSE transport - default)

```bash
python run_mcp.py --port 8080
```

### REST API (optional)

```bash
python api.py [port]  # Default port: 5000
```

### CLI

```bash
# List ESPs and assemblies
python cli.py esp list
python cli.py esp get ESP-001
python cli.py esp bom ESP-001

# Manage parts
python cli.py parts get ESP-MTR-001
python cli.py parts list

# Manage assemblies
python cli.py assemblies get ASM-MTR-001
python cli.py assemblies list

# Update part quantities in BOMs
python cli.py assemblies update-quantity ASM-MTR-002 ESP-SEL-001 5
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_esps` | List all ESP pump models |
| `get_esp` | Get complete ESP with assemblies and parts |
| `get_esp_bom` | Get flat BOM parts list for an ESP |
| `get_bom_summary` | Get BOM summary (weight, counts, critical) |
| `get_parts_by_category` | Filter parts by category |
| `get_critical_parts` | List all critical parts |
| `get_assembly` | Get assembly with its parts |
| `update_assembly_part_quantity` | Update quantity of a part in an assembly |
| And more... |

## Data Model

- **Parts**: Individual components (part_number, name, category, material, weight_kg, is_critical, uom)
- **Assemblies**: Groups of parts with quantities (assembly_code, name, parts)
- **ESP Units**: Top-level pumps linking assemblies

Each part in an assembly has a `quantity` field that can be updated to reflect real-world assembly requirements.

## Docker

### Local Development

```bash
# Build and run MCP server on port 8080
docker-compose up --build

# MCP server available at http://localhost:8080
```

### Google Cloud Run Deployment

```bash
# Deploy directly from source
gcloud run deploy bom-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

The MCP server will be available at your Cloud Run URL.

## License

MIT