FROM python:3.10-slim

ENV ENV_MODE production
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    pandoc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create virtual environment
RUN uv venv /app/.venv

# Copy dependencies file
COPY pyproject.toml ./

# Install dependencies but exclude problematic asyncio packages
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv uv sync --quiet

# Remove the problematic asyncio packages after installation
RUN uv pip uninstall pytest-asyncio nest-asyncio daytona-api-client-async -y || echo "Some packages not found"

# Remove any asyncio package that might have been installed
RUN uv pip uninstall asyncio -y || echo "asyncio package not found"

# Remove asyncio directories completely
RUN rm -rf /app/.venv/lib/python3.10/site-packages/asyncio* || echo "No asyncio directories found"
RUN rm -rf /app/.venv/lib/python3.10/site-packages/nest_asyncio* || echo "No nest_asyncio directories found"

# Install hypercorn as an alternative to uvicorn
RUN uv pip install hypercorn

# Verify we're using system asyncio
RUN uv run python -c "import asyncio; print('Using asyncio from:', asyncio.__file__)"

# Copy application code
COPY . .

# Set environment variables for virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/app/.venv/lib/python3.10/site-packages:/app"

# Calculate optimal worker count based on available resources
ENV WORKERS=8
ENV THREADS=2
ENV WORKER_CONNECTIONS=2000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the full FastAPI application with direct server
CMD ["python", "simple_server.py"]
