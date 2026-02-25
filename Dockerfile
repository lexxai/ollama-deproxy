ARG PYTHON_VERSION=3.14

# Stage 1: Builder (install dependencies)
FROM python:${PYTHON_VERSION} AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --link-mode=copy --locked --no-group dev

# Stage 2: Runtime (slim image)
FROM python:${PYTHON_VERSION}-slim

ARG _USER=appuser
ARG _GROUP=appgroup

WORKDIR /app

# Copy virtual environment and project files
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/pyproject.toml ./

# Create non-root user/group
RUN groupadd -r ${_GROUP} && useradd -r --no-log-init -g ${_GROUP} -s /usr/sbin/nologin ${_USER}

# Copy source and scripts (set permissions +x on entrypoint)
COPY --chown=${_USER}:${_GROUP} ./src ./src/
COPY --chmod=+x ./entrypoint.sh ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin:$PATH \
    VIRTUAL_ENV=/app/.venv \
    PYTHONPATH=/app/src

# Switch to non-root user
USER ${_USER}

# Entrypoint: run server using uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]