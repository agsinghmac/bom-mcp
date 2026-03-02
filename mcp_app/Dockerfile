# Node.js MCP App Server (UI layer)
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY server.ts ./
COPY resources/ ./resources/

# Expose port
EXPOSE 8080

# Run MCP App server
CMD ["node", "server.ts"]
