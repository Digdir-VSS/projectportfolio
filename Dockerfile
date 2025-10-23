FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl gnupg2 unixodbc unixodbc-dev libgssapi-krb5-2 && \
    rm -rf /var/lib/apt/lists/*

# Add Microsoft repo for Debian 12 (bookworm/trixie compatible)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="$PATH:/opt/mssql-tools18/bin"

WORKDIR /.

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --python python3.13

COPY . .

COPY .hidden_config ./.hidden_config

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --python python3.13

ENV PATH="/.venv/bin:$PATH"

EXPOSE 8080

CMD ["python", "app.py"]
