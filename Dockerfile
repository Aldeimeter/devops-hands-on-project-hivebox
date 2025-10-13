# Base stage - shared dependencies and setup
FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:e41e1e3bfa549df25a9786a0f5ee64b021500d61e3cda41f251c60ebde1e3a90 AS base

WORKDIR /api

# Copy dependency files
COPY hivebox-python/data ./data
COPY hivebox-python/pyproject.toml hivebox-python/uv.lock ./

ENV APP_VERSION="0.2.0"

# Test stage - includes dev dependencies and tests
FROM base AS test

# Install ALL dependencies (including dev)
RUN uv sync --frozen --no-cache

# Copy application code AND tests
COPY hivebox-python/main.py .
COPY hivebox-python/app ./app
COPY hivebox-python/tests ./tests

# Run tests by default
CMD ["/api/.venv/bin/pytest", "tests/", "-v"]

# Production stage - minimal, no tests
FROM base AS production

LABEL maintainer="aldeimeter666@gmail.com" \
      version="0.2.0" \
      description="HiveBox API"

# Install only production dependencies
RUN uv sync --frozen --no-cache --no-dev

# Security: non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /api

USER appuser

# Copy only application code
COPY hivebox-python/main.py .
COPY hivebox-python/app ./app

ENTRYPOINT ["/api/.venv/bin/fastapi", "run", "/api/main.py", "--port", "80", "--host", "0.0.0.0"]
