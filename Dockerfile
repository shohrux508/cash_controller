# ============================================================
# Stage 1: Build dependencies
# ============================================================
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Copy application source
COPY . .

# ============================================================
# Stage 2: Production runtime
# ============================================================
FROM python:3.12-slim

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

WORKDIR /app

# Copy built application from builder
COPY --from=builder /app /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]
