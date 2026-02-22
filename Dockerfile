# Use Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY esp_db.py api.py cli.py run_mcp.py mcp_server.py ./

# Create database directory
RUN mkdir -p /app/data

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "api:app"]
