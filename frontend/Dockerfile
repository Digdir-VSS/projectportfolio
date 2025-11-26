FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /.

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --python python3.13

COPY frontend ./frontend
COPY backend ./backend
COPY models ./models

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --python python3.13

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

# If frontend/app.py is the entrypoint
CMD ["uv", "run", "--no-sync", "-m", "frontend.app"]
