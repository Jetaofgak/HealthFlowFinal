# Python build stage - using uv for faster package installation
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_HTTP_TIMEOUT=300

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5004

# Run app
CMD ["python", "app.py"]
