# Use Python runtime
FROM python:3.11-slim

# Capture git SHA at build time
# Pass with: docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD)
ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY esp_db.py api.py cli.py run_mcp.py mcp_server.py skill_resource_manager.py version.py ./
COPY .skills/ .skills/

# Create database directory
RUN mkdir -p /app/data

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run FastMCP native streamable-http server
CMD ["python", "run_mcp.py", "--port", "8080"]