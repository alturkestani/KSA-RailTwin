"""R5 CP5 H4a helpers (screening-analyst): sidecar summary for the whole routed set, and the
before/after tables of the corridor set. Label: screening input, not a forecast; routed
alignments are indicative, not designs.

  uv run python scripts/r5_h4a.py summary [--corridors cities/ksa/corridors]
      [--sidecars cities/ksa/alignments] [--out cities/ksa/alignments/summary.csv]
  uv run python scripts/r5_h4a.py diff --before-ref HEAD --out runs/r5/screening/h4a

`network.align apply --corridors-dir <dir> --only`-style runs write summary.csv with only the rows
they applied; `summary` rebuilds it for every routed corridor in the set, in the order and with the
columns `network.align apply` uses (same rows as one apply over the full set).
"""

from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path

import pandas as pd
import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)
COLS = (
    "id",
    "line_type",
    "length_km",
    "straight_km_legs",
    "detour_ratio",
    "tunnel_km",
    "viaduct_km",
    "earthworks_km",
    "restricted_km",
    "min_curve_kmh",
    "profile_feasible",
)
FAMS = ["trunk_gap", "branch_spur", "commuter_belt", "station_addition"]


def _rows(ids: list[str], read) -> pd.DataFrame:
    return pd.DataFrame([{k: read(i).get(k) for k in COLS} for i in ids])


@app.command()
def summary(
    corridors: Path = typer.Option(Path("cities/ksa/corridors")),
    sidecars: Path = typer.Option(Path("cities/ksa/alignments")),
    out: Path = typer.Option(Path("cities/ksa/alignments/summary.csv")),
) -> None:
    files = sorted(p for p in corridors.rglob("*.yaml") if "station_addition" not in p.parts)
    ids = [yaml.safe_load(p.read_text(encoding="utf-8"))["id"] for p in files]
    df = _rows(ids, lambda i: json.loads((sidecars / f"{i}.json").read_text(encoding="utf-8")))
    df.to_csv(out, index=False)
    typer.echo(f"{len(df)} rows in {out}")


def _git(ref: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"], check=True, capture_output=True, text=True
    ).stdout


def _set_at(ref: str | None) -> dict[str, dict]:
    if ref is None:
        return {
            c["id"]: c
            for c in (
                yaml.safe_load(p.read_text(encoding="utf-8"))
                for p in sorted(Path("cities/ksa/corridors").rglob("*.yaml"))
            )
        }
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "cities/ksa/corridors"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    return {
        c["id"]: c for c in (yaml.safe_load(_git(ref, n)) for n in names if n.endswith(".yaml"))
    }


@app.command()
def diff(
    before_ref: str = typer.Option("HEAD"),
    out: Path = typer.Option(Path("runs/r5/screening/h4a")),
) -> None:
    old, new = _set_at(before_ref), _set_at(None)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in FAMS:
        o = {i for i, c in old.items() if c["family"] == f}
        n = {i for i, c in new.items() if c["family"] == f}

        def chg(i: str) -> bool:
            a, b = old[i], new[i]
            key = [(s["id"], s["lat"], s["lon"]) for s in a["stations"]]
            return key != [(s["id"], s["lat"], s["lon"]) for s in b["stations"]]

        same = o & n
        rows.append(
            {
                "family": f,
                "before": len(o),
                "after": len(n),
                "added": len(n - o),
                "removed": len(o - n),
                "same_id_same_stations": sum(not chg(i) for i in same),
                "same_id_stations_changed": sum(chg(i) for i in same),
            }
        )
    pd.DataFrame(rows).to_csv(out / "family_counts.csv", index=False)
    ids = []
    for i in sorted(set(old) | set(new)):
        st = "added" if i not in old else "removed" if i not in new else "unchanged"
        if st == "unchanged":
            a = [(s["id"], s["lat"], s["lon"]) for s in old[i]["stations"]]
            b = [(s["id"], s["lat"], s["lon"]) for s in new[i]["stations"]]
            st = "unchanged" if a == b else "stations changed"
        c = new.get(i) or old[i]
        before = " > ".join(s["id"] for s in old[i]["stations"]) if i in old else ""
        after = " > ".join(s["id"] for s in new[i]["stations"]) if i in new else ""
        ids.append(
            {
                "id": i,
                "family": c["family"],
                "change": st,
                "stations_before": before,
                "stations_after": after,
            }
        )
    pd.DataFrame(ids).to_csv(out / "id_changes.csv", index=False)
    routed = []
    for i, c in sorted(new.items()):
        r = c.get("alignment_routed") or {}
        if r.get("status") != "routed":
            continue
        routed.append(
            {
                "id": i,
                "family": c["family"],
                "line_type": c["line_type"],
                "routed_km": r.get("length_km"),
                "straight_km": r.get("straight_km_legs"),
                "detour_ratio": r.get("detour_ratio"),
                "tunnel_km": r.get("tunnel_km"),
                "viaduct_km": r.get("viaduct_km"),
                "profile_feasible": r.get("profile_feasible"),
                "run": r.get("run"),
                "weights_hash": r.get("weights_hash"),
            }
        )
    pd.DataFrame(routed).to_csv(out / "routed.csv", index=False)
    typer.echo(pd.DataFrame(rows).to_string(index=False))


@app.command("check-summary")
def check_summary(ref: str = typer.Option("HEAD")) -> None:
    """Rebuild summary.csv at a git ref from that ref's corridors and sidecars; compare bytes."""
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "cities/ksa/corridors"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    files = sorted(n for n in names if n.endswith(".yaml") and "/station_addition/" not in n)
    ids = [yaml.safe_load(_git(ref, n))["id"] for n in files]
    df = _rows(ids, lambda i: json.loads(_git(ref, f"cities/ksa/alignments/{i}.json")))
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    same = buf.getvalue() == _git(ref, "cities/ksa/alignments/summary.csv")
    typer.echo(f"{ref}: rebuilt summary.csv identical to the tracked one: {same}")
    if not same:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
