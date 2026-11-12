"""CLI for `funding`: `version`, plus the options register and the risk-matrix template.

uv run python -m funding.cli models-validate
uv run python -m funding.cli risk-validate [--path ...]
"""

from pathlib import Path

import typer

from common.cli import make_app
from funding import models, risk_matrix

app = make_app(
    "funding", "Funding, ownership and delivery models; risk allocation; fiscal exposure."
)


@app.command("models-validate")
def models_validate(path: Path = typer.Option(models.DEFAULT_PATH, "--path", exists=True)) -> None:
    """Validate cities/ksa/funding/models.yaml (same as `python -m funding.models validate`)."""
    models.validate(path=path, sources_dir=models.SOURCES_DIR)


@app.command("risk-validate")
def risk_validate(
    path: Path = typer.Option(risk_matrix.DEFAULT_PATH, "--path", exists=True),
) -> None:
    """Validate a risk-matrix YAML (same as `python -m funding.risk_matrix validate`)."""
    risk_matrix.validate(path=path, sources_dir=risk_matrix.SOURCES_DIR)


if __name__ == "__main__":
    app()
