FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System deps for SQL Server
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl gnupg2 unixodbc unixodbc-dev libgssapi-krb5-2 && \
    rm -rf /var/lib/apt/lists/*

# MS SQL drivers
RUN curl https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="$PATH:/opt/mssql-tools18/bin"

WORKDIR /.

# Copy lockfiles first for layer caching
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --python python3.13

# Copy only backend code (and any shared modules)
COPY backend ./backend
COPY models ./models

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --python python3.13

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# IMPORTANT: CMD must be split into args, not one string
CMD ["uv", "run", "--no-sync", "uvicorn", "backend.api_main:api_app", "--host", "0.0.0.0", "--port", "8000"]

