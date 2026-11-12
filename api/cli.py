"""CLI for `api`: `version` and `serve` (the dashboard API plus the built web app).

uv run python -m api.cli serve --port 8765
uv run python -m api.cli serve --data-root tests/fixtures/api \
    --runs-root tests/fixtures/api/run_outputs
"""

from __future__ import annotations

import os

import typer

from common.cli import make_app

app = make_app(
    "api", "API for the decision dashboard (FastAPI pattern from TrafficTwin; no API keys)."
)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8765, "--port"),
    data_root: str = typer.Option("", "--data-root", help="RAILTWIN_DATA_ROOT (default repo)"),
    runs_root: str = typer.Option("", "--runs-root", help="RAILTWIN_RUNS_ROOT (default runs/)"),
) -> None:
    """Serve the API and web/dist (build it first: cd web && npm run build)."""
    import uvicorn

    if data_root:
        os.environ["RAILTWIN_DATA_ROOT"] = data_root
    if runs_root:
        os.environ["RAILTWIN_RUNS_ROOT"] = runs_root
    uvicorn.run("api.main:app", host=host, port=port)


if __name__ == "__main__":
    app()
