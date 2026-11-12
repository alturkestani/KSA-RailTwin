"""R6_V3 (CP7-3): the variant library and the search over corridors x variants x phases.

  uv run python -m optimise.variants enumerate                   # <R6_OUT>/library/variants.json
  uv run python -m optimise.variants library --stage 1           # single-field variants
  uv run python -m optimise.variants library --stage 2           # combinations (A-r6-103)
  uv run python -m optimise.variants milp                        # <R6_OUT>/milp/
  uv run python -m optimise.variants ga --budget B2 --seed 1     # <R6_OUT>/ga/<budget>-s<seed>/
  uv run python -m optimise.variants rescore                     # every front point, full judge
  uv run python -m optimise.variants backtest                    # judge v3 vs v2 (task 1)

Variant surface (A-r6-101/102, `cities/ksa/assumptions/r6v3_variants.yaml`): on every searchable
line corridor, one field at a time: line type (classes that pass A-r6-004), electrified false,
each intermediate station dropped; single track is scored once and pruned (no track term in the
frozen cost or demand model). Stage 2 combines a corridor's best line type with electrified false
where both beat the base (A-r6-103). Station additions have no variants.

Extended fast model (A-r6-006 unchanged in method): an option = (corridor, variant); a layout is at
most one option per corridor at one phase; its score is the sum of the options' single-corridor
judge scores at their phase; accessibility is the union of their reach sets. The MILP and the
NSGA-II are the R6 engines on this model (same budgets, settings and stop rule); every front
point is re-scored by the full judge.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from optimise import judge as jd
from optimise import search as se

CFG = Path("cities/ksa/assumptions/r6v3_variants.yaml")
LINE_TYPES = ("hsr", "mixed", "conventional_passenger", "commuter")
VFIELDS = ("line_type", "track", "electrified", "drop_stations")
P = len(se.PHASES)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R6_V3 variants."""


def cfg(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CFG).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- the surface
def corridor(cid: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    fam = {"S2": "trunk_gap", "S3": "branch_spur", "S4": "commuter_belt"}.get(
        cid[:2], "station_addition"
    )
    return yaml.safe_load(
        (root / "cities/ksa/corridors" / fam / f"{cid}.yaml").read_text(encoding="utf-8")
    )


def feasible_line_types(cid: str, root: Path = REPO_ROOT) -> list[str]:
    """Classes other than the corridor's own that pass the judge's A-r6-004 check. The check is the
    frozen judge's own function, run in a subprocess with only the judge on the path."""
    jr = jd.judge_root(se.JUDGE, root)
    code = (
        "import json,sys;from pathlib import Path;from optimise import layout as L;"
        "cid=sys.argv[1];r=Path('.');"
        "ok=[t for t in L.LINE_TYPES if not L.feasibility({'id':cid,'line_type':t},r)];"
        "print(json.dumps(ok))"
    )
    env = dict(os.environ, R6_JUDGE_ROOT=str(jr))
    env.pop("PYTHONPATH", None)
    out = subprocess.run(
        [str(root / ".venv/bin/python"), "-c", code, cid],
        cwd=jr,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    own = corridor(cid, root)["line_type"]
    return [t for t in json.loads(out) if t != own]


def vid(cid: str, v: dict[str, Any]) -> str:
    """Library name of a variant = the judge's variant id (optimise.layout.variant_id, v3)."""
    import hashlib

    if not v:
        return cid
    key = {k: v[k] for k in VFIELDS if k in v}
    h = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:8]
    return f"{cid}-v{h}"


def enumerate_stage1(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    c = cfg(root)
    demo = c["pruning"]["track_demonstration_corridor"]["value"]
    out = []
    for cid in se.space(root):
        if cid.startswith("S5-"):
            continue
        cor = corridor(cid, root)
        for t in feasible_line_types(cid, root):
            out.append({"id": cid, "variant": {"line_type": t}, "kind": "line_type"})
        for e in c["surface"]["electrified"]["value"]:
            out.append({"id": cid, "variant": {"electrified": bool(e)}, "kind": "electrified"})
        for s in cor["stations"]:
            if s.get("class") != "terminal":
                out.append(
                    {"id": cid, "variant": {"drop_stations": [s["id"]]}, "kind": "drop_station"}
                )
        if cid == demo:
            out.append({"id": cid, "variant": {"track": "single"}, "kind": "track_demo"})
    for o in out:
        o["lib"] = vid(o["id"], o["variant"])
        o["stage"] = 1
    return out


def best_phase_robust(s: dict[str, Any]) -> float:
    sw = s["phase_sweep"]
    return max(min(sw[str(ph)][f"npv_at_p50_cost|{p}"] for p in se.POPS) for ph in se.PHASES)


def enumerate_stage2(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """A-r6-103: best line type x electrified false, where both improve on the base corridor."""
    lib = root / se.LIB
    idx = json.loads((lib / "variants.json").read_text())
    by: dict[str, dict[str, list]] = {}
    for o in idx["variants"]:
        if o["stage"] != 1:
            continue
        p = lib / o["lib"] / "score.json"
        if not p.exists():
            continue
        s = json.loads(p.read_text())
        if not s.get("feasible"):
            continue
        by.setdefault(o["id"], {}).setdefault(o["kind"], []).append((best_phase_robust(s), o))
    out = []
    for cid, k in sorted(by.items()):
        bp = lib / cid / "score.json"
        if not bp.exists() or not {"line_type", "electrified"} <= set(k):
            continue
        base = best_phase_robust(json.loads(bp.read_text()))
        lt = max(k["line_type"], key=lambda x: x[0])
        el = max(k["electrified"], key=lambda x: x[0])
        if lt[0] > base and el[0] > base:
            v = {**lt[1]["variant"], **el[1]["variant"]}
            out.append(
                {"id": cid, "variant": v, "kind": "combined", "stage": 2, "lib": vid(cid, v)}
            )
    return out


@app.command("enumerate")
def enumerate_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Write <R6_OUT>/library/variants.json (stage 1) with the run-count estimate."""
    lib = root / se.LIB
    lib.mkdir(parents=True, exist_ok=True)
    v = enumerate_stage1(root)
    base = se.space(root, include_excluded=True)
    v2 = json.loads((root / "runs/r6/library/library.json").read_text())
    secs = [
        json.loads((root / "runs/r6/library" / i / "score.json").read_text())["seconds"]
        for i in v2["ids"]
    ]
    n_all = len(base) + len(v)
    est = {
        "v2_library_runs": len(secs),
        "v2_seconds_per_run_mean": round(float(np.mean(secs)), 1),
        "v2_seconds_total": round(float(np.sum(secs)), 1),
        "v3_runs_stage1_incl_base": n_all,
        "parallel": cfg(root)["compute"]["library_parallel_runs"]["value"],
    }
    est["v3_wall_hours_estimate"] = round(
        n_all * est["v2_seconds_per_run_mean"] / est["parallel"] / 3600, 2
    )
    pruned_track = [
        c
        for c in se.space(root)
        if not c.startswith("S5-") and c not in {x["id"] for x in v if x["kind"] == "track_demo"}
    ]
    (lib / "variants.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "judge": se.JUDGE,
                "estimate": est,
                "base_ids": base,
                "variants": v,
                "not_scored": {
                    "track_single (A-r6-102)": pruned_track,
                    "station additions (no variant field applies)": [
                        c for c in se.space(root) if c.startswith("S5-")
                    ],
                },
            },
            indent=1,
        )
        + "\n"
    )
    kinds = pd.Series([x["kind"] for x in v]).value_counts().to_dict()
    typer.echo(json.dumps({"variants": len(v), "kinds": kinds, **est}))


# --------------------------------------------------------------------------- library
@app.command("library")
def library_cmd(
    stage: int = typer.Option(1),
    workers: int = typer.Option(0, help="parallel judge runs (0 = the YAML setting)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Single-option judge scores (phase sweep, accessibility) of the variants of one stage."""
    h0 = jd.check_full(se.JUDGE, root)
    lib = root / se.LIB
    idxp = lib / "variants.json"
    idx = json.loads(idxp.read_text())
    if stage == 2:
        new = enumerate_stage2(root)
        known = {o["lib"] for o in idx["variants"]}
        idx["variants"] += [o for o in new if o["lib"] not in known]
        idxp.write_text(json.dumps(idx, indent=1) + "\n")
    todo = [o for o in idx["variants"] if o["stage"] == stage]
    n = workers or int(cfg(root)["compute"]["library_parallel_runs"]["value"])

    def one(o: dict[str, Any]) -> tuple[str, str]:
        out = lib / o["lib"]
        if (out / "score.json").exists():
            return o["lib"], "cached"
        lp = lib / "_layouts" / f"{o['lib']}.yaml"
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_text(
            yaml.safe_dump(
                {"id": f"single-{o['lib']}", "corridors": [{"id": o["id"], **o["variant"]}]}
            )
        )
        t = time.monotonic()
        try:
            s = se.run_judge(lp, out, root, 1, ("--phase-sweep",))
        except Exception as e:  # noqa: BLE001 - reported per variant
            return o["lib"], f"FAILED {e}"[:300]
        best = best_phase_robust(s) if s.get("feasible") else None
        se.append_result(
            {
                "time_utc": se.now(),
                "engine": f"variant-library-s{stage}",
                "commit": se.git_head(root),
                "layout_hash": se.layout_hash({"corridors": [{"id": o["id"], **o["variant"]}]}),
                "hypothesis": f"{o['id']}: {o['kind']} {json.dumps(o['variant'])} beats the base "
                "corridor at its best phase",
                "fidelity": "full (single corridor, phase sweep)",
                "decision": "library",
                "cost_usd": "0 (local)",
                **se.row_from_full(s),
                "notes": f"best-phase robust NPV {best:.1f}"
                if best is not None
                else "; ".join(s.get("errors", []))[:200],
            },
            root,
        )
        return o["lib"], f"ok {time.monotonic() - t:.0f}s"

    with ThreadPoolExecutor(n) as ex:
        for name, st in ex.map(one, todo):
            typer.echo(f"{name}: {st}")
    h1 = jd.check_full(se.JUDGE, root)
    (lib / f"variants-stage{stage}.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "judge": se.JUDGE,
                "sha256_start": h0,
                "sha256_end": h1,
                "n": len(todo),
                "libs": [o["lib"] for o in todo],
            },
            indent=1,
        )
        + "\n"
    )


# --------------------------------------------------------------------------- extended fast model
class FastV:
    """Additive fast model over (corridor, variant) options (A-r6-006 method, A-r6-101..103)."""

    def __init__(self, root: Path = REPO_ROOT, variants: bool = True) -> None:
        lib = root / se.LIB
        scores = {p.parent.name: json.loads(p.read_text()) for p in lib.glob("*/score.json")}
        ids = [i for i in se.space(root) if i in scores and scores[i].get("feasible")]
        vs = json.loads((lib / "variants.json").read_text())["variants"] if variants else []
        opts: list[tuple[str, dict[str, Any], str]] = []
        for cid in ids:
            opts.append((cid, {}, cid))
            for o in vs:
                if o["id"] != cid or o["kind"] == "track_demo":
                    continue
                s = scores.get(o["lib"])
                if s and s.get("feasible"):
                    opts.append((cid, o["variant"], o["lib"]))
        self.ids = ids
        self.opts = opts
        self.index = {c: i for i, c in enumerate(ids)}
        self.opt_corr = np.array([self.index[c] for c, _, _ in opts])
        self.offs = np.array([int(np.flatnonzero(self.opt_corr == i)[0]) for i in range(len(ids))])
        self.nopt = np.bincount(self.opt_corr, minlength=len(ids))
        self.maxval = self.nopt * P
        n = len(opts)
        self.pvb = np.zeros((n, P, 3))
        self.pvc = np.zeros((n, P, 3))
        self.pvc90 = np.zeros((n, P, 3))
        self.capex = np.zeros((n, P))
        for o, (_, _, name) in enumerate(opts):
            sw = scores[name]["phase_sweep"]
            for j, ph in enumerate(se.PHASES):
                s = sw[str(ph)]
                self.capex[o, j] = s["capex_p50"]
                for k, pop in enumerate(se.POPS):
                    self.pvb[o, j, k] = s[f"pvb_p50|{pop}"]
                    self.pvc[o, j, k] = s[f"pvc_p50|{pop}"]
                    self.pvc90[o, j, k] = s[f"pvc_p90|{pop}"]
        zp = pd.read_parquet(lib / "zones_pop.parquet").set_index("zone_id").population
        zids = sorted(zp.index)
        zix = {z: k for k, z in enumerate(zids)}
        self.popv = np.array([float(zp[z]) for z in zids])
        s1 = scores[ids[0]]["accessibility"]["zones_reached"]["S1"]
        self.metros = list(s1)
        self.reach = {}
        for b in ("60", "120"):
            arr = np.zeros((n, len(self.metros), len(zids)), dtype=bool)
            for o, (_, _, name) in enumerate(opts):
                lay = scores[name]["accessibility"]["zones_reached"]["layout"]
                for j, m in enumerate(self.metros):
                    for z in set(lay[m][b]) - set(s1[m][b]):
                        arr[o, j, zix[z]] = True
            self.reach[b] = arr

    # genome[i] = 0 (off) or 1 + option_rank * P + phase_index for corridor i
    def decode(self, g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        on = np.flatnonzero(g)
        k = g[on] - 1
        return self.offs[on] + k // P, k % P

    def score(self, g: np.ndarray, pops: tuple[int, ...] = (0, 1, 2)) -> dict[str, Any]:
        o, ph = self.decode(g)
        npv50 = (self.pvb[o, ph, :] - self.pvc[o, ph, :]).sum(axis=0)
        npv90 = (self.pvb[o, ph, :] - self.pvc90[o, ph, :]).sum(axis=0)
        gain = {
            b: float((self.reach[b][o].any(axis=0) @ self.popv).sum()) if len(o) else 0.0
            for b in ("60", "120")
        }
        return {
            "robust_npv": float(min(npv50[list(pops)])),
            "npv": dict(zip(se.POPS, map(float, npv50), strict=True)),
            "npv_p90cost": dict(zip(se.POPS, map(float, npv90), strict=True)),
            "capex_p50": float(self.capex[o, ph].sum()),
            "access_gain_60": gain["60"],
            "access_gain_120": gain["120"],
            "n": int(len(o)),
            "n_variants": int(sum(1 for x in o if self.opts[x][1])),
        }

    def phase_of(self, g: np.ndarray) -> np.ndarray:
        """Phase index + 1 per corridor (0 = off), the R6 genome the dependency repair uses."""
        return np.where(g > 0, (g - 1) % P + 1, 0)

    def item(self, o: int, ph: int) -> dict[str, Any]:
        cid, v, _ = self.opts[o]
        return {"id": cid, "phase": se.PHASES[ph], **v}

    def layout_of(self, g: np.ndarray, lid: str, ceiling: float | None = None) -> dict[str, Any]:
        o, ph = self.decode(g)
        d: dict[str, Any] = {
            "id": lid,
            "layer": "hypothetical",
            "base": "S1",
            "label": LABEL,
            "corridors": [self.item(int(a), int(b)) for a, b in zip(o, ph, strict=True)],
        }
        if ceiling is not None:
            d["capex_ceiling_sar_m"] = float(ceiling)
        return d

    def genome_of(self, layout: dict[str, Any]) -> np.ndarray:
        g = np.zeros(len(self.ids), dtype=int)
        for c in layout.get("corridors", []):
            if c["id"] not in self.index:
                continue
            i = self.index[c["id"]]
            v = {k: c[k] for k in VFIELDS if k in c}
            ranks = [r for r in range(self.nopt[i]) if self.opts[self.offs[i] + r][1] == v]
            if not ranks:
                continue
            ph = se.PHASES.index(int(c.get("phase", 2030)))
            g[i] = 1 + ranks[0] * P + ph
        return g


def repair(fast: FastV, g: np.ndarray, deps: dict[int, list[int]]) -> np.ndarray:
    """R6 repair on the phase part of the genome (the option is kept)."""
    ph = fast.phase_of(g)
    ph2 = se.repair(ph, deps)
    g = g.copy()
    on = g > 0
    g[on] = g[on] + (ph2[on] - ph[on])
    return g


def milp(fast: FastV, ceiling: float, deps: dict[int, list[int]], pops=(0, 1, 2)) -> np.ndarray:
    """Exact fast-mode optimum of robust NPV under a capex ceiling over options x phases."""
    from scipy.optimize import Bounds, LinearConstraint
    from scipy.optimize import milp as smilp

    n = len(fast.opts)
    nv = n * P + 1
    c = np.zeros(nv)
    c[-1] = -1.0
    A, lo, hi = [], [], []
    for k in pops:
        row = np.zeros(nv)
        row[:-1] = -(fast.pvb[:, :, k] - fast.pvc[:, :, k]).ravel()
        row[-1] = 1.0
        A.append(row)
        lo.append(-np.inf)
        hi.append(0.0)
    row = np.zeros(nv)
    row[:-1] = fast.capex.ravel()
    A.append(row)
    lo.append(-np.inf)
    hi.append(ceiling)

    def cols(i: int, upto: int | None = None) -> list[int]:
        out = []
        for o in np.flatnonzero(fast.opt_corr == i):
            out += [o * P + p for p in range(P if upto is None else upto + 1)]
        return out

    for i in range(len(fast.ids)):  # at most one option and one phase per corridor
        row = np.zeros(nv)
        row[cols(i)] = 1.0
        A.append(row)
        lo.append(-np.inf)
        hi.append(1.0)
    for i, js in deps.items():
        for p in range(P):
            row = np.zeros(nv)
            for o in np.flatnonzero(fast.opt_corr == i):
                row[o * P + p] = 1.0
            for j in js:
                row[cols(j, p)] -= 1.0
            A.append(row)
            lo.append(-np.inf)
            hi.append(0.0)
    r = smilp(
        c,
        constraints=LinearConstraint(np.array(A), lo, hi),
        integrality=np.r_[np.ones(n * P), 0],
        bounds=Bounds(np.r_[np.zeros(n * P), -1e9], np.r_[np.ones(n * P), 1e9]),
    )
    if not r.success:
        raise RuntimeError(r.message)
    x = np.rint(r.x[:-1]).reshape(n, P)
    g = np.zeros(len(fast.ids), dtype=int)
    for o, p in zip(*np.nonzero(x > 0.5), strict=True):
        i = fast.opt_corr[o]
        g[i] = 1 + (o - fast.offs[i]) * P + p
    return g


def objectives(fast: FastV, g: np.ndarray, ceiling: float, pops=(0, 1, 2)) -> tuple:
    s = fast.score(g, pops)
    f = np.array([s["robust_npv"], -s["capex_p50"], s["access_gain_120"]])
    return f, s["capex_p50"] <= ceiling, s


def nsga2(
    fast: FastV,
    ceiling: float,
    deps: dict[int, list[int]],
    seed: int,
    pop_size: int = 80,
    gens: int = 100,
    seeds_in: list[np.ndarray] | None = None,
    pops=(0, 1, 2),
    patience: int = 2,
    max_restarts: int | None = None,
) -> tuple[list[np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    """`optimise.search.nsga2` on the option genome: the same selection, crossover, mutation rate
    (1.5 / n per gene), restart and stop rule (A-r6-013); a mutated gene takes a uniform value in
    0..options x phases (half the draws off, as in R6). `max_restarts` (A-r6-106) stops a run whose
    front is still moving; the info says which rule stopped it."""
    rng = np.random.default_rng(seed)
    n = len(fast.ids)
    tie = np.random.default_rng(12345)

    def better(e1, e2) -> bool:
        if e1[2] != e2[2]:
            return bool(e1[2])
        if not e1[2]:
            return e1[1][1] > e2[1][1]
        if se.dominates(e1[1], e2[1]):
            return True
        if se.dominates(e2[1], e1[1]):
            return False
        return bool(tie.random() < 0.5)

    def uniform() -> np.ndarray:  # one draw per corridor in 1..options x phases
        return np.floor(rng.random(n) * fast.maxval).astype(int) + 1

    def rand() -> np.ndarray:
        g = np.zeros(n, dtype=int)
        k = rng.integers(1, max(2, n // 6))
        on = rng.choice(n, size=k, replace=False)
        g[on] = uniform()[on]
        return repair(fast, g, deps)

    archive: dict[bytes, tuple] = {}
    front: dict[bytes, np.ndarray] = {}

    def note_front(key: bytes, f: np.ndarray, feas: bool) -> None:
        if not feas or any(se.dominates(g, f) or np.array_equal(g, f) for g in front.values()):
            return
        for k in [k for k, g in front.items() if se.dominates(f, g)]:
            del front[k]
        front[key] = f

    def ev(g: np.ndarray):
        key = g.tobytes()
        if key not in archive:
            f, feas, s = objectives(fast, g, ceiling, pops)
            archive[key] = (g, f, feas, s)
            note_front(key, f, feas)
        return archive[key]

    restarts, stalled, gens_run = 0, 0, 0
    popn = [rand() for _ in range(pop_size)]
    popn[0] = np.zeros(n, dtype=int)
    for s in seeds_in or []:
        popn.append(repair(fast, s.copy(), deps))
    last = set()
    while True:
        for _ in range(gens):
            gens_run += 1
            evs = [ev(g) for g in popn]
            kids = []
            while len(kids) < pop_size:
                a, b = rng.choice(len(popn), 2, replace=False)
                c, d = rng.choice(len(popn), 2, replace=False)
                p1 = popn[a] if better(evs[a], evs[b]) else popn[b]
                p2 = popn[c] if better(evs[c], evs[d]) else popn[d]
                child = np.where(rng.random(n) < 0.5, p1, p2)
                mut = rng.random(n) < 1.5 / n
                newv = uniform() * (rng.random(n) < 0.5)
                kids.append(repair(fast, np.where(mut, newv, child), deps))
            union = popn + kids
            ue = [ev(g) for g in union]
            feas_idx = [i for i, e in enumerate(ue) if e[2]]
            inf_idx = sorted((i for i, e in enumerate(ue) if not e[2]), key=lambda i: -ue[i][1][1])
            nxt: list[int] = []
            if feas_idx:
                F = np.array([ue[i][1] for i in feas_idx])
                for fr in se.nondominated_sort(F):
                    ids = [feas_idx[i] for i in fr]
                    if len(nxt) + len(ids) <= pop_size:
                        nxt += ids
                    else:
                        cd = se.crowding(np.array([e[1] for e in ue]), ids)
                        nxt += sorted(ids, key=lambda i: -cd[i])[: pop_size - len(nxt)]
                        break
            nxt += inf_idx[: pop_size - len(nxt)]
            popn = [union[i] for i in nxt]
        fk = set(front)
        stalled = stalled + 1 if fk == last else 0
        last = fk
        typer.echo(
            f"restart {restarts}: front {len(fk)}, evaluations {len(archive)}, stalled {stalled}",
            err=True,
        )
        if stalled >= patience:
            stop = f"front unchanged over {patience} restarts"
            break
        if max_restarts is not None and restarts >= max_restarts:
            stop = f"restart cap {max_restarts} reached (A-r6-106); front still moving"
            break
        restarts += 1
        best = [archive[k][0] for k in fk]
        popn = best[: pop_size // 2] + [
            rand() for _ in range(pop_size - min(len(best), pop_size // 2))
        ]
    out = sorted((archive[k] for k in last), key=lambda v: -v[1][0])
    info = {
        "evaluations": len(archive),
        "generations": gens_run,
        "restarts": restarts,
        "stop": stop,
    }
    return [v[0] for v in out], [v[3] for v in out], info


def row_fast(s: dict[str, Any]) -> dict[str, Any]:
    return se.row_from_fast(s) | {"notes": f"{s['n_variants']} variant option(s)"}


@app.command("milp")
def milp_cmd(
    variants: bool = typer.Option(True),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Exact fast-mode robust-NPV optimum per budget, with and without variants."""
    h0 = jd.check_full(se.JUDGE, root)
    fast = FastV(root, variants)
    deps = se.dependencies(fast, root)
    out = root / se.R6 / ("milp" if variants else "milp-novariants")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, ceil in se.budgets(root).items():
        g = milp(fast, ceil, deps)
        s = fast.score(g)
        lay = fast.layout_of(g, f"milp-v3-{name}", ceil)
        (out / f"{name}.yaml").write_text(yaml.safe_dump(lay, sort_keys=False))
        rows.append({"budget": name, "ceiling": ceil, **row_fast(s)})
        se.append_result(
            {
                "time_utc": se.now(),
                "engine": "milp-v3" if variants else "milp-v3-novariants",
                "commit": se.git_head(root),
                "layout_hash": se.layout_hash(lay),
                "hypothesis": f"exact fast-mode optimum over options x phases, budget {name}",
                "fidelity": "fast",
                "decision": "front",
                "cost_usd": "0 (local)",
                **row_fast(s),
            },
            root,
        )
    pd.DataFrame(rows).to_csv(out / "milp.csv", index=False)
    h1 = jd.check_full(se.JUDGE, root)
    (out / "info.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "options": len(fast.opts),
                "corridors": len(fast.ids),
                "sha256_start": h0,
                "sha256_end": h1,
            },
            indent=1,
        )
        + "\n"
    )
    typer.echo(pd.DataFrame(rows).to_string())


@app.command("ga")
def ga_cmd(
    budget: str = typer.Option(...),
    seed: int = typer.Option(1),
    seed_layouts: str = typer.Option(""),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """NSGA-II on the extended fast model for one budget and seed (A-r6-013 settings)."""
    h0 = jd.check_full(se.JUDGE, root)
    t0 = time.monotonic()
    c = yaml.safe_load((root / se.BUDGETS).read_text(encoding="utf-8"))["ga"]
    fast = FastV(root)
    deps = se.dependencies(fast, root)
    ceil = se.budgets(root)[budget]
    seeds_in = [
        fast.genome_of(yaml.safe_load(Path(p).read_text()))
        for p in filter(None, seed_layouts.split(","))
    ]
    gs, ss, info = nsga2(
        fast,
        ceil,
        deps,
        seed,
        int(c["pop_size"]["value"]),
        int(c["generations_per_restart"]["value"]),
        seeds_in,
        patience=int(c["stop_after_restarts_without_front_change"]["value"]),
        max_restarts=int(cfg(root)["search"]["max_restarts"]["value"]),
    )
    tag = f"{budget}-s{seed}"
    out = root / se.R6 / "ga" / tag
    if out.exists():
        shutil.rmtree(out)
    (out / "layouts").mkdir(parents=True)
    rows = []
    for k, (g, s) in enumerate(zip(gs, ss, strict=True)):
        lay = fast.layout_of(g, f"ga-v3-{tag}-{k:03d}", ceil)
        (out / "layouts" / f"{k:03d}.yaml").write_text(yaml.safe_dump(lay, sort_keys=False))
        rows.append({"k": k, "layout_hash": se.layout_hash(lay), **row_fast(s)})
    pd.DataFrame(rows).to_csv(out / "front.csv", index=False)
    h1 = jd.check_full(se.JUDGE, root)
    info |= {
        "label": LABEL,
        "budget": budget,
        "ceiling_sar_m": ceil,
        "seed": seed,
        "options": len(fast.opts),
        "front_size": len(gs),
        "seconds": round(time.monotonic() - t0, 1),
        "judge": se.JUDGE,
        "judge_sha256_start": h0,
        "judge_sha256_end": h1,
        "seeded_from": seed_layouts,
    }
    (out / "info.json").write_text(json.dumps(info, indent=1) + "\n")
    for r in rows:
        se.append_result(
            {
                "time_utc": se.now(),
                "engine": "ga-v3",
                "commit": se.git_head(root),
                "hypothesis": f"NSGA-II front over options x phases, budget {budget}, seed {seed}",
                "fidelity": "fast",
                "decision": "front",
                "cost_usd": "0 (local)",
                **r,
                "notes": f"{tag}; {r['notes']}",
            },
            root,
        )
    typer.echo(f"{tag}: front {len(gs)}, {info['evaluations']} evals, {info['restarts']} restarts")


def combined_front(root: Path = REPO_ROOT, budget: str | None = None) -> pd.DataFrame:
    rows = []
    for d in sorted((root / se.R6 / "ga").glob("*")):
        if budget and not d.name.startswith(budget + "-"):
            continue
        f = pd.read_csv(d / "front.csv")
        f["layout"] = [str(d / "layouts" / f"{k:03d}.yaml") for k in f.k]
        f["tag"] = d.name
        rows.append(f)
    df = pd.concat(rows, ignore_index=True).drop_duplicates("layout_hash")
    F = np.c_[df.robust_npv, -df.capex_p50, df.access_gain_120]
    return df.iloc[first_front(F)].sort_values("capex_p50").reset_index(drop=True)


def first_front(F: np.ndarray) -> list[int]:
    """Indices of the non-dominated rows (maximisation), vectorised per row: the same set as
    `optimise.search.nondominated_sort(F)[0]` on fronts of thousands of points."""
    keep = []
    for i, f in enumerate(F):
        d = F - f
        if not ((d >= 0).all(axis=1) & (d > 0).any(axis=1)).any():
            keep.append(i)
    return keep


@app.command("rescore")
def rescore_cmd(
    extra: str = typer.Option("", help="comma-separated extra layout YAMLs (MILP, agent kept)"),
    per_budget: int = typer.Option(0, help="capex quantiles per budget (0 = the YAML, A-r6-107)"),
    workers: int = typer.Option(2, help="full-judge runs in parallel (4 workers each)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Full-judge score of a selection of the combined GA front of every budget (A-r6-107: max
    robust NPV, max reach, capex quantiles, best point holding a variant) plus the extras;
    writes <R6_OUT>/rescore/fast_vs_full.csv."""
    h0 = jd.check_full(se.JUDGE, root)
    per_budget = per_budget or int(cfg(root)["search"]["rescore_capex_quantiles"]["value"])
    out = root / se.R6 / "rescore"
    out.mkdir(parents=True, exist_ok=True)
    fast = FastV(root)
    pick: list[tuple[str, str, str]] = []
    for b in se.budgets(root):  # A-r6-107: the R6 spread plus the best point with a variant
        f = combined_front(root, b)
        nv = f.notes.str.extract(r"(\d+) variant")[0].astype(int)
        idx = {int(f.robust_npv.idxmax()), int(f.access_gain_120.idxmax())}
        idx |= {int(round(q * (len(f) - 1))) for q in np.linspace(0, 1, per_budget)}
        if (nv > 0).any():
            idx.add(int(f.robust_npv.where(nv > 0).idxmax()))
        pick += [(b, f.loc[i, "tag"], f.loc[i, "layout"]) for i in sorted(idx)]
    pick += [("extra", "extra", p) for p in filter(None, extra.split(","))]
    todo: dict[str, tuple[str, str, str]] = {}
    for b, tag, p in pick:
        h = se.layout_hash(yaml.safe_load(Path(p).read_text()))
        todo.setdefault(h, (b, tag, p))

    def one(item: tuple[str, tuple[str, str, str]]) -> dict[str, Any]:
        h, (b, tag, p) = item
        lp = out / f"{h}.yaml"
        if not lp.exists():
            shutil.copy(p, lp)
        sp = out / h / "score.json"
        s = json.loads(sp.read_text()) if sp.exists() else se.run_judge(lp, out / h, root, 4)
        lay = yaml.safe_load(lp.read_text())
        fs = fast.score(fast.genome_of(lay))
        if not (out / h / ".logged").exists():
            se.append_result(
                {
                    "time_utc": se.now(),
                    "engine": "ga-v3-rescore" if b != "extra" else "rescore-v3",
                    "commit": se.git_head(root),
                    "layout_hash": h,
                    "hypothesis": f"full re-score of a front point ({tag}, {Path(p).name})",
                    "fidelity": "full",
                    "decision": "front",
                    "cost_usd": "0 (local)",
                    **se.row_from_full(s),
                },
                root,
            )
            (out / h / ".logged").write_text("")
        return {
            "budget": b,
            "layout_hash": h,
            "source": p,
            "fast_robust_npv": fs["robust_npv"],
            "full_robust_npv": s.get("robust_npv"),
            "full_feasible": s.get("feasible"),
            "fast_capex": fs["capex_p50"],
            "full_capex": (s.get("capex_sar_m") or {}).get("capex_p50"),
            "fast_access_120": fs["access_gain_120"],
            "full_access_120": s.get("access_gain_120"),
            "n": fs["n"],
            "n_variants": fs["n_variants"],
        }

    rows = []
    with ThreadPoolExecutor(workers) as ex:
        for r in ex.map(one, sorted(todo.items())):
            rows.append(r)
            pd.DataFrame(rows).to_csv(out / "fast_vs_full.csv", index=False)
    h1 = jd.check_full(se.JUDGE, root)
    df = pd.DataFrame(rows)
    from scipy.stats import spearmanr

    ok = df[df.full_feasible.astype(bool)]
    rho = (
        float(spearmanr(ok.fast_robust_npv, ok.full_robust_npv).statistic) if len(ok) > 2 else None
    )
    (out / "rescore.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "n": len(df),
                "spearman_robust_npv": rho,
                "sha256_start": h0,
                "sha256_end": h1,
            },
            indent=1,
        )
        + "\n"
    )
    typer.echo(f"{len(df)} layouts re-scored; Spearman fast vs full {rho}")


# --------------------------------------------------------------------------- back-test
def leaves(d: Any, pre: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out |= leaves(v, f"{pre}/{k}")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out |= leaves(v, f"{pre}[{i}]")
    else:
        out[pre] = d
    return out


SKIP = ("/seconds", "/layout")


def same(a: Any, b: Any) -> bool:
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return True
    return a == b


@app.command("backtest")
def backtest_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Diff every figure of the v3 back-test runs against the v2 copies (no tolerance)."""
    bt = root / se.R6 / "backtest"
    rows = []

    def cmp(test: str, a: dict, b: dict, fa: str, fb: str) -> None:
        la, lb = leaves(a), leaves(b)
        for k in sorted(set(la) | set(lb)):
            if k in SKIP:
                continue
            rows.append(
                {
                    "test": test,
                    "item": k,
                    "v3": la.get(k, "<missing>"),
                    "v2": lb.get(k, "<missing>"),
                    "identical": k in la and k in lb and same(la[k], lb[k]),
                    "v3_file": fa,
                    "v2_file": fb,
                }
            )

    fa, fb = bt / "S0-2025-v3-variants.json", root / "runs/r6/p5b/S0-2025-v2-p5b.json"
    cmp(
        "S0 2025 (mode and line totals)",
        json.loads(fa.read_text()),
        json.loads(fb.read_text()),
        str(fa.relative_to(root)),
        str(fb.relative_to(root)),
    )
    a3 = pd.read_csv(bt / "A-v3-variants/rows-A.csv")
    a2 = pd.read_csv(bt / "A-v2-p5b/rows-A.csv")
    for (_, r3), (_, r2) in zip(a3.iterrows(), a2.iterrows(), strict=True):
        assert r3["item"] == r2["item"] and r3["test"] == r2["test"]
        rows.append(
            {
                "test": r3["test"]
                .replace("A1 S0", "S0")
                .replace("A2 S1", "S1")
                .replace("A3 S1", "S1"),
                "item": r3["item"],
                "v3": r3["judge"],
                "v2": r2["judge"],
                "identical": same(float(r3["judge"]), float(r2["judge"])),
                "v3_file": "runs/r6/v3/backtest/A-v3-variants/rows-A.csv",
                "v2_file": "runs/r6/v3/backtest/A-v2-p5b/rows-A.csv",
            }
        )
    for k in ("L1", "L2", "L3", "L4", "L5"):
        fa, fb = bt / k / "score.json", root / "runs/r6/top5" / k / "score.json"
        cmp(
            f"S6-{k} score.json (all cases)",
            json.loads(fa.read_text()),
            json.loads(fb.read_text()),
            str(fa.relative_to(root)),
            str(fb.relative_to(root)),
        )
    df = pd.DataFrame(rows)
    df.to_csv(bt / "backtest-v3-vs-v2.csv", index=False)
    num = df[[isinstance(x, (int, float)) and not isinstance(x, bool) for x in df.v3]]
    s = df.groupby("test").agg(n=("identical", "size"), identical=("identical", "sum"))
    s["numeric"] = num.groupby("test").size().reindex(s.index).fillna(0).astype(int)
    s.to_csv(bt / "backtest-summary.csv")
    typer.echo(s.to_string())
    typer.echo("IDENTICAL" if df.identical.all() else "DIFFERENT")


if __name__ == "__main__":
    app()
