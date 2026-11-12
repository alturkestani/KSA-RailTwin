# ruff: noqa: E501
"""Alignment weights v2 (FIX_R7 item 4b): a parallel, versioned parameter set; v1 stays frozen.

v2 adds three priors, all from data already in the routing surface (Copernicus GLO-30, OSM ODbL):
a grade dead-band (A-align-101: grades below a fraction of the cap cost nothing; earthworks absorb
them), a straightness penalty on flat cells (A-align-102/103: distance to the station-to-station
chord), and re-opens the corridor bonus, the urban penalty and the grade smoothing length that v1
tuned. Diagnosis (`network.align_diag`, docs/alignments.md §4a) motivates each one.

Tuning is a full factorial grid evaluated once per (combination, line); then

- **leave-one-out**: for each validation line, the combination that minimises the objective
  (A-align-070: mean of mean offsets + 20 km x length error beyond ±5 %) on the OTHER two lines
  is applied to the held-out line, whose offset is the honest out-of-sample figure;
- **in-sample**: the combination that minimises the objective on all three lines becomes
  `align_weights_v2.yaml`, frozen with its SHA-256.

    uv run python -m network.align_v2 tune --seed 1 --workers 4          # runs/align/tune-v2-s1
    uv run python -m network.align_v2 write-weights                      # align_weights_v2.yaml + .sha256
    uv run python -m network.align validate --weights cities/ksa/assumptions/align_weights_v2.yaml --out runs/align/validation-v2-s1
    uv run python -m network.align_v2 loo-validate --seed 1              # runs/align/validation-v2-loo-s1
    uv run python -m network.align_v2 route --ids <id>,<id> --seed 1     # cities/ksa/alignments-v2/
    uv run python -m network.align_v2 table                              # docs/alignments-v2-tables.md

Label: hypothetical alignment (ours): indicative engineering sketch, not a design.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import canonical_json, seed_option, write_meta
from network import align as al

V2 = Path("cities/ksa/assumptions/align_weights_v2.yaml")
V1 = al.WEIGHTS
TUNE = Path("runs/align/tune-v2-s1")
SIDECARS_V2 = Path("cities/ksa/alignments-v2")
LINES = ("hhr", "sar-north-passenger", "sar-east-passenger")
# the grid (A-align-100); every key is a dotted path into the weights file
GRID: dict[str, list[Any]] = {
    "weights.grade_deadband": [0.0, 0.3, 0.6],
    "router.grade_smoothing_m": [500, 1000, 2000],
    "weights.straightness": [0.0, 0.05, 0.2],
    "weights.corridor_bonus": [0.0, 0.1],  # v1's 0.25 is the reference run (validation-s1)
    "weights.urban": [0.75, 1.5],
}
NEW_KEYS = {
    "grade_deadband": {"value": 0.0, "range": [0.0, 0.6], "assumption_id": "A-align-101"},
    "straightness": {"value": 0.0, "range": [0.0, 0.2], "assumption_id": "A-align-102"},
    "straightness_flat_relief_m": {"value": 40.0, "assumption_id": "A-align-103"},
}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Alignment weights v2 (FIX_R7)."""


def base_v2(root: Path = REPO_ROOT) -> dict[str, Any]:
    """v1 weights with the v2 keys added at their neutral values (routing identical to v1)."""
    w = copy.deepcopy(al.load_weights(root / V1, root))
    for k, v in NEW_KEYS.items():
        w["weights"][k] = dict(v)
    w["version"] = 2
    w["frozen"] = False
    return w


def combos() -> list[dict[str, Any]]:
    keys = list(GRID)
    return [dict(zip(keys, vals, strict=True)) for vals in itertools.product(*GRID.values())]


def apply(w: dict[str, Any], combo: dict[str, Any]) -> dict[str, Any]:
    for k, v in combo.items():
        w = al.set_dotted(w, k, v)
    return w


def _eval(args: tuple[int, str, str, int, str]) -> dict[str, Any]:
    ci, combo_json, lid, seed, root_s = args
    w = apply(base_v2(Path(root_s)), json.loads(combo_json))
    w["validation"]["lines"] = {lid: w["validation"]["lines"][lid]}
    df = al.validate_lines(w, Path(root_s), None, seed, structures=False)
    r = df.iloc[0]
    return {
        "combo": ci,
        "key": json.dumps(json.loads(combo_json), sort_keys=True),
        "line": lid,
        "length_error": float(r.length_error),
        "mean_offset_km": float(r.mean_offset_km),
        "hausdorff_km": float(r.hausdorff_km),
    }


def objective(rows: pd.DataFrame, tol: float = 0.05) -> float:
    """A-align-070 on the given lines: mean of the mean offsets + 20 km x |length error| beyond tol."""
    pen = 20.0 * np.maximum(0.0, rows.length_error.abs() - tol)
    return float(rows.mean_offset_km.mean() + pen.sum())


def select(grid: pd.DataFrame) -> dict[str, Any]:
    """Leave-one-out and in-sample choices from the evaluated grid."""
    folds = []
    for h in LINES:
        train = grid[grid.line != h]
        obj = train.groupby("combo").apply(objective, include_groups=False)
        best = int(obj.idxmin())
        held = grid[(grid.combo == best) & (grid.line == h)].iloc[0]
        folds.append(
            {
                "held_out": h,
                "combo": best,
                "train_objective": round(float(obj.min()), 4),
                "held_out_mean_offset_km": round(float(held.mean_offset_km), 3),
                "held_out_length_error": round(float(held.length_error), 4),
                "held_out_hausdorff_km": round(float(held.hausdorff_km), 3),
            }
        )
    obj = grid.groupby("combo").apply(objective, include_groups=False)
    return {
        "folds": folds,
        "in_sample_combo": int(obj.idxmin()),
        "in_sample_objective": round(float(obj.min()), 4),
    }


@app.command("tune")
def tune_cmd(
    seed: int = seed_option(),
    workers: int = typer.Option(4),
    out: Path = typer.Option(TUNE),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Evaluate the full grid on each validation line, then the leave-one-out and in-sample choices."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    o = out if out.is_absolute() else root / out
    o.mkdir(parents=True, exist_ok=True)
    cs = combos()
    done = pd.read_csv(o / "grid.csv") if (o / "grid.csv").exists() else pd.DataFrame()
    # results are cached by the combination's values (key), so a changed grid reuses them
    key_of = {json.dumps(c, sort_keys=True): i for i, c in enumerate(cs)}
    rows = []
    if len(done):
        for r in done.to_dict(orient="records"):
            if r.get("key") in key_of:
                rows.append(r | {"combo": key_of[r["key"]]})
    have = {(r["combo"], r["line"]) for r in rows}
    tasks = [
        (i, json.dumps(c), lid, seed, str(root))
        for i, c in enumerate(cs)
        for lid in LINES
        if (i, lid) not in have
    ]
    typer.echo(f"{len(cs)} combinations x {len(LINES)} lines; {len(tasks)} to run")
    with ProcessPoolExecutor(workers) as ex:
        futs = [ex.submit(_eval, t) for t in tasks]
        for k, f in enumerate(as_completed(futs)):
            rows.append(f.result())
            if k % 12 == 0 or k == len(futs) - 1:
                pd.DataFrame(rows).sort_values(["combo", "line"]).to_csv(
                    o / "grid.csv", index=False
                )
                typer.echo(f"{k + 1}/{len(futs)}")
    grid = pd.DataFrame(rows).sort_values(["combo", "line"])
    grid.to_csv(o / "grid.csv", index=False)
    pd.DataFrame([{"combo": i, **c} for i, c in enumerate(cs)]).to_csv(
        o / "combos.csv", index=False
    )
    sel = select(grid)
    sel["grid"] = GRID
    sel["combos"] = {str(f["combo"]): cs[f["combo"]] for f in sel["folds"]} | {
        str(sel["in_sample_combo"]): cs[sel["in_sample_combo"]]
    }
    (o / "chosen.json").write_text(json.dumps(sel, indent=1) + "\n")
    write_meta(
        o,
        seed,
        {"grid": GRID, "base": "align_weights.yaml v1 + v2 keys"},
        extra={"label": al.LABEL},
    )
    typer.echo(json.dumps(sel, indent=1))


def weights_from_combo(combo: dict[str, Any], root: Path) -> dict[str, Any]:
    return apply(base_v2(root), combo)


@app.command("write-weights")
def write_weights_cmd(
    tune: Path = typer.Option(TUNE),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write align_weights_v2.yaml from the in-sample choice, frozen, and its .sha256."""
    t = tune if tune.is_absolute() else root / tune
    sel = json.loads((t / "chosen.json").read_text())
    combo = sel["combos"][str(sel["in_sample_combo"])]
    w = weights_from_combo(combo, root)
    w["frozen"] = True
    w["tune_v2"] = {
        "method": "full factorial grid, leave-one-out over the three validation lines (A-align-100)",
        "grid": GRID,
        "run": str(TUNE),
        "in_sample_objective": sel["in_sample_objective"],
        "chosen": combo,
        "leave_one_out": sel["folds"],
    }
    head = (
        "# > **Document version:** cities/ksa/assumptions/align_weights_v2.yaml v1.0 | 4 Nov 2026 | "
        "Author: FIX_R7 builder (gis-network-engineer role) | Status: reviewed (tuned and frozen)\n"
        "# Alignment weights v2 (FIX_R7 item 4b): a PARALLEL set. v1 (align_weights.yaml, hash 2b718ecb...)\n"
        "# stays frozen and is what every R4-R7 figure uses. v2 = v1 + grade dead-band (A-align-101),\n"
        "# straightness on flat cells (A-align-102/103), and re-tuned corridor bonus / urban penalty /\n"
        "# grade smoothing, chosen by a leave-one-out grid on HHR, SAR North and SAR East\n"
        "# (network.align_v2; runs/align/tune-v2-s1). Adoption is Tariq's decision at the review.\n"
    )
    p = root / V2
    p.write_text(head + yaml.safe_dump(w, sort_keys=False, allow_unicode=True), encoding="utf-8")
    h = al.weights_hash(al.load_weights(p, root))
    (p.parent / "align_weights_v2.sha256").write_text(f"{h}  align_weights_v2.yaml\n")
    typer.echo(f"wrote {V2} hash {h}")


def load_v2(root: Path = REPO_ROOT) -> dict[str, Any]:
    w = al.load_weights(root / V2, root)
    h = (root / V2.parent / "align_weights_v2.sha256").read_text().split()[0]
    if al.weights_hash(w) != h:
        raise SystemExit("align_weights_v2.yaml does not match its .sha256")
    return w


@app.command("loo-validate")
def loo_validate_cmd(
    seed: int = seed_option(),
    tune: Path = typer.Option(TUNE),
    out: Path = typer.Option(Path("runs/align/validation-v2-loo-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route each held-out line with its fold's weights (trained on the other two), with structures."""
    t = tune if tune.is_absolute() else root / tune
    o = out if out.is_absolute() else root / out
    sel = json.loads((t / "chosen.json").read_text())
    rows = []
    for f in sel["folds"]:
        w = weights_from_combo(sel["combos"][str(f["combo"])], root)
        w["validation"]["lines"] = {f["held_out"]: w["validation"]["lines"][f["held_out"]]}
        df = al.validate_lines(w, root, o / f["held_out"], seed)
        rows.append(df.assign(fold_combo=f["combo"], fold_weights_hash=al.weights_hash(w)))
    df = pd.concat(rows, ignore_index=True)
    df.to_csv(o / "validation.csv", index=False)
    write_meta(o, seed, {"chosen": sel}, extra={"label": al.LABEL})
    typer.echo(df.to_string(index=False))


@app.command("route")
def route_cmd(
    ids: str = typer.Option(..., help="comma-separated corridor ids"),
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/align/corridors-v2-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Route corridors with weights v2 into runs/align/corridors-v2-s<seed>/ and write v2 sidecars
    under cities/ksa/alignments-v2/ (same schema as cities/ksa/alignments/, label unchanged)."""
    from screening.corridors import stations_key

    w = load_v2(root)
    o = out if out.is_absolute() else root / out
    files = {p.stem: p for p in al._corridor_files(root)}
    (root / SIDECARS_V2).mkdir(parents=True, exist_ok=True)
    for cid in ids.split(","):
        c = yaml.safe_load(files[cid].read_text(encoding="utf-8"))
        res = al.route_corridor(c, w, root)
        al.write_outputs(c, res, w, o / cid, seed, root)
        sm = json.loads((o / cid / "summary.json").read_text(encoding="utf-8"))
        sm |= {
            "status": "routed",
            "stations_key": stations_key(c["stations"]),
            "geojson": (SIDECARS_V2 / f"{cid}.geojson").as_posix(),
            "run": (o / cid).relative_to(root).as_posix(),
            "weights_hash": al.weights_hash(w),
            "weights_frozen": True,
            "weights_file": V2.as_posix(),
        }
        sm.pop("legs", None)
        (root / SIDECARS_V2 / f"{cid}.json").write_text(
            json.dumps(sm, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (root / SIDECARS_V2 / f"{cid}.geojson").write_bytes(
            (o / cid / "alignment.geojson").read_bytes()
        )
        side = sm
        v1 = json.loads((root / al.SIDECARS / f"{cid}.json").read_text())
        typer.echo(f"{cid}: {side['length_km']} km (v1 {v1['length_km']})")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


_ = canonical_json  # re-exported for callers hashing v2 metadata


# --------------------------------------------------------------------------- doc tables
DOC = Path("docs/alignments.md")
CAUSE_NAMES = {
    "within_1km": "within 1 km (DEM resolution, smoothing, OSM digitisation)",
    "urban_approach": "urban station approach (≤ 25 km of a station ≥ 15 % urban)",
    "avoids_urban": "urban penalty: real line runs through urban cells the router avoids",
    "grade_choice": "grade term: real line takes grades the surface penalises (flat ground)",
    "unseen_corridor": "corridor the surface cannot see (longer real line, no surface reason)",
    "lateral_freedom_flat": "flat-terrain lateral freedom (surface indifferent, ≤ 2 %)",
    "lateral_freedom_relief": "lateral freedom on relief (surface indifferent, ≤ 2 %)",
}


def _md(df: pd.DataFrame) -> list[str]:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return out


def tables(root: Path = REPO_ROOT) -> dict[str, list[str]]:
    """The generated blocks of docs/alignments.md (§4a, §4b, §4c) from the run outputs."""
    out: dict[str, list[str]] = {}
    d = root / "runs/align/diag-v1-s1"
    legs = pd.read_csv(d / "legs.csv")
    lc = pd.read_csv(d / "leg_causes.csv")
    piv = lc.pivot_table(
        index=["line", "leg"],
        columns="cause",
        values="contribution_km",
        aggfunc="sum",
        fill_value=0.0,
    )
    t = legs.set_index(["line", "leg"]).join(piv).reset_index()
    rows = []
    for _, r in t.iterrows():
        parts = [
            f"{CAUSE_NAMES[c].split(' (')[0].split(':')[0]} {r[c]:.2f}"
            for c in CAUSE_NAMES
            if c in t.columns and r[c] >= 0.005
        ]
        rows.append(
            {
                "line": r.line,
                "leg": f"{r['from']} → {r['to']}",
                "real km": f"{r.osm_km:.1f}",
                "routed km": f"{r.routed_km:.1f}",
                "leg mean offset km": f"{r.leg_mean_offset_km:.2f}",
                "surface cost real / routed": f"{r.cost_ratio:.3f}",
                "near a highway, real / routed": f"{r.osm_near_highway:.0%} / {r.routed_near_highway:.0%}",
                "median relief m": f"{r.median_relief_m:.0f}",
                "leg cause": r.leg_cause,
                "km of the line's mean offset, by cause": "; ".join(parts) or "0",
            }
        )
    out["4a-legs"] = _md(pd.DataFrame(rows))
    c = pd.read_csv(d / "causes.csv").set_index("line")
    rows = []
    for k, name in CAUSE_NAMES.items():
        rows.append(
            {
                "cause": name,
                **{ln: f"{c.loc[ln, k]:.2f}" if k in c.columns else "0.00" for ln in LINES},
            }
        )
    rows.append(
        {
            "cause": "**mean offset (sum)**",
            **{ln: f"**{c.loc[ln, 'mean_offset_km']:.3f}**" for ln in LINES},
        }
    )
    out["4a-causes"] = _md(pd.DataFrame(rows))
    v1 = pd.read_csv(root / "runs/align/validation-s1/validation.csv").set_index("line")
    v2 = pd.read_csv(root / "runs/align/validation-v2-s1/validation.csv").set_index("line")
    lo = pd.read_csv(root / "runs/align/validation-v2-loo-s1/validation.csv").set_index("line")
    rows = []
    for ln in LINES:
        for lab, src in (("v1 (frozen)", v1), ("v2 in-sample", v2), ("v2 held-out", lo)):
            r = src.loc[ln]
            rows.append(
                {
                    "line": ln,
                    "weights": lab,
                    "routed km": f"{r.routed_km:.1f}",
                    "length error": f"{r.length_error:+.1%}",
                    "mean offset km": f"{r.mean_offset_km:.2f}",
                    "Hausdorff km": f"{r.hausdorff_km:.1f}",
                    "P90 offset km": f"{r.p90_offset_km:.1f}",
                    "tunnel km (OSM)": f"{r.tunnel_km:.1f} ({r.osm_tunnel_km:.1f})",
                    "viaduct km (OSM bridge)": f"{r.viaduct_km:.1f} ({r.osm_bridge_km:.1f})",
                    "targets met": f"length {'yes' if r.length_ok else 'no'}, offset {'yes' if r.offset_ok else 'no'}",
                }
            )
    out["4b-validation"] = _md(pd.DataFrame(rows))
    sel = json.loads((root / TUNE / "chosen.json").read_text())
    rows = []
    for f in sel["folds"]:
        cb = sel["combos"][str(f["combo"])]
        rows.append(
            {
                "held-out line": f["held_out"],
                "trained on": ", ".join(x for x in LINES if x != f["held_out"]),
                "chosen (dead-band / smoothing m / straightness / corridor bonus / urban)": " / ".join(
                    str(cb[k])
                    for k in (
                        "weights.grade_deadband",
                        "router.grade_smoothing_m",
                        "weights.straightness",
                        "weights.corridor_bonus",
                        "weights.urban",
                    )
                ),
                "training objective km": f"{f['train_objective']:.3f}",
                "held-out mean offset km": f"{f['held_out_mean_offset_km']:.2f}",
            }
        )
    cb = sel["combos"][str(sel["in_sample_combo"])]
    rows.append(
        {
            "held-out line": "none (in-sample = weights v2)",
            "trained on": "all three",
            "chosen (dead-band / smoothing m / straightness / corridor bonus / urban)": " / ".join(
                str(cb[k])
                for k in (
                    "weights.grade_deadband",
                    "router.grade_smoothing_m",
                    "weights.straightness",
                    "weights.corridor_bonus",
                    "weights.urban",
                )
            ),
            "training objective km": f"{sel['in_sample_objective']:.3f}",
            "held-out mean offset km": "n/a",
        }
    )
    out["4b-loo"] = _md(pd.DataFrame(rows))
    cmpf = root / "runs/r7-v2/compare.json"
    if cmpf.exists():
        cm = json.loads(cmpf.read_text())["corridors"]
        rows = []
        for cid, r in cm.items():
            if not r.get("routed"):
                rows.append(
                    {
                        "corridor": f"`{cid}`",
                        "weights": "n/a",
                        "length km": "not routed",
                        "tunnel km": "",
                        "viaduct km": "",
                        "earthworks km": "",
                        "max formation grade": "",
                        "running time min": "",
                        "re-run": "no: " + r["note"],
                    }
                )
                continue
            for lab in ("v1", "v2"):
                x = r[lab]
                rows.append(
                    {
                        "corridor": f"`{cid}`",
                        "weights": lab,
                        "length km": f"{x['length_km']:.1f}",
                        "tunnel km": f"{x['tunnel_km']:.1f}",
                        "viaduct km": f"{x['viaduct_km']:.1f}",
                        "earthworks km": f"{x['earthworks_km']:.1f}",
                        "max formation grade": f"{x['formation_max_grade']:.4f}",
                        "running time min": f"{x['running_min']:.1f}",
                        "re-run": ""
                        if lab == "v1"
                        else (
                            ("yes" if r["rerun"] else "no")
                            + f" (length {r['change']['length']:+.1%}, tunnel + viaduct {r['change']['tunnel_plus_viaduct_km']:+.1%}, earthworks {r['change']['earthworks_km']:+.1%}, running time {r['change']['running_min']:+.1%})"
                        ),
                    }
                )
        out["4c-geometry"] = _md(pd.DataFrame(rows))
    sf = root / "runs/r7-v2/sensitivity.json"
    if sf.exists():
        s = json.loads(sf.read_text())
        rows = []
        for r in s["rows"]:
            if not r["moved"]:
                continue

            def ab(k: str, r: dict = r) -> str:
                a, b = r[k]
                return f"{a:,.0f} → {b:,.0f}"

            rows.append(
                {
                    "entity": f"`{r['entity']}`",
                    "robust NPV": ab("robust_npv"),
                    "capex P10 / P50 / P90": " / ".join(
                        ab(f"capex_{q}") for q in ("p10", "p50", "p90")
                    ),
                    "net fiscal cost 60 y, fully public, P10 / P50 / P90": " / ".join(
                        ab(f"nfc60_fully_public_sar_{q}") for q in ("p10", "p50", "p90")
                    ),
                    "net fiscal cost 60 y, availability PPP, P10 / P50 / P90": " / ".join(
                        ab(f"nfc60_ppp_dbfom_availability_{q}") for q in ("p10", "p50", "p90")
                    )
                    if "nfc60_ppp_dbfom_availability_p50" in r
                    else "n/a",
                    "VfM (% of PSC)": f"{ab('vfm')} ({r['vfm_pct_psc'][0]:.1f} % → {r['vfm_pct_psc'][1]:.1f} %)",
                }
            )
        unmoved = [r["entity"] for r in s["rows"] if not r["moved"]]
        out["4c-figures"] = _md(pd.DataFrame(rows)) + [
            "",
            "Unchanged (no routed corridor re-run in them): "
            + ", ".join(f"`{u}`" for u in unmoved)
            + ".",
        ]
    return out


def write_doc_blocks(root: Path = REPO_ROOT) -> int:
    """Replace each `<!-- gen:<key> -->` ... `<!-- /gen:<key> -->` block of docs/alignments.md."""
    import re

    p = root / DOC
    s = p.read_text(encoding="utf-8")
    n = 0
    for k, lines in tables(root).items():
        pat = re.compile(
            rf"(<!-- gen:{re.escape(k)} -->\n)(?:.*?\n)?(<!-- /gen:{re.escape(k)} -->)", re.S
        )
        if pat.search(s):
            s = pat.sub(lambda m, lines=lines: m.group(1) + "\n".join(lines) + "\n" + m.group(2), s)
            n += 1
    p.write_text(s, encoding="utf-8")
    return n


@app.command("table")
def table_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Regenerate the §4a/§4b/§4c tables inside docs/alignments.md from the run outputs."""
    typer.echo(f"{write_doc_blocks(root)} blocks written in {DOC}")


if __name__ == "__main__":
    app()
