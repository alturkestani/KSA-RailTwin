import importlib

import pytest
from typer.testing import CliRunner

PACKAGES = [
    "rail",
    "network",
    "screening",
    "costs",
    "demand",
    "modechoice",
    "access",
    "economics",
    "funding",
    "optimise",
    "coupling",
    "api",
]
runner = CliRunner()


@pytest.mark.parametrize("pkg", PACKAGES)
def test_version_command(pkg: str) -> None:
    app = importlib.import_module(f"{pkg}.cli").app
    res = runner.invoke(app, ["--seed", "5", "version"])
    assert res.exit_code == 0, res.output
    assert res.output.startswith(f"{pkg} ksa-railtwin ") and "seed 5" in res.output
