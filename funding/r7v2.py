# ruff: noqa: E501
"""R7 figures under alignment weights v2: a reported sensitivity (FIX_R7 item 4c), never the base.

The R7 base figures (runs/r6, runs/r7, docs/delivery-models.md, docs/fiscal-exposure.md,
recommendations.yaml) stay on the frozen v1 alignments. This module re-runs the chain for the CP7
corridors that v2 moves materially, into parallel run folders:

1. `compare`: v1 vs v2 sidecar (cities/ksa/alignments vs cities/ksa/alignments-v2) per routed CP7
   corridor: length, tunnel / viaduct / earthworks km, max formation grade, end-to-end running time
   (access.running_time on the corridor YAML with the routed km-posts and curve limits). A corridor
   is re-run when length moves by more than 2 % or tunnel + viaduct or earthworks km by more than 5 %
   (prompts/FIX_R7.md item 4c).
2. `costs`: the corridor YAML with the v2 sidecar applied (screening.corridors.apply_alignment,
   A-align-080) -> network.evaluate.costing_input -> costs.estimate (seed 1, 10,000 draws) into
   runs/costs-v2/<id>/ (the control re-costs the v1 YAML and must match runs/costs/<id>/).
3. `overlay`: an APFS clone of the frozen judge root judge/v3-variants at runs/r7-v2/judge-root,
   with ONLY the affected corridors' input files substituted (corridor YAML, alignment sidecar,
   runs/costs/<id>, runs/network-eval/costing/<id>*.yaml). Every other file is hash-checked against
   the frozen judge; the judge's code is untouched (its own `optimise.judge verify` still passes).
4. `score`: the judge's own entry point run from the overlay root: each affected corridor standalone
   at its CP7 phase into runs/r7/corridors-v2/<id>@<phase>/ and every CP7 layout containing one,
   with all cases, into runs/r7-v2/top5/<L>/.
5. `fiscal`: funding.fiscal and funding.vfm with those scores (funding.inputs.OVERRIDES) into
   runs/r7-v2/fiscal/ and runs/r7-v2/vfm/, and runs/r7-v2/sensitivity.json: before/after of every R7
   figure that moved (robust NPV, capex P10/P50/P90, net fiscal cost P10/P50/P90 60 y, VfM).

    uv run python -m funding.r7v2 compare | costs | overlay | control | score | fiscal | all

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import write_meta
from funding import inputs

OUT = Path("runs/r7-v2")
JUDGE = "v3-variants"
SIDE_V1 = Path("cities/ksa/alignments")
SIDE_V2 = Path("cities/ksa/alignments-v2")
COSTS_V2 = Path("runs/costs-v2")
CORR_V2 = Path("runs/r7/corridors-v2")
LEN_TOL = 0.02  # prompts/FIX_R7.md item 4c
STRUCT_TOL = 0.05
LAYOUT_IDS = {"L1": "S6-L1", "L2": "S6-L2", "L3": "S6-L3"}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R7 alignment-v2 sensitivity (FIX_R7 item 4c)."""


def corridor_file(cid: str, root: Path = REPO_ROOT) -> Path:
    hits = sorted((root / "cities/ksa/corridors").glob(f"*/{cid}.yaml"))
    if len(hits) != 1:
        raise FileNotFoundError(cid)
    return hits[0]


def cp7_corridors(root: Path = REPO_ROOT) -> dict[str, int]:
    return inputs.corridor_phases(root)


def running_minutes(c: dict[str, Any], root: Path = REPO_ROOT) -> float:
    """End-to-end all-stop in-vehicle minutes from the R4 running-time model."""
    from access import running_time as rt

    run = rt.build_run(c, root)
    ids = run.stations.id.tolist()
    tab = rt.pair_table(run, ids)
    row = tab[(tab["from"] == ids[0]) & (tab.to == ids[-1])]
    return round(float(row.ivt_min.iloc[0]), 2)


def v2_yaml(cid: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    from screening.corridors import apply_alignment

    c = yaml.safe_load(corridor_file(cid, root).read_text(encoding="utf-8"))
    return apply_alignment(c, root / SIDE_V2)


def _pct(a: float, b: float) -> float | None:
    return None if a == 0 else round(b / a - 1.0, 4)


@app.command("compare")
def compare_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> dict[str, Any]:
    """v1 vs v2 per CP7 corridor; decide which ones are re-run (runs/r7-v2/compare.json)."""
    from screening.corridors import apply_alignment

    rows = {}
    for cid, ph in cp7_corridors(root).items():
        c = yaml.safe_load(corridor_file(cid, root).read_text(encoding="utf-8"))
        if c.get("family") == "station_addition":
            rows[cid] = {
                "phase": ph,
                "routed": False,
                "note": "station addition on existing or committed track: not routed (docs/alignments.md §7 decision 4); weights v1/v2 do not apply",
            }
            continue
        s1 = json.loads((root / SIDE_V1 / f"{cid}.json").read_text())
        s2 = json.loads((root / SIDE_V2 / f"{cid}.json").read_text())
        c1 = apply_alignment(c, root / SIDE_V1)
        c2 = apply_alignment(c, root / SIDE_V2)
        if c1 != c:
            raise SystemExit(
                f"{cid}: re-applying the v1 sidecar does not reproduce the corridor YAML"
            )
        m1, m2 = running_minutes(c1, root), running_minutes(c2, root)
        st1 = float(s1["tunnel_km"]) + float(s1["viaduct_km"])
        st2 = float(s2["tunnel_km"]) + float(s2["viaduct_km"])
        r = {
            "phase": ph,
            "routed": True,
            "line_type": s1["line_type"],
            "v1": {
                k: s1[k]
                for k in (
                    "length_km",
                    "tunnel_km",
                    "viaduct_km",
                    "earthworks_km",
                    "formation_max_grade",
                    "weights_hash",
                    "run",
                )
            }
            | {"running_min": m1},
            "v2": {
                k: s2[k]
                for k in (
                    "length_km",
                    "tunnel_km",
                    "viaduct_km",
                    "earthworks_km",
                    "formation_max_grade",
                    "weights_hash",
                    "run",
                )
            }
            | {"running_min": m2},
            "change": {
                "length": _pct(float(s1["length_km"]), float(s2["length_km"])),
                "tunnel_plus_viaduct_km": _pct(st1, st2),
                "tunnel_plus_viaduct_km_abs": round(st2 - st1, 3),
                "earthworks_km": _pct(float(s1["earthworks_km"]), float(s2["earthworks_km"])),
                "running_min": _pct(m1, m2),
            },
        }
        ch = r["change"]
        r["rerun"] = bool(
            abs(ch["length"] or 0) > LEN_TOL
            or abs(ch["tunnel_plus_viaduct_km"] or 0) > STRUCT_TOL
            or abs(ch["earthworks_km"] or 0) > STRUCT_TOL
        )
        rows[cid] = r
    out = {
        "label": LABEL,
        "thresholds": {"length": LEN_TOL, "structure_km": STRUCT_TOL},
        "corridors": rows,
    }
    (root / OUT).mkdir(parents=True, exist_ok=True)
    (root / OUT / "compare.json").write_text(json.dumps(out, indent=1) + "\n")
    typer.echo(json.dumps(rows, indent=1))
    return out


def rerun_ids(root: Path = REPO_ROOT) -> list[str]:
    d = json.loads((root / OUT / "compare.json").read_text())
    return [k for k, v in d["corridors"].items() if v.get("rerun")]


def _estimate(spec: dict, costing: dict, out: Path, root: Path, seed: int = 1) -> None:
    out.mkdir(parents=True, exist_ok=True)
    sp, cp = out / "spec.yaml", out / "costing.yaml"
    sp.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
    cp.write_text(yaml.safe_dump(costing, sort_keys=False), encoding="utf-8")
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "costs.estimate",
            "--corridor",
            str(sp),
            "--costing",
            str(cp),
            "--seed",
            str(seed),
            "--draws",
            "10000",
            "--out",
            str(out),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])


@app.command("costs")
def costs_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """R5 cost estimate on the v2 corridor YAML (runs/costs-v2/<id>/), with a v1 control that must
    reproduce runs/costs/<id>/distribution.parquet."""
    import pandas as pd

    from network.evaluate import costing_input

    for cid in rerun_ids(root):
        c1 = yaml.safe_load(corridor_file(cid, root).read_text(encoding="utf-8"))
        s1, k1 = costing_input(c1, root)
        ref_spec = yaml.safe_load((root / "runs/network-eval/costing" / f"{cid}.yaml").read_text())
        ref_cost = yaml.safe_load(
            (root / "runs/network-eval/costing" / f"{cid}.costing.yaml").read_text()
        )
        if s1 != ref_spec or k1 != ref_cost:
            raise SystemExit(
                f"{cid}: costing_input on the v1 YAML differs from runs/network-eval/costing"
            )
        ctl = root / OUT / "control-costs" / cid
        _estimate(s1, k1, ctl, root)
        a = pd.read_parquet(ctl / "distribution.parquet")
        b = pd.read_parquet(root / "runs/costs" / cid / "distribution.parquet")
        if not a.equals(b):
            raise SystemExit(f"{cid}: v1 control cost run differs from runs/costs/{cid}")
        c2 = v2_yaml(cid, root)
        (root / OUT / "corridors").mkdir(parents=True, exist_ok=True)
        (root / OUT / "corridors" / f"{cid}.yaml").write_text(
            yaml.safe_dump(c2, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        s2, k2 = costing_input(c2, root)
        _estimate(s2, k2, root / COSTS_V2 / cid, root)
        typer.echo(f"{cid}: v1 control identical; v2 costed into {COSTS_V2 / cid}")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _files(base: Path) -> dict[str, str]:
    out = {}
    for p in sorted(base.rglob("*")):
        if p.is_symlink():
            out[str(p.relative_to(base))] = "link:" + os.readlink(p)
        elif p.is_file():
            out[str(p.relative_to(base))] = _sha(p)
    return out


def substitutions(cid: str, root: Path) -> dict[str, Path]:
    """judge-root relative path -> source of the v2 file."""
    rel = corridor_file(cid, root).relative_to(root)
    return {
        str(rel): root / OUT / "corridors" / f"{cid}.yaml",
        f"cities/ksa/alignments/{cid}.json": root / SIDE_V2 / f"{cid}.json",
        f"cities/ksa/alignments/{cid}.geojson": root / SIDE_V2 / f"{cid}.geojson",
        f"runs/network-eval/costing/{cid}.yaml": root / COSTS_V2 / cid / "spec.yaml",
        f"runs/network-eval/costing/{cid}.costing.yaml": root / COSTS_V2 / cid / "costing.yaml",
        f"runs/costs/{cid}": root / COSTS_V2 / cid,
    }


@app.command("overlay")
def overlay_cmd(
    substitute: bool = typer.Option(True, help="False: an unmodified clone (control)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> Path:
    """APFS clone of judge/v3-variants with the v2 inputs substituted; hash-checked."""
    from optimise import judge as jd

    src = jd.judge_root(JUDGE, root)
    dst = root / OUT / ("judge-root" if substitute else "judge-root-control")
    if dst.exists():
        subprocess.run(["chmod", "-R", "u+w", str(dst)], check=True)
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-cR", str(src), str(dst)], check=True)
    subprocess.run(["chmod", "-R", "u+w", str(dst)], check=True)
    subs: dict[str, str] = {}
    if substitute:
        for cid in rerun_ids(root):
            for rel, s in substitutions(cid, root).items():
                t = dst / rel
                if s.is_dir():
                    shutil.rmtree(t)
                    shutil.copytree(s, t)
                else:
                    t.write_bytes(s.read_bytes())
                subs[rel] = str(s.relative_to(root))
    a, b = _files(src), _files(dst)
    changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    allowed = [k for k in changed if any(k == r or k.startswith(r + "/") for r in subs)]
    if set(changed) != set(allowed):
        raise SystemExit(
            f"overlay differs outside the substitutions: {sorted(set(changed) - set(allowed))[:10]}"
        )
    code = [k for k in changed if k.endswith(".py")]
    if code:
        raise SystemExit(f"overlay changed judge code: {code}")
    subprocess.run(["chmod", "-R", "a-w", str(dst)], check=True)
    rec = {
        "label": LABEL,
        "frozen_judge": str(src.relative_to(root)),
        "frozen_judge_sha256": jd.load_record(JUDGE, root)["sha256"],
        "files_total": len(b),
        "files_changed": changed,
        "substitutions": subs,
        "identical_outside_substitutions": True,
    }
    (root / OUT / f"{dst.name}.json").write_text(json.dumps(rec, indent=1) + "\n")
    typer.echo(
        f"{dst.relative_to(root)}: {len(changed)} files changed, all inside {len(subs)} substitutions"
    )
    return dst


def run_judge(
    jroot: Path, layout: dict[str, Any], out: Path, root: Path, extra: tuple[str, ...] = ()
) -> dict[str, Any]:
    """The frozen judge's own entry point, run from an overlay root (optimise.search.run_judge with
    R6_JUDGE_ROOT pointed at the overlay); meta records the overlay."""
    from optimise import judge as jd

    out.mkdir(parents=True, exist_ok=True)
    lay = out / "layout.yaml"
    lay.write_text(yaml.safe_dump(layout, sort_keys=False))
    env = dict(os.environ, R6_JUDGE_ROOT=str(jroot))
    env.pop("PYTHONPATH", None)
    r = subprocess.run(
        [
            str(root / ".venv/bin/python"),
            str(jroot / "optimise/layout.py"),
            "evaluate",
            "--layout",
            str(lay.resolve()),
            "--out",
            str(out.resolve()),
            "--workers",
            "4",
            *extra,
        ],
        cwd=jroot,
        env=env,
        capture_output=True,
        text=True,
    )
    (out / "judge.log").write_text(r.stdout + "\n" + r.stderr[-20000:])
    if r.returncode:
        raise RuntimeError(f"judge failed: {r.stderr[-1500:]}")
    rec = jd.load_record(JUDGE, root)
    ov = json.loads((root / OUT / f"{jroot.name}.json").read_text())
    write_meta(
        out,
        1,
        {"layout": layout, "judge_args": list(extra)},
        extra={
            "label": LABEL,
            "judge": JUDGE,
            "judge_sha256": rec["sha256"],
            "judge_commit": rec["commit"],
            "judge_root": str(jroot.relative_to(root)),
            "overlay_substitutions": ov["substitutions"],
            "alignment_weights": "v2 (cities/ksa/assumptions/align_weights_v2.yaml)"
            if ov["substitutions"]
            else "v1 (control)",
        },
    )
    m = json.loads((out / "meta.json").read_text())
    m["harness_code_version"] = m.get("code_version")
    m["code_version"] = (
        f"judge {rec['name']} @ {rec['commit'][:10]} sha256 {rec['sha256'][:16]} (overlay {jroot.name})"
    )
    (out / "meta.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    return json.loads((out / "score.json").read_text())


def _same_score(a: dict, b: dict) -> bool:
    drop = {"seconds"}
    return {k: v for k, v in a.items() if k not in drop} == {
        k: v for k, v in b.items() if k not in drop
    }


@app.command("control")
def control_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """The overlay mechanism on unmodified inputs must reproduce R7's standalone score."""
    jr = overlay_cmd(substitute=False, root=root)
    cid = rerun_ids(root)[0]
    ph = cp7_corridors(root)[cid]
    lay = yaml.safe_load((root / "runs/r7/corridors" / f"{cid}@{ph}" / "layout.yaml").read_text())
    s = run_judge(jr, lay, root / OUT / "control" / f"{cid}@{ph}", root)
    ref = json.loads((root / inputs.corridor_score_path(cid, ph, root)).read_text())
    ok = _same_score(s, ref)
    (root / OUT / "control" / "result.json").write_text(
        json.dumps({"corridor": cid, "identical_except_seconds": ok}, indent=1) + "\n"
    )
    typer.echo(
        f"control {cid}@{ph}: {'identical' if ok else 'DIFFERENT'} to {inputs.corridor_score_path(cid, ph, root).relative_to(root)}"
    )
    if not ok:
        raise typer.Exit(1)


@app.command("score")
def score_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Standalone corridor scores and every CP7 layout that contains a re-run corridor."""
    jr = root / OUT / "judge-root"
    ids = rerun_ids(root)
    ph = cp7_corridors(root)
    for cid in ids:
        lay = (
            yaml.safe_load(
                (root / "runs/r7/corridors" / f"{cid}@{ph[cid]}" / "layout.yaml").read_text()
            )
            if (root / "runs/r7/corridors" / f"{cid}@{ph[cid]}").exists()
            else None
        )
        if lay is None:
            lay = {
                "id": f"R7-{cid}@{ph[cid]}",
                "layer": "hypothetical",
                "base": "S1",
                "source": "funding.r7v2",
                "corridors": [{"id": cid, "phase": ph[cid]}],
            }
        lay = lay | {"source": "funding.r7v2 (alignment weights v2 sensitivity; FIX_R7 item 4c)"}
        s = run_judge(jr, lay, root / CORR_V2 / f"{cid}@{ph[cid]}", root)
        typer.echo(f"{cid}@{ph[cid]}: robust NPV {s['robust_npv']:.0f} ({LABEL})")
    for L, sid in LAYOUT_IDS.items():
        sc = inputs.scenario(L, root)
        if not {c["id"] for c in sc["layout"]["corridors"]} & set(ids):
            continue
        lay = {
            "id": sid,
            "layer": "hypothetical",
            "base": "S1",
            "source": f"scenarios/{sid}.yaml (alignment weights v2 sensitivity)",
            "corridors": [
                {"id": c["id"], "phase": int(c["phase"])} for c in sc["layout"]["corridors"]
            ],
        }
        s = run_judge(jr, lay, root / OUT / "top5" / L, root, ("--all-cases",))
        typer.echo(f"{sid}: robust NPV {s['robust_npv']:.0f} ({LABEL})")


def overrides(root: Path = REPO_ROOT) -> dict[str, Path]:
    ph = cp7_corridors(root)
    o = {cid: root / CORR_V2 / f"{cid}@{ph[cid]}" / "score.json" for cid in rerun_ids(root)}
    for L in LAYOUT_IDS:
        p = root / OUT / "top5" / L / "score.json"
        if p.exists():
            o[L] = p
    return o


def _r(x: float | None, n: int = 1) -> float | None:
    return None if x is None else round(float(x), n)


@app.command("fiscal")
def fiscal_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """fiscal.json and vfm.json on the v2 scores; sensitivity.json with every moved figure."""
    from funding import fiscal, vfm

    ov = overrides(root)
    inputs.OVERRIDES.clear()
    inputs.OVERRIDES.update(ov)
    try:
        params = fiscal.load_params()
        fis2 = fiscal.build_all(params, root)
        vfm2 = vfm.build_all(params, root)
    finally:
        inputs.OVERRIDES.clear()
    for d, sub in ((fis2, "fiscal"), (vfm2, "vfm")):
        o = root / OUT / sub
        o.mkdir(parents=True, exist_ok=True)
        (o / f"{sub}.json").write_text(json.dumps(d, indent=1, default=float) + "\n")
        write_meta(
            o,
            1,
            params,
            extra={
                "label": LABEL,
                "score_overrides": {k: str(v.relative_to(root)) for k, v in ov.items()},
            },
        )
    fis1 = json.loads((root / "runs/r7/fiscal/fiscal.json").read_text())
    vfm1 = json.loads((root / "runs/r7/vfm/vfm.json").read_text())
    rp = fis1["robust_case"]
    rows, lines = [], {}
    for grp in ("corridors", "programmes"):
        for k in fis1[grp]:
            b1, b2 = fis1[grp][k]["basis"], fis2[grp][k]["basis"]
            v1, v2 = vfm1[grp][k]["central"], vfm2[grp][k]["central"]
            rec = {
                "entity": k,
                "group": grp,
                "robust_npv": [_r(b1["robust_npv"]), _r(b2["robust_npv"])],
            }
            for q in ("p10", "p50", "p90"):
                rec[f"capex_{q}"] = [_r(b1["capex"][q]), _r(b2["capex"][q])]
            for m in ("fully_public_sar", "ppp_dbfom_availability"):
                if m in fis1[grp][k]["models"]:
                    n1 = fis1[grp][k]["models"][m]["by_pop"][rp]["net_fiscal_cost_60y"]
                    n2 = fis2[grp][k]["models"][m]["by_pop"][rp]["net_fiscal_cost_60y"]
                    for q in ("p10", "p50", "p90"):
                        rec[f"nfc60_{m}_{q}"] = [_r(n1[q]), _r(n2[q])]
            rec["vfm"] = [_r(v1["vfm"]), _r(v2["vfm"])]
            rec["vfm_pct_psc"] = [_r(v1["vfm_pct_psc"], 2), _r(v2["vfm_pct_psc"], 2)]
            moved = {f: v for f, v in rec.items() if isinstance(v, list) and v[0] != v[1]}
            rec["moved"] = sorted(moved)
            rows.append(rec)
            if moved:
                np1, np2 = rec["robust_npv"]
                c1, c2 = rec["capex_p50"]
                f1, f2 = rec["nfc60_fully_public_sar_p50"]
                lines[k] = (
                    f"Under weights v2 (not adopted): robust NPV {np1:,.0f} → {np2:,.0f}, capex P50 {c1:,.0f} → {c2:,.0f}, "
                    f"fully public net fiscal cost 60 y P50 {f1:,.0f} → {f2:,.0f} SAR m ({(f2 / f1 - 1) * 100:+.1f} %); VfM sign "
                    f"{'unchanged' if (rec['vfm'][0] > 0) == (rec['vfm'][1] > 0) else 'CHANGES'}."
                )
    if lines:
        lines["vfm"] = (
            "Under weights v2 (not adopted) the VfM of "
            + ", ".join(
                f"{r['entity']} moves {r['vfm'][0]:,.0f} → {r['vfm'][1]:,.0f}"
                for r in rows
                if r["entity"] in lines
            )
            + "; every sign is "
            + (
                "unchanged."
                if all((r["vfm"][0] > 0) == (r["vfm"][1] > 0) for r in rows)
                else "NOT unchanged."
            )
        )
    out = {
        "label": LABEL,
        "robust_case": rp,
        "alignment_weights": "v2 vs v1",
        "rows": rows,
        "lines": lines,
        "overrides": {k: str(v.relative_to(root)) for k, v in ov.items()},
    }
    (root / OUT / "sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")
    typer.echo(json.dumps(lines, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    app()
