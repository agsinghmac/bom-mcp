# BOM-MCP

Electric Submersible Pump (ESP) Parts and Bill of Materials (BOM) database with REST API, CLI, and MCP interface.

## Features

- SQLite database with ESP parts, assemblies, and units
- REST API server (Flask)
- Command-line interface
- MCP server for AI assistants

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### REST API

```bash
python api.py [port]  # Default port: 5000
```

### CLI

```bash
python cli.py esp list
python cli.py esp get ESP-001
python cli.py esp bom ESP-001
python cli.py parts get ESP-MTR-001
python cli.py assemblies get ASM-MTR-001
```

### MCP Server

```bash
# stdio transport
python run_mcp.py

# SSE transport on port 8080
python run_mcp.py --port 8080
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/esp/<id>` | Full ESP with assemblies and parts |
| `GET /api/esp/<id>/bom` | Flat BOM parts list |
| `GET /api/esp/<id>/summary` | BOM summary (counts, weights) |
| `GET /api/parts/<pn>` | Single part details |
| `GET /api/assemblies/<code>` | Assembly with nested parts |

## Data Model

- **Parts**: Individual components (part_number, name, category, material, weight_kg, is_critical, uom)
- **Assemblies**: Groups of parts
- **ESP Units**: Top-level pumps linking assemblies

## Docker

### Local Development

```bash
# Build and run
docker-compose up --build

# API available at http://localhost:5000
```

### Google Cloud Run Deployment

1. **Build the container:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/bom-mcp
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy bom-mcp \
     --image gcr.io/PROJECT_ID/bom-mcp \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080
   ```

   Or deploy directly from source:
   ```bash
   gcloud run deploy bom-mcp \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## License

MIT