# Corporate LXP MCP Platform Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Install the package in development mode
RUN pip install -e .

# Expose ports
EXPOSE 9000 9001

# Default command
CMD ["python", "-m", "corporate_lxp_mcp.main"]
