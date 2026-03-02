# Use Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY esp_db.py api.py cli.py run_mcp.py mcp_server.py http_server.py ./

# Create database directory
RUN mkdir -p /app/data

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run HTTP REST wrapper server
CMD ["python", "http_server.py", "--port", "8080"]