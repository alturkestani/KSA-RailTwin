"""All film tools under one CLI.

uv run python -m film.cli --help
uv run python -m film.cli script validate film/script/
uv run python -m film.cli shots check film/storyboard/shots.yaml --lines film/script/lines.csv
uv run python -m film.cli rights check film/rights_log.csv
uv run python -m film.cli subs check film/subs/
"""

from __future__ import annotations

import typer

from film import assemble, render, rights, script, shots, subs, voice

app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="KSA Rail Twin film tools (W10)."
)
app.add_typer(script.app, name="script")
app.add_typer(shots.app, name="shots")
app.add_typer(rights.app, name="rights")
app.add_typer(subs.app, name="subs")
app.add_typer(voice.app, name="voice")
app.add_typer(render.app, name="render")
app.add_typer(assemble.app, name="assemble")


if __name__ == "__main__":
    app()
