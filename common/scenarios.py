"""Scenario files (scenario-yaml skill): validation. The runner (`run`) arrives in R4.

uv run python -m common.scenarios validate scenarios/

Checks every `scenarios/S*.yaml` against `Scenario` (identity, layers, matched baseline, label),
that the baseline exists, that every candidate file exists and is a hypothetical line with a
generating rule and short-list ids, and that no hypothetical candidate appears in S0 or S1.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml

from common.schemas import Scenario

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def check(path: Path) -> list[str]:
    files = sorted(path.glob("S*.yaml")) if path.is_dir() else [path]
    errors: list[str] = []
    ids: dict[str, Scenario] = {}
    for f in files:
        try:
            s = Scenario.model_validate(yaml.safe_load(f.read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001 - report every file, not the first failure
            errors.append(f"{f}: {e}")
            continue
        ids[s.id] = s
    for sid, s in ids.items():
        if s.baseline and s.baseline not in ids and path.is_dir():
            errors.append(f"{sid}: baseline {s.baseline} not found")
        if sid in ("S0", "S1") and s.candidates:
            errors.append(f"{sid}: a fixed baseline may not list hypothetical candidates")
        for c in s.candidates:
            p = Path(c)
            if not p.exists():
                errors.append(f"{sid}: candidate {c} missing")
                continue
            line = yaml.safe_load(p.read_text(encoding="utf-8"))
            if line.get("layer") != "hypothetical":
                errors.append(f"{sid}: candidate {c} is not layer hypothetical")
            if not (line.get("rule_id") and line.get("generated_from_ids")):
                errors.append(f"{sid}: candidate {c} lacks rule_id / generated_from_ids")
            for base in ("S0", "S1"):
                if base in ids and line.get("id") in ids[base].lines.include:
                    errors.append(f"{sid}: candidate {line.get('id')} appears in {base}")
    return errors + ([] if files else [f"no scenario files under {path}"])


def check_mode_choice(path: Path) -> list[str]:
    """Every `mode_choice_params` file and each file it includes exist (repo-relative)."""
    from common import REPO_ROOT

    files = sorted(path.glob("S*.yaml")) if path.is_dir() else [path]
    errors: list[str] = []
    for f in files:
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        rel = doc.get("mode_choice_params")
        if not rel:
            continue
        target = REPO_ROOT / rel
        if not target.exists():
            errors.append(f"{f.name}: mode_choice_params {rel} missing")
            continue
        inc = (yaml.safe_load(target.read_text(encoding="utf-8")) or {}).get("include", [])
        missing = [i for i in inc if not (REPO_ROOT / i).exists()]
        errors += [f"{f.name}: {rel} includes missing {i}" for i in missing]
    return errors


@app.command()
def validate(path: Path = typer.Argument(Path("scenarios"))) -> None:
    """Validate scenario files; exit 1 on any error."""
    errors = check(path) + check_mode_choice(path)
    for e in errors:
        typer.echo(f"FAIL {e}")
    if errors:
        raise typer.Exit(1)
    n = len(list(path.glob("S*.yaml"))) if path.is_dir() else 1
    typer.echo(f"ok {n} scenario files")


@app.command()
def run() -> None:  # pragma: no cover - R4
    """Scenario runner (R4 onwards; not implemented at R2)."""
    raise typer.Exit("common.scenarios run arrives in R4")


if __name__ == "__main__":
    app()
