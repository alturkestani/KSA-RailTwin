"""Shared typer app factory: every package CLI takes `--seed` and has a `version` command.

uv run python -m <pkg>.cli version
uv run python -m <pkg>.cli --seed 7 version
"""

from __future__ import annotations

import importlib.metadata as md
import tomllib

import typer

from common import REPO_ROOT
from common.runmeta import code_version, seed_option


def project_version() -> str:
    try:
        return md.version("ksa-railtwin")
    except md.PackageNotFoundError:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        return data["project"]["version"]


def make_app(package: str, help_text: str) -> typer.Typer:
    app = typer.Typer(add_completion=False, help=help_text, no_args_is_help=True)

    @app.callback()
    def main(ctx: typer.Context, seed: int = seed_option()) -> None:
        ctx.obj = {"seed": seed}

    @app.command()
    def version(ctx: typer.Context) -> None:
        """Print package, project version, code version and seed."""
        seed = (ctx.obj or {}).get("seed")
        typer.echo(f"{package} ksa-railtwin {project_version()} code {code_version()} seed {seed}")

    return app
