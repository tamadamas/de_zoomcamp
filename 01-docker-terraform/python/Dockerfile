FROM python:3.13-slim-trixie as build

COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim-trixie as runtime

ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /app -s /bin/false appuser

WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app .

USER appuser

# ENTRYPOINT ["python", "ingest_data.py"]
ENTRYPOINT ["bash"]
