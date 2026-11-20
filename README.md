# Project portfolio

## Usage

This app should be used! 

## Local development

Log in with your own Azure account, and add this to `.env` instead of `FABRIC_SECRET`:

```
AZURE_SQL_AUTH=cli
```

```bash
az login
```

The database and Microsoft Graph then use your own account, so it needs access to both.
Without this setting the app uses the service principal, as it does in the container apps.

`CLIENT_SECRET` is still needed: it belongs to the Entra login in the browser, which `az login` doesn't replace.

### Running the app

Install the dependencies once:

```bash
uv sync
```

Then run the backend and the frontend from the repo root, each in its own terminal.

Backend, on http://localhost:8000:

```bash
uv run python -m uvicorn backend.api_main:api_app --host 0.0.0.0 --port 8000 --reload
```

Frontend, on http://localhost:8080:

```bash
uv run python -m frontend.app
```

Open http://localhost:8080 in the browser.
