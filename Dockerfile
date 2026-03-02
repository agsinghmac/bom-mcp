# Python MCP Server
# For Cloud Run deployment - use this for the Python-only MCP server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY esp_db.py api.py cli.py run_mcp.py mcp_server.py ./

# Create database directory
RUN mkdir -p /app/data

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run MCP server with StreamableHttp transport
CMD ["python", "run_mcp.py", "--port", "8080"]
