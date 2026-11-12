"""CLI for `costs`: `version` plus the sub-apps `register`, `rcf`, `estimate`, `index`.

uv run python -m costs.cli version
uv run python -m costs.cli register validate
uv run python -m costs.cli rcf show
(each sub-app also runs directly: `uv run python -m costs.register ...`, `costs.rcf`,
`costs.estimate`)
"""

from common.cli import make_app
from costs import estimate, index_build, rcf, register

app = make_app(
    "costs",
    "Cost register, capex/opex estimates, lifecycle, financing, reference-class uplifts.",
)
app.add_typer(register.app, name="register")
app.add_typer(rcf.app, name="rcf")
app.add_typer(estimate.app, name="estimate")
app.add_typer(index_build.app, name="index")

if __name__ == "__main__":
    app()
