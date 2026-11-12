"""R6 search: the fast-mode library, the classical engines (MILP + NSGA-II), the autoresearch
loop tooling and full-fidelity re-scoring through the locked judge (R6 design C).

  uv run python -m optimise.search library --workers 4       # <R6_OUT>/library/<id>/score.json
  uv run python -m optimise.search milp                       # <R6_OUT>/milp/
  uv run python -m optimise.search ga --budget B2 --seed 1    # <R6_OUT>/ga/<budget>-s<seed>/
  uv run python -m optimise.search try --hypothesis "..."          # one agent edit of
                                                                   # scenarios/candidate.yaml
  uv run python -m optimise.search full --layout <yaml> --out <dir>  # full-fidelity judge score

The judge is never imported here: every score comes from a subprocess running
`judge/<R6_JUDGE>/optimise/layout.py` (default `v3-variants`, R6_V3; R6 used `v2-p5b`) with only
the frozen files on its path; the judge fingerprint is checked before every evaluation and the
full SHA-256 at the start and end of every engine run.

Fast mode (A-r6-006): a layout's score is the sum of its corridors' single-corridor scores at
their phase (library, judge at full fidelity per corridor), i.e. corridor interactions (competing
or feeding lines) are ignored; accessibility is the union of the single-corridor reach sets.
Every kept or front layout is re-scored by the full judge before it counts.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import csv
import hashlib
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

# R6_V3 (CP7-3): judge v3 and outputs under runs/r6/v3 by default; the R6 (v2) runs are
# reproduced with R6_JUDGE=v2-p5b R6_OUT=runs/r6
JUDGE = os.environ.get("R6_JUDGE", "v3-variants")
R6 = Path(os.environ.get("R6_OUT", "runs/r6/v3"))
LIB = R6 / "library"
CANDIDATE = Path("scenarios/candidate.yaml")
BUDGETS = Path("cities/ksa/assumptions/r6_search.yaml")
POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
PHASES = (2030, 2035, 2040, 2050)
# CP6 P6a: one shared Jubail station (Al Jubayl); the second site and the two-station variant
# are appraised for the record (P5b re-run) but are not in the search space
EXCLUDED = (
    "S5-station_addition-al-jubayl-royal-commission",
    "S5-station_addition-jubail-two-stations",
)
RESULTS_COLS = (
    "time_utc",
    "engine",
    "commit",
    "layout_hash",
    "hypothesis",
    "fidelity",
    "feasible",
    "robust_npv",
    "npv_low",
    "npv_medium",
    "npv_high",
    "capex_p50",
    "access_gain_60",
    "access_gain_120",
    "n_corridors",
    "decision",
    "eval_seconds",
    "cost_usd",
    "notes",
)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R6 search."""


# --------------------------------------------------------------------------- judge calls
def judge_cmd(root: Path = REPO_ROOT) -> list[str]:
    jr = jd.judge_root(JUDGE, root)
    return [str(root / ".venv/bin/python"), str(jr / "optimise/layout.py")]


def run_judge(
    layout: Path,
    out: Path,
    root: Path = REPO_ROOT,
    workers: int = 4,
    extra: tuple[str, ...] = (),
    check: bool = True,
) -> dict[str, Any]:
    if check:
        jd.check_fingerprint(JUDGE, root)
    env = dict(os.environ, R6_JUDGE_ROOT=str(jd.judge_root(JUDGE, root)))
    env.pop("PYTHONPATH", None)
    out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            *judge_cmd(root),
            "evaluate",
            "--layout",
            str(layout.resolve()),
            "--out",
            str(out.resolve()),
            "--workers",
            str(workers),
            *extra,
        ],
        cwd=jd.judge_root(JUDGE, root),
        env=env,
        capture_output=True,
        text=True,
    )
    (out / "judge.log").write_text(r.stdout + "\n" + r.stderr[-20000:])
    if r.returncode:
        raise RuntimeError(f"judge failed on {layout}: {r.stderr[-1500:]}")
    from common.runmeta import write_meta

    rec = jd.load_record(JUDGE, root)
    write_meta(
        out,
        1,
        {"layout": yaml.safe_load(layout.read_text()), "judge_args": list(extra)},
        extra={
            "label": LABEL,
            "judge": JUDGE,
            "judge_sha256": rec["sha256"],
            "judge_commit": rec["commit"],
            "judge_fingerprint_checked": check,
        },
    )
    judge_meta_version(out, rec)
    return json.loads((out / "score.json").read_text())


def judge_meta_version(out: Path, rec: dict[str, Any]) -> None:
    """The code that scored the layout is the frozen judge: record its commit as code_version and
    keep this checkout's describe as harness_code_version."""
    mp = out / "meta.json"
    m = json.loads(mp.read_text())
    if not str(m.get("code_version", "")).startswith("judge "):
        m["harness_code_version"] = m.get("code_version")
    m["code_version"] = f"judge {rec['name']} @ {rec['commit'][:10]} sha256 {rec['sha256'][:16]}"
    mp.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- space + library
def space(root: Path = REPO_ROOT, include_excluded: bool = False) -> list[str]:
    ids = []
    for s in ("S2", "S3", "S4", "S5"):
        sc = yaml.safe_load((root / "scenarios" / f"{s}.yaml").read_text(encoding="utf-8"))
        for c in sc.get("candidates", []):
            cid = Path(c).stem
            if (root / "runs/costs" / cid / "SKIPPED.json").exists():
                continue
            if cid in EXCLUDED and not include_excluded:
                continue
            ids.append(cid)
    if include_excluded:
        ids.append("S5-station_addition-jubail-two-stations")
    return ids


@app.command("library")
def library_cmd(
    workers: int = typer.Option(4, help="corridors in parallel (1 judge process each)"),
    only: str = typer.Option(""),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Single-corridor judge scores (phase sweep, accessibility) for the fast mode."""
    h0 = jd.check_full(JUDGE, root)
    ids = space(root, include_excluded=True)
    if only:
        ids = [i for i in ids if i in set(only.split(","))]
    lib = root / LIB
    lib.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, R6_JUDGE_ROOT=str(jd.judge_root(JUDGE, root)))
    subprocess.run(
        [*judge_cmd(root), "zonepop", "--layout", "-", "--out", str(lib.resolve())],
        cwd=jd.judge_root(JUDGE, root),
        env=env,
        check=True,
    )

    def one(cid: str) -> tuple[str, str]:
        out = lib / cid
        if (out / "score.json").exists():
            return cid, "cached"
        lp = lib / "_layouts" / f"{cid}.yaml"
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_text(yaml.safe_dump({"id": f"single-{cid}", "corridors": [{"id": cid}]}))
        t = time.monotonic()
        try:
            run_judge(lp, out, root, 1, ("--phase-sweep",))
        except Exception as e:  # noqa: BLE001 - reported per corridor
            return cid, f"FAILED {e}"[:300]
        return cid, f"ok {time.monotonic() - t:.0f}s"

    with ThreadPoolExecutor(workers) as ex:
        for cid, st in ex.map(one, ids):
            typer.echo(f"{cid}: {st}", err=False)
    h1 = jd.check_full(JUDGE, root)
    (lib / "library.json").write_text(
        json.dumps(
            {"label": LABEL, "judge": JUDGE, "sha256_start": h0, "sha256_end": h1, "ids": ids},
            indent=1,
        )
        + "\n"
    )


def load_library(root: Path = REPO_ROOT) -> dict[str, dict[str, Any]]:
    out = {}
    for p in sorted((root / LIB).glob("*/score.json")):
        out[p.parent.name] = json.loads(p.read_text())
    return out


class Fast:
    """Additive fast model over the library (A-r6-006)."""

    def __init__(self, root: Path = REPO_ROOT, ids: list[str] | None = None) -> None:
        lib = load_library(root)
        self.ids = [i for i in (ids or space(root)) if i in lib and lib[i].get("feasible")]
        n, P = len(self.ids), len(PHASES)
        self.pvb = np.zeros((n, P, 3))
        self.pvc = np.zeros((n, P, 3))
        self.pvc90 = np.zeros((n, P, 3))
        self.capex = np.zeros((n, P))
        for i, cid in enumerate(self.ids):
            sw = lib[cid]["phase_sweep"]
            for j, ph in enumerate(PHASES):
                s = sw[str(ph)]
                self.capex[i, j] = s["capex_p50"]
                for k, pop in enumerate(POPS):
                    self.pvb[i, j, k] = s[f"pvb_p50|{pop}"]
                    self.pvc[i, j, k] = s[f"pvc_p50|{pop}"]
                    self.pvc90[i, j, k] = s[f"pvc_p90|{pop}"]
        zp = pd.read_parquet(root / LIB / "zones_pop.parquet").set_index("zone_id").population
        self.zpop = zp.to_dict()
        any_lib = lib[self.ids[0]]["accessibility"]["zones_reached"]
        self.metros = list(any_lib["S1"])
        self.s1 = {(m, b): set(any_lib["S1"][m][b]) for m in self.metros for b in ("60", "120")}
        zids = sorted(self.zpop)
        zix = {z: k for k, z in enumerate(zids)}
        self.popv = np.array([float(self.zpop[z]) for z in zids])
        # reach[b][c, m, z]: zone z newly reached (vs S1) from metro m by corridor c alone
        self.reach = {}
        for b in ("60", "120"):
            arr = np.zeros((len(self.ids), len(self.metros), len(zids)), dtype=bool)
            for i, c in enumerate(self.ids):
                lay = lib[c]["accessibility"]["zones_reached"]["layout"]
                for j, m in enumerate(self.metros):
                    for z in set(lay[m][b]) - self.s1[(m, b)]:
                        arr[i, j, zix[z]] = True
            self.reach[b] = arr
        self.index = {c: i for i, c in enumerate(self.ids)}

    def _pop(self, z: str) -> float:
        return float(self.zpop.get(z, 0.0))

    def score(self, genome: np.ndarray, pops: tuple[int, ...] = (0, 1, 2)) -> dict[str, Any]:
        """genome[i] = 0 (off) or 1..4 (phase index + 1)."""
        on = np.flatnonzero(genome)
        ph = genome[on] - 1
        npv50 = (self.pvb[on, ph, :] - self.pvc[on, ph, :]).sum(axis=0)
        npv90 = (self.pvb[on, ph, :] - self.pvc90[on, ph, :]).sum(axis=0)
        cap = float(self.capex[on, ph].sum())
        gain = {
            b: float((self.reach[b][on].any(axis=0) @ self.popv).sum()) if len(on) else 0.0
            for b in ("60", "120")
        }
        return {
            "robust_npv": float(min(npv50[list(pops)])),
            "npv": dict(zip(POPS, map(float, npv50), strict=True)),
            "npv_p90cost": dict(zip(POPS, map(float, npv90), strict=True)),
            "capex_p50": cap,
            "access_gain_60": gain["60"],
            "access_gain_120": gain["120"],
            "n": int(len(on)),
        }

    def genome_of(self, layout: dict[str, Any]) -> np.ndarray:
        g = np.zeros(len(self.ids), dtype=int)
        for c in layout.get("corridors", []):
            if c["id"] in self.index and not set(c) - {"id", "phase"}:
                g[self.index[c["id"]]] = PHASES.index(int(c.get("phase", 2030))) + 1
        return g

    def layout_of(self, g: np.ndarray, lid: str, ceiling: float | None = None) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": lid,
            "layer": "hypothetical",
            "base": "S1",
            "label": LABEL,
            "corridors": [
                {"id": self.ids[i], "phase": PHASES[int(g[i]) - 1]} for i in np.flatnonzero(g)
            ],
        }
        if ceiling is not None:
            d["capex_ceiling_sar_m"] = float(ceiling)
        return d


# --------------------------------------------------------------------------- dependencies
def dependencies(fast: Fast, root: Path = REPO_ROOT) -> dict[int, list[int]]:
    """i -> corridors one of which must be built no later than i (i touches no S1 station)."""
    from access import railgraph

    cfg = railgraph.load_cfg(root)
    net = []
    for ld in railgraph.scenario_lines("S1", cfg, root, None):
        net += [(float(s["lat"]), float(s["lon"])) for s in ld["stations"]]
    net_a = np.array(net)
    pts = {}
    for i, cid in enumerate(fast.ids):
        fam = {"S2": "trunk_gap", "S3": "branch_spur", "S4": "commuter_belt"}.get(cid[:2])
        if fam is None:
            continue
        c = yaml.safe_load(
            (root / "cities/ksa/corridors" / fam / f"{cid}.yaml").read_text(encoding="utf-8")
        )
        pts[i] = np.array([(float(s["lat"]), float(s["lon"])) for s in c["stations"]])

    def near(a: np.ndarray, b: np.ndarray) -> bool:
        g = np.broadcast_arrays(a[:, None, 1], a[:, None, 0], b[None, :, 1], b[None, :, 0])
        d = railgraph.km_between(*(x.ravel() for x in g))
        return bool((d <= 1.0).any())

    deps = {}
    for i, p in pts.items():
        ends = p[[0, -1]]
        if near(ends, net_a):
            continue
        others = [j for j in pts if j != i and near(ends, pts[j])]
        if others:
            deps[i] = others
    return deps


def repair(g: np.ndarray, deps: dict[int, list[int]]) -> np.ndarray:
    """A corridor whose only connections are later-phase corridors moves to their phase."""
    g = g.copy()
    for _ in range(3):
        for i, js in deps.items():
            if g[i] == 0:
                continue
            on = [g[j] for j in js if g[j] > 0]
            if on and min(on) > g[i]:
                g[i] = min(on)
    return g


# --------------------------------------------------------------------------- budgets
def budgets(root: Path = REPO_ROOT) -> dict[str, float]:
    d = yaml.safe_load((root / BUDGETS).read_text(encoding="utf-8"))
    return {k: float(v["value"]) for k, v in d["capex_ceilings_sar_m"].items()}


# --------------------------------------------------------------------------- MILP
def milp(fast: Fast, ceiling: float, deps: dict[int, list[int]], pops=(0, 1, 2)) -> np.ndarray:
    """Exact fast-mode optimum of robust NPV under a capex ceiling (scipy HiGHS).
    Variables x[i, p] (build corridor i in phase p) and t (the robust NPV)."""
    from scipy.optimize import Bounds, LinearConstraint
    from scipy.optimize import milp as smilp

    n, P = len(fast.ids), len(PHASES)
    nv = n * P + 1
    c = np.zeros(nv)
    c[-1] = -1.0
    A, lo, hi = [], [], []
    for k in pops:  # t <= sum v x
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
    for i in range(n):  # at most one phase
        row = np.zeros(nv)
        row[i * P : (i + 1) * P] = 1.0
        A.append(row)
        lo.append(-np.inf)
        hi.append(1.0)
    for i, js in deps.items():  # built by phase p => some dependency built by phase <= p
        for p in range(P):
            row = np.zeros(nv)
            row[i * P + p] = 1.0
            for j in js:
                row[j * P : j * P + p + 1] -= 1.0
            A.append(row)
            lo.append(-np.inf)
            hi.append(0.0)
    integrality = np.r_[np.ones(n * P), 0]
    bounds = Bounds(np.r_[np.zeros(n * P), -1e9], np.r_[np.ones(n * P), 1e9])
    r = smilp(
        c,
        constraints=LinearConstraint(np.array(A), lo, hi),
        integrality=integrality,
        bounds=bounds,
    )
    if not r.success:
        raise RuntimeError(r.message)
    x = np.rint(r.x[:-1]).reshape(n, P)
    g = np.zeros(n, dtype=int)
    for i in range(n):
        if x[i].max() > 0.5:
            g[i] = int(np.argmax(x[i])) + 1
    return g


# --------------------------------------------------------------------------- NSGA-II
def dominates(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.all(a >= b) and np.any(a > b))


def nondominated_sort(F: np.ndarray) -> list[list[int]]:
    n = len(F)
    S = [[] for _ in range(n)]
    cnt = np.zeros(n, dtype=int)
    fronts: list[list[int]] = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if dominates(F[p], F[q]):
                S[p].append(q)
            elif dominates(F[q], F[p]):
                cnt[p] += 1
        if cnt[p] == 0:
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in S[p]:
                cnt[q] -= 1
                if cnt[q] == 0:
                    nxt.append(q)
        i += 1
        fronts.append(nxt)
    return fronts[:-1]


def crowding(F: np.ndarray, idx: list[int]) -> dict[int, float]:
    d = dict.fromkeys(idx, 0.0)
    if len(idx) <= 2:
        return dict.fromkeys(idx, np.inf)
    for m in range(F.shape[1]):
        s = sorted(idx, key=lambda i: F[i, m])
        d[s[0]] = d[s[-1]] = np.inf
        span = F[s[-1], m] - F[s[0], m] or 1.0
        for k in range(1, len(s) - 1):
            d[s[k]] += (F[s[k + 1], m] - F[s[k - 1], m]) / span
    return d


def objectives(fast: Fast, g: np.ndarray, ceiling: float, pops=(0, 1, 2)) -> tuple:
    s = fast.score(g, pops)
    feas = s["capex_p50"] <= ceiling
    # maximise robust NPV, minimise capex, maximise accessibility; the 120-min band (A-r6-007):
    # no corridor adds any 60-min door-to-door reach (library), so the 60-min band is reported only
    f = np.array([s["robust_npv"], -s["capex_p50"], s["access_gain_120"]])
    return f, feas, s


def nsga2(
    fast: Fast,
    ceiling: float,
    deps: dict[int, list[int]],
    seed: int,
    pop_size: int = 80,
    gens: int = 120,
    seeds_in: list[np.ndarray] | None = None,
    pops=(0, 1, 2),
    patience: int = 2,
) -> tuple[list[np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    """NSGA-II with constraint domination (infeasible = capex over the ceiling, ranked by excess);
    restarts when the front stalls for `gens` generations; stops after `patience` restarts without
    a front change (R6 guardrail D). Returns the final non-dominated feasible set."""
    rng = np.random.default_rng(seed)
    n = len(fast.ids)
    P = len(PHASES)

    def rand() -> np.ndarray:
        g = np.zeros(n, dtype=int)
        k = rng.integers(1, max(2, n // 6))
        on = rng.choice(n, size=k, replace=False)
        g[on] = rng.integers(1, P + 1, size=k)
        return repair(g, deps)

    archive: dict[bytes, tuple[np.ndarray, np.ndarray, bool, dict]] = {}

    def ev(g: np.ndarray):
        key = g.tobytes()
        if key not in archive:
            f, feas, s = objectives(fast, g, ceiling, pops)
            archive[key] = (g, f, feas, s)
            note_front(key, f, feas)
        return archive[key]

    front: dict[bytes, np.ndarray] = {}  # running non-dominated feasible archive

    def note_front(key: bytes, f: np.ndarray, feas: bool) -> None:
        if not feas or any(dominates(g, f) or np.array_equal(g, f) for g in front.values()):
            return
        for k in [k for k, g in front.items() if dominates(f, g)]:
            del front[k]
        front[key] = f

    def front_keys() -> set[bytes]:
        return set(front)

    restarts, stalled, gens_run = 0, 0, 0
    popn = [rand() for _ in range(pop_size)]
    popn[0] = np.zeros(n, dtype=int)
    for s in seeds_in or []:
        popn.append(repair(s.copy(), deps))
    last_front = set()
    while True:
        for _gen in range(gens):
            gens_run += 1
            evs = [ev(g) for g in popn]
            # tournament + uniform crossover + mutation
            kids = []
            while len(kids) < pop_size:
                a, b = rng.choice(len(popn), 2, replace=False)
                c, d = rng.choice(len(popn), 2, replace=False)
                p1 = popn[a] if better(evs[a], evs[b]) else popn[b]
                p2 = popn[c] if better(evs[c], evs[d]) else popn[d]
                mask = rng.random(n) < 0.5
                child = np.where(mask, p1, p2)
                mut = rng.random(n) < 1.5 / n
                child = np.where(mut, rng.integers(0, P + 1, size=n) * (rng.random(n) < 0.5), child)
                kids.append(repair(child, deps))
            union = popn + kids
            ue = [ev(g) for g in union]
            # constraint domination: feasible first, then by capex excess
            feas_idx = [i for i, e in enumerate(ue) if e[2]]
            inf_idx = sorted((i for i, e in enumerate(ue) if not e[2]), key=lambda i: -ue[i][1][1])
            F = np.array([ue[i][1] for i in feas_idx]) if feas_idx else np.zeros((0, 3))
            nxt: list[int] = []
            if feas_idx:
                for fr in nondominated_sort(F):
                    ids = [feas_idx[i] for i in fr]
                    if len(nxt) + len(ids) <= pop_size:
                        nxt += ids
                    else:
                        cd = crowding(np.array([ue[i][1] for i in range(len(ue))]), ids)
                        nxt += sorted(ids, key=lambda i: -cd[i])[: pop_size - len(nxt)]
                        break
            nxt += inf_idx[: pop_size - len(nxt)]
            popn = [union[i] for i in nxt]
        fk = front_keys()
        if fk == last_front:
            stalled += 1
        else:
            stalled = 0
        last_front = fk
        if stalled >= patience:
            break
        restarts += 1
        best = [archive[k][0] for k in fk]
        popn = best[: pop_size // 2] + [
            rand() for _ in range(pop_size - min(len(best), pop_size // 2))
        ]
    front = [archive[k] for k in last_front]
    front.sort(key=lambda v: -v[1][0])
    info = {
        "evaluations": len(archive),
        "generations": gens_run,
        "restarts": restarts,
        "stop": f"front unchanged over {patience} restarts",
    }
    return [v[0] for v in front], [v[3] for v in front], info


_TIE = np.random.default_rng(12345)  # tie-break stream of the binary tournament


def better(e1, e2) -> bool:
    if e1[2] and not e2[2]:
        return True
    if e2[2] and not e1[2]:
        return False
    if not e1[2]:
        return e1[1][1] > e2[1][1]
    if dominates(e1[1], e2[1]):
        return True
    if dominates(e2[1], e1[1]):
        return False
    return bool(_TIE.random() < 0.5)


# --------------------------------------------------------------------------- results.tsv
def layout_hash(layout: dict[str, Any]) -> str:
    core = {
        "corridors": sorted(json.dumps(c, sort_keys=True) for c in layout.get("corridors", [])),
        "proposed_links": layout.get("proposed_links", []),
    }
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:12]


def append_result(row: dict[str, Any], root: Path = REPO_ROOT) -> None:
    p = root / R6 / "results.tsv"
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.exists()
    with p.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RESULTS_COLS, delimiter="\t", extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in RESULTS_COLS})


def git_head(root: Path = REPO_ROOT) -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True
    ).stdout.strip()


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def row_from_full(s: dict[str, Any]) -> dict[str, Any]:
    n = s.get("npv_at_p50_cost") or {}
    return {
        "feasible": s.get("feasible"),
        "robust_npv": round(float(s.get("robust_npv", float("nan"))), 1)
        if s.get("feasible")
        else "",
        "npv_low": round(n.get("un_wpp_low", float("nan")), 1) if n else "",
        "npv_medium": round(n.get("un_wpp_medium", float("nan")), 1) if n else "",
        "npv_high": round(n.get("un_wpp_high", float("nan")), 1) if n else "",
        "capex_p50": round((s.get("capex_sar_m") or {}).get("capex_p50", float("nan")), 1),
        "access_gain_60": s.get("access_gain_60"),
        "access_gain_120": s.get("access_gain_120"),
        "n_corridors": s.get("n_corridors"),
        "eval_seconds": s.get("seconds"),
    }


def row_from_fast(s: dict[str, Any]) -> dict[str, Any]:
    return {
        "feasible": True,
        "robust_npv": round(s["robust_npv"], 1),
        "npv_low": round(s["npv"]["un_wpp_low"], 1),
        "npv_medium": round(s["npv"]["un_wpp_medium"], 1),
        "npv_high": round(s["npv"]["un_wpp_high"], 1),
        "capex_p50": round(s["capex_p50"], 1),
        "access_gain_60": round(s["access_gain_60"]),
        "access_gain_120": round(s["access_gain_120"]),
        "n_corridors": s["n"],
    }


# --------------------------------------------------------------------------- commands
@app.command("full")
def full_cmd(
    layout: Path = typer.Option(...),
    out: Path = typer.Option(...),
    all_cases: bool = typer.Option(False),
    engine: str = typer.Option("rescore"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Full-fidelity judge score of one layout; one results.tsv row."""
    extra = ("--all-cases",) if all_cases else ()
    s = run_judge(layout, out, root, 4, extra)
    d = yaml.safe_load(layout.read_text())
    append_result(
        {
            "time_utc": now(),
            "engine": engine,
            "commit": git_head(root),
            "layout_hash": layout_hash(d),
            "hypothesis": f"full re-score of {layout.name}",
            "fidelity": "full",
            "decision": "scored",
            "cost_usd": "0 (local)",
            **row_from_full(s),
        },
        root,
    )
    typer.echo(json.dumps(row_from_full(s)))


@app.command("milp")
def milp_cmd(
    holdout: bool = typer.Option(False, help="score on low+medium only (overfitting check)"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Exact fast-mode robust-NPV optimum per budget level (runs/r6/milp/)."""
    fast = Fast(root)
    deps = dependencies(fast, root)
    pops = (0, 1) if holdout else (0, 1, 2)
    out = root / R6 / ("milp-holdout" if holdout else "milp")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, ceil in budgets(root).items():
        g = milp(fast, ceil, deps, pops)
        s = fast.score(g, pops)
        lay = fast.layout_of(g, f"milp-{name}", ceil)
        (out / f"{name}.yaml").write_text(yaml.safe_dump(lay, sort_keys=False))
        rows.append({"budget": name, "ceiling": ceil, **row_from_fast(s)})
        append_result(
            {
                "time_utc": now(),
                "engine": "milp" + ("-holdout" if holdout else ""),
                "commit": git_head(root),
                "layout_hash": layout_hash(lay),
                "hypothesis": f"exact fast-mode optimum, budget {name}",
                "fidelity": "fast",
                "decision": "front",
                "cost_usd": "0 (local)",
                **row_from_fast(s),
            },
            root,
        )
    pd.DataFrame(rows).to_csv(out / "milp.csv", index=False)
    (out / "deps.json").write_text(
        json.dumps({fast.ids[i]: [fast.ids[j] for j in js] for i, js in deps.items()}, indent=1)
    )
    typer.echo(pd.DataFrame(rows).to_string())


@app.command("ga")
def ga_cmd(
    budget: str = typer.Option(...),
    seed: int = typer.Option(1),
    pop_size: int = typer.Option(80),
    gens: int = typer.Option(100),
    holdout: bool = typer.Option(False),
    seed_layouts: str = typer.Option("", help="comma-separated layout YAMLs to seed the GA"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """NSGA-II on the fast model for one budget level and seed (runs/r6/ga/)."""
    h0 = jd.check_full(JUDGE, root)
    t0 = time.monotonic()
    fast = Fast(root)
    deps = dependencies(fast, root)
    ceil = budgets(root)[budget]
    pops = (0, 1) if holdout else (0, 1, 2)
    seeds_in = []
    for p in filter(None, seed_layouts.split(",")):
        seeds_in.append(fast.genome_of(yaml.safe_load(Path(p).read_text())))
    gs, ss, info = nsga2(fast, ceil, deps, seed, pop_size, gens, seeds_in, pops)
    tag = f"{budget}-s{seed}" + ("-holdout" if holdout else "")
    out = root / R6 / "ga" / tag
    if out.exists():
        shutil.rmtree(out)
    (out / "layouts").mkdir(parents=True)
    rows = []
    for k, (g, s) in enumerate(zip(gs, ss, strict=True)):
        lay = fast.layout_of(g, f"ga-{tag}-{k:03d}", ceil)
        (out / "layouts" / f"{k:03d}.yaml").write_text(yaml.safe_dump(lay, sort_keys=False))
        rows.append({"k": k, "layout_hash": layout_hash(lay), **row_from_fast(s)})
    df = pd.DataFrame(rows)
    df.to_csv(out / "front.csv", index=False)
    h1 = jd.check_full(JUDGE, root)
    info |= {
        "label": LABEL,
        "budget": budget,
        "ceiling_sar_m": ceil,
        "seed": seed,
        "pop_size": pop_size,
        "gens_per_restart": gens,
        "holdout": holdout,
        "score_populations": [POPS[i] for i in pops],
        "front_size": len(gs),
        "seconds": round(time.monotonic() - t0, 1),
        "judge_sha256_start": h0,
        "judge_sha256_end": h1,
        "seeded_from": seed_layouts,
    }
    (out / "info.json").write_text(json.dumps(info, indent=1) + "\n")
    for r in rows:
        append_result(
            {
                "time_utc": now(),
                "engine": "ga" + ("-holdout" if holdout else ""),
                "commit": git_head(root),
                "hypothesis": f"NSGA-II front, budget {budget}, seed {seed}",
                "fidelity": "fast",
                "decision": "front",
                "cost_usd": "0 (local)",
                "notes": tag,
                **r,
            },
            root,
        )
    typer.echo(
        f"{tag}: front {len(gs)}, {info['evaluations']} evaluations, {info['restarts']} restarts"
    )
    typer.echo(df.head(15).to_string())


@app.command("try")
def try_cmd(
    hypothesis: str = typer.Option(...),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """One autoresearch-loop attempt on scenarios/candidate.yaml: fast screen, then the full judge
    if the fast screen keeps it; keep = robust NPV improves on the best kept layout or the point is
    non-dominated (robust NPV, capex, accessibility 60) among kept layouts; else revert the file."""
    jd.check_fingerprint(JUDGE, root)
    st = root / R6 / "agent"
    st.mkdir(parents=True, exist_ok=True)
    kept_p = st / "kept.json"
    kept = json.loads(kept_p.read_text()) if kept_p.exists() else []
    cand = root / CANDIDATE
    lay = yaml.safe_load(cand.read_text())
    h = layout_hash(lay)
    t0 = time.monotonic()
    fast = Fast(root)
    variant = any(set(c) - {"id", "phase"} for c in lay.get("corridors", []))
    unknown = [c["id"] for c in lay.get("corridors", []) if c["id"] not in fast.index]
    fs = None if (variant or unknown) else fast.score(fast.genome_of(lay))
    pts = [np.array([k["robust_npv"], -k["capex_p50"], k["access_gain_120"]]) for k in kept]
    best = max((k["robust_npv"] for k in kept), default=-np.inf)

    def keeps(f: np.ndarray) -> bool:
        return f[0] > best + 1e-6 or not any(dominates(p, f) or np.allclose(p, f) for p in pts)

    row = {
        "time_utc": now(),
        "engine": "agent",
        "commit": git_head(root),
        "layout_hash": h,
        "hypothesis": hypothesis,
        "cost_usd": "in-session (run total in docs/cost-log.md)",
    }
    if fs is not None:
        f = np.array([fs["robust_npv"], -fs["capex_p50"], fs["access_gain_120"]])
        append_result({**row, "fidelity": "fast", "decision": "screen", **row_from_fast(fs)}, root)
        if not keeps(f):
            prev = st / "kept.yaml"
            if prev.exists():
                shutil.copy(prev, cand)
            append_result(
                {**row, "fidelity": "fast", "decision": "reverted", **row_from_fast(fs)}, root
            )
            typer.echo(f"REVERTED (fast) {json.dumps(row_from_fast(fs))}")
            return
    try:
        s = run_judge(cand, root / R6 / "agent" / "evals" / h, root, 4)
    except RuntimeError as e:  # a judge error is logged and the edit reverted, never retried
        prev = st / "kept.yaml"
        if prev.exists():
            shutil.copy(prev, cand)
        msg = str(e).replace("\n", " ")[-280:]
        append_result({**row, "fidelity": "full", "decision": "error-reverted", "notes": msg}, root)
        typer.echo(f"REVERTED (judge error) {msg}")
        return
    rf = row_from_full(s)
    if not s.get("feasible"):
        prev = st / "kept.yaml"
        if prev.exists():
            shutil.copy(prev, cand)
        append_result(
            {
                **row,
                "fidelity": "full",
                "decision": "reverted",
                **rf,
                "notes": "; ".join(s.get("errors", []))[:300],
            },
            root,
        )
        typer.echo(f"REVERTED (infeasible) {s.get('errors')}")
        return
    f = np.array([s["robust_npv"], -s["capex_sar_m"]["capex_p50"], s["access_gain_120"]])
    if keeps(f):
        kept.append(
            {
                "layout_hash": h,
                "robust_npv": float(f[0]),
                "capex_p50": float(-f[1]),
                "access_gain_120": float(f[2]),
                "hypothesis": hypothesis,
            }
        )
        kept_p.write_text(json.dumps(kept, indent=1))
        shutil.copy(cand, st / "kept.yaml")
        shutil.copy(cand, st / f"kept-{h}.yaml")
        dec = "kept"
    else:
        prev = st / "kept.yaml"
        if prev.exists():
            shutil.copy(prev, cand)
        dec = "reverted"
    append_result(
        {
            **row,
            "fidelity": "full",
            "decision": dec,
            **rf,
            "eval_seconds": round(time.monotonic() - t0, 1),
        },
        root,
    )
    typer.echo(f"{dec.upper()} {json.dumps(rf)}")


# --------------------------------------------------------------------------- re-score
def combined_front(root: Path = REPO_ROOT, budget: str | None = None, holdout: bool = False):
    """Union of the GA fronts (all seeds) of one budget (or all), reduced to non-dominated."""
    rows = []
    for d in sorted((root / R6 / "ga").glob("*")):
        tag = d.name
        if holdout != tag.endswith("-holdout") or (budget and not tag.startswith(budget + "-")):
            continue
        f = pd.read_csv(d / "front.csv")
        f["layout"] = [str(d / "layouts" / f"{k:03d}.yaml") for k in f.k]
        f["tag"] = tag
        rows.append(f)
    df = pd.concat(rows, ignore_index=True).drop_duplicates("layout_hash")
    F = np.c_[df.robust_npv, -df.capex_p50, df.access_gain_120]
    nd = nondominated_sort(F)[0]
    return df.iloc[sorted(nd)].sort_values("capex_p50").reset_index(drop=True)


@app.command("rescore")
def rescore_cmd(
    per_budget: int = typer.Option(6),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Full-judge re-score of a spread of front points per budget (max NPV, max access and
    capex quantiles between); writes runs/r6/rescore/fast_vs_full.csv."""
    h0 = jd.check_full(JUDGE, root)
    out = root / R6 / "rescore"
    out.mkdir(parents=True, exist_ok=True)
    pick = []
    for b in budgets(root):
        f = combined_front(root, b)
        idx = {int(f.robust_npv.idxmax()), int(f.access_gain_120.idxmax())}
        idx |= {int(round(q * (len(f) - 1))) for q in np.linspace(0, 1, per_budget)}
        for i in sorted(idx):
            pick.append((b, f.loc[i]))
    done = {}
    rows = []
    for b, r in pick:
        h = r.layout_hash
        lp = out / f"{h}.yaml"
        if h not in done:
            shutil.copy(r.layout, lp)
            s = run_judge(lp, out / h, root, 4)
            done[h] = s
            append_result(
                {
                    "time_utc": now(),
                    "engine": "ga-rescore",
                    "commit": git_head(root),
                    "layout_hash": h,
                    "hypothesis": f"full re-score of a {b} GA front point ({r.tag})",
                    "fidelity": "full",
                    "decision": "front",
                    "cost_usd": "0 (local)",
                    **row_from_full(s),
                },
                root,
            )
        s = done[h]
        rows.append(
            {
                "budget": b,
                "layout_hash": h,
                "source": r.layout,
                "fast_robust_npv": r.robust_npv,
                "full_robust_npv": s["robust_npv"],
                "fast_capex": r.capex_p50,
                "full_capex": s["capex_sar_m"]["capex_p50"],
                "fast_access_120": r.access_gain_120,
                "full_access_120": s.get("access_gain_120"),
                "n": r.n_corridors,
            }
        )
        pd.DataFrame(rows).to_csv(out / "fast_vs_full.csv", index=False)
    h1 = jd.check_full(JUDGE, root)
    (out / "rescore.json").write_text(json.dumps({"sha256_start": h0, "sha256_end": h1}) + "\n")
    typer.echo(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    app()
