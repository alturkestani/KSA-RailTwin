"""Fiscal exposure per corridor and per CP7 programme, by delivery model (W6, R7).

Metric definitions: `cities/ksa/funding/risk_matrix_template.yaml` (fiscal_exposure_metrics, R1d).
Inputs: the judge v3 scores (funding.inputs), the parameters in
`cities/ksa/assumptions/funding_r7.yaml` (A-fund ids), the MoF budget reference (S-fund-026).
Money: SAR million, 2025 prices; PV at 2026 on the appraisal schedule (Green Book 2026, A-cba-001).

Per model kind:
- public (fully public, public with private O&M): the state pays capex, opex and renewals and keeps
  fares; fiscal cost = the judge's `fiscal_cost` (PV(costs - fares), A-cba-312).
- availability (DBFOM/DBFM availability PPP): fixed-price contract capex = base capex x (1 + bid
  contingency, A-fund-007); the private side finances it at sovereign + premium (A-fund-101,
  A-fund-008) and is repaid by an availability payment over the term (A-fund-010) that also
  passes opex through; the state keeps fares, pays a construction contribution (A-fund-002) and
  transaction costs (A-fund-103), and carries the overrun beyond the private absorption capacity
  (A-fund-102) as a contingent liability (PFRAM, S-fund-021/023).
- demand_concession: the concessionaire keeps fares and pays opex over the term; the state pays a
  viability-gap grant at construction and a minimum revenue guarantee (A-fund-104) sized on the
  reference-class outturn ratio (A-rcf-029).
- *_plus_lvc: as the base kind; land value capture is reported as the break-even value it would
  need (no Saudi instrument reviewed: unclear).

    uv run python -m funding.fiscal build [--seed 1] [--out runs/r7/fiscal]
    uv run python -m funding.fiscal report      # docs/fiscal-exposure.md tables to stdout
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from economics import discounting
from funding import inputs

PARAMS_PATH = REPO_ROOT / "cities" / "ksa" / "assumptions" / "funding_r7.yaml"
UPLIFTS_PATH = REPO_ROOT / "cities" / "ksa" / "costs" / "uplifts.yaml"
OUT = Path("runs/r7/fiscal")
HORIZONS = (30, 40, 60)
POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
Z90 = 1.2815515655446004
QS = ("p10", "p50", "p90")


# --------------------------------------------------------------------------- parameters
def load_params(path: Path = PARAMS_PATH) -> dict[str, Any]:
    p = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for k, v in p["params"].items():
        if not ({"source", "assumption"} & set(v)):
            raise ValueError(f"{k}: needs source: or assumption: (rule 1)")
        if "id" not in v:
            raise ValueError(f"{k}: needs a register id")
    return p


def central(p: dict[str, Any]) -> dict[str, float]:
    """The central value of every numeric parameter, keyed by name."""
    return {k: float(v["value"]) for k, v in p["params"].items() if "value" in v}


def ridership_ratio_table(path: Path = UPLIFTS_PATH, uid: str = "U-ridership-rail-fbc"):
    for u in yaml.safe_load(Path(path).read_text(encoding="utf-8"))["uplifts"]:
        if isinstance(u, dict) and u.get("id") == uid:
            pts = u["params"]["percentiles"]
            return np.array(sorted(pts)) / 100.0, np.array([pts[k] for k in sorted(pts)])
    raise KeyError(uid)


def expected_shortfall(g: float, probs: np.ndarray, vals: np.ndarray) -> float:
    """E[max(0, g - R)] for the empirical outturn ratio R (percentile table; tails held flat)."""
    grid = np.linspace(0.0005, 0.9995, 1000)
    r = np.interp(grid, probs, vals)
    return float(np.mean(np.maximum(0.0, g - r)))


def shortfall_at(g: float, probs: np.ndarray, vals: np.ndarray, q: float) -> float:
    return max(0.0, g - float(np.interp(q, probs, vals)))


# --------------------------------------------------------------------------- lognormal tail
def lognormal_fit(k50: float, k90: float) -> tuple[float, float]:
    sigma = max(math.log(k90 / k50), 1e-9) / Z90
    return math.log(k50), sigma


def ln_mean(k50: float, k90: float) -> float:
    mu, s = lognormal_fit(k50, k90)
    return math.exp(mu + s * s / 2)


def ln_excess(k50: float, k90: float, x: float) -> float:
    """E[max(0, K - x)] for K lognormal through (P50, P90) (A-fund-108)."""
    mu, s = lognormal_fit(k50, k90)
    if x <= 0:
        return ln_mean(k50, k90) - x
    d2 = (mu - math.log(x)) / s
    d1 = d2 + s
    phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))  # noqa: E731
    return math.exp(mu + s * s / 2) * phi(d1) - x * phi(d2)


# --------------------------------------------------------------------------- basis
@dataclass
class Part:
    """One corridor (phase) inside an entity; weights split the entity's PVs across parts."""

    corridor: str
    phase: int
    w_capex: float
    w_base: float
    w_opex: float
    w_fare: float


@dataclass
class Basis:
    entity: str
    kind: str  # corridor | programme
    score_path: str
    judge: str
    capex: dict[str, float]  # p10, p50, p90, base_p50
    rows: dict[tuple[str, int], dict[str, float]]
    bcr_p10: dict[str, float]
    npv_at_p90_cost: dict[str, float]
    robust_npv: float
    parts: list[Part] = field(default_factory=list)


def _rows(score: dict[str, Any], rate_case: str) -> dict[tuple[str, int], dict[str, float]]:
    return {
        (r["population"], int(r["horizon"])): r
        for r in score["appraisal_rows"]
        if r["rate_case"] == rate_case
    }


def basis_from_score(
    entity: str, kind: str, path: Path, rate_case: str, parts: list[Part]
) -> Basis:
    s = inputs.load(path)
    cx = s["capex_sar_m"]
    rows = _rows(s, rate_case)
    return Basis(
        entity=entity,
        kind=kind,
        score_path=str(Path(path).relative_to(REPO_ROOT)),
        judge=inputs.judge_hash(path),
        capex={
            "p10": cx["capex_p10"],
            "p50": cx["capex_p50"],
            "p90": cx["capex_p90"],
            "base_p50": cx["capex_base_p50"],
        },
        rows=rows,
        bcr_p10={p: rows[(p, 60)]["bcr_p10"] for p in POPS},
        npv_at_p90_cost={p: rows[(p, 60)]["npv_at_p90_cost"] for p in POPS},
        robust_npv=float(s["robust_npv"]),
        parts=parts,
    )


def corridor_bases(params: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Basis]:
    rc = params["appraisal"]["rate_case"]
    out: dict[str, Basis] = {}
    for cid, ph in inputs.corridor_phases(root).items():
        path = inputs.corridor_score_path(cid, ph, root)
        out[cid] = basis_from_score(cid, "corridor", path, rc, [Part(cid, ph, 1, 1, 1, 1)])
    return out


def programme_bases(
    params: dict[str, Any], cors: dict[str, Basis], root: Path = REPO_ROOT
) -> dict[str, Basis]:
    """Programme = the layout's own judge score; its PVs are split across corridors in proportion
    to their standalone PVs (capex is exact and additive; opex and fares are not, A-fund-109)."""
    rc = params["appraisal"]["rate_case"]
    rp = params["appraisal"]["robust_case"]
    out: dict[str, Basis] = {}
    for lay, sid in inputs.LAYOUTS.items():
        cs = [(c["id"], int(c["phase"])) for c in inputs.scenario(lay, root)["layout"]["corridors"]]

        def share(key: str, cs=cs) -> list[float]:
            v = [
                cors[c].capex[key] if key in cors[c].capex else cors[c].rows[(rp, 60)][key]
                for c, _ in cs
            ]
            t = sum(v)
            return [x / t for x in v]

        wc, wb = share("p50"), share("base_p50")
        wo, wf = share("pv_opex_renewals_p50"), share("pv_fare_revenue_p50")
        parts = [Part(c, ph, wc[i], wb[i], wo[i], wf[i]) for i, (c, ph) in enumerate(cs)]
        path = inputs.layout_score_path(lay, root)
        out[sid] = basis_from_score(sid, "programme", path, rc, parts)
    return out


# --------------------------------------------------------------------------- cash-flow engine
@dataclass
class Settings:
    rate_case: str
    pv_year: int
    c: dict[str, float]  # central parameter values (overridable for sensitivities)
    ratio_probs: np.ndarray
    ratio_vals: np.ndarray
    budget_years: dict[int, float]


def settings(params: dict[str, Any], rate_case: str | None = None, **override: float) -> Settings:
    c = central(params)
    c.update(override)
    probs, vals = ridership_ratio_table()
    by = {int(k): float(v) for k, v in params["params"]["budget_reference"]["years"].items()}
    rc = rate_case or params["appraisal"]["rate_case"]
    return Settings(rc, int(params["appraisal"]["pv_year"]), c, probs, vals, by)


def dfs(st: Settings, last_year: int) -> np.ndarray:
    rc = st.rate_case
    sched = (
        discounting.constant(float(rc.split(":", 1)[1]))
        if rc.startswith("const:")
        else discounting.SCHEDULES[rc]
    )
    return discounting.factors(sched, last_year - st.pv_year + 1)


def years(st: Settings, last_year: int) -> np.ndarray:
    return np.arange(st.pv_year, last_year + 1)


def budget_real(st: Settings, yrs: np.ndarray, growth: float | None = None) -> np.ndarray:
    """Total state expenditure in 2025 prices (SAR m): MoF 2026-2028 (S-fund-026), then nominal
    growth (A-fund-005), deflated by CPI (A-fund-105)."""
    g = st.c["budget_growth_nominal"] if growth is None else growth
    pi = st.c["cpi_inflation"]
    last = max(st.budget_years)
    out = []
    for y in yrs:
        nom = st.budget_years.get(int(y))
        if nom is None:
            nom = st.budget_years[last] * (1 + g) ** (int(y) - last)
        out.append(nom * 1000.0 / (1 + pi) ** (int(y) - 2025))
    return np.array(out)


def annual_equivalent(pv: float, df: np.ndarray, yrs: np.ndarray, a: int, b: int) -> float:
    m = (yrs >= a) & (yrs <= b)
    s = float(df[m].sum())
    return pv / s if s > 0 else 0.0


@dataclass
class Flows:
    """Annual public cash flows (SAR m, 2025 prices) by year, and their PVs."""

    yrs: np.ndarray
    capex: np.ndarray
    ap: np.ndarray
    opex: np.ndarray
    fares: np.ndarray
    txn: np.ndarray
    contingent: np.ndarray
    grant: np.ndarray

    def total(self) -> np.ndarray:
        return (
            self.capex + self.ap + self.opex + self.txn + self.contingent + self.grant - self.fares
        )


def flows(
    b: Basis, st: Settings, kind: str, pop: str, horizon: int, q: str, expected: bool = False
) -> Flows:
    """Public cash flows for one entity, model kind, population case, horizon and capex quantile.
    `expected=True` uses the lognormal mean / expected excess instead of quantile q."""
    c = st.c
    last = max(p.phase for p in b.parts) + horizon + 1
    yrs = years(st, last)
    row = b.rows[(pop, 60)]  # annual equivalents always from the 60-year row (A-fund-109)
    n = len(yrs)
    z = {k: np.zeros(n) for k in ("capex", "ap", "opex", "fares", "txn", "contingent", "grant")}
    k50, k90 = b.capex["p50"], b.capex["p90"]
    kq = ln_mean(k50, k90) if expected else b.capex[q]
    r = c["sovereign_real_rate"] + c["private_finance_premium"]
    term = int(c["ppp_term_years"])
    for p in b.parts:
        build = (yrs >= p.phase - 3) & (yrs <= p.phase - 1)
        ops_end = p.phase + horizon - 1
        ops = (yrs >= p.phase) & (yrs <= ops_end)
        e60 = p.phase + 59
        last60 = max(last, e60)
        df60, yrs60 = dfs(st, last60), years(st, last60)
        o = annual_equivalent(row["pv_opex_renewals_p50"] * p.w_opex, df60, yrs60, p.phase, e60)
        f = annual_equivalent(row["pv_fare_revenue_p50"] * p.w_fare, df60, yrs60, p.phase, e60)
        kc = b.capex["base_p50"] * p.w_base * (1 + c["bid_contingency"])
        if kind == "public":
            z["capex"] += np.where(build, kq * p.w_capex / 3.0, 0.0)
            z["opex"] += np.where(ops, o, 0.0)
            z["fares"] += np.where(ops, f, 0.0)
            continue
        in_term = ops & (yrs <= p.phase + term - 1)
        after = ops & (yrs > p.phase + term - 1)
        z["txn"] += np.where(yrs == p.phase - 3, c["transaction_cost"] * kc, 0.0)
        # overrun above the private absorption capacity returns to the state (PFRAM contingent)
        cap = kc * (1 + c["absorption_capacity"])
        k_part = (k50 * p.w_capex, k90 * p.w_capex)
        loss = ln_excess(k_part[0], k_part[1], cap) if expected else max(0.0, kq * p.w_capex - cap)
        z["contingent"] += np.where(yrs == p.phase, loss, 0.0)
        z["opex"] += np.where(after, o, 0.0)
        z["fares"] += np.where(after, f, 0.0)
        if kind == "availability":
            s = c["public_contribution_availability"]
            z["capex"] += np.where(build, s * kc / 3.0, 0.0)
            fin = sum((1 - s) * kc / 3.0 * (1 + r) ** (p.phase - y) for y in yrs[build])
            ann = fin * r / (1 - (1 + r) ** -term)
            z["ap"] += np.where(in_term, ann + o, 0.0)
            z["fares"] += np.where(in_term, f, 0.0)
        elif kind == "demand_concession":
            fin = sum(kc / 3.0 * (1 + r) ** (p.phase - y) for y in yrs[build])
            pv_net = sum((f - o) / (1 + r) ** (y - p.phase) for y in yrs[in_term])
            gap = max(0.0, fin - pv_net)  # viability gap at opening, paid as a grant in build years
            grant_now = gap / sum((1 + r) ** (p.phase - y) for y in yrs[build])
            z["grant"] += np.where(build, grant_now, 0.0)
            g = c["mrg_level"]
            if expected:
                sh = expected_shortfall(g, st.ratio_probs, st.ratio_vals)
            else:
                # revenue shortfall is a demand risk: the low capex quantile is not the low demand
                # case; P10/P50/P90 here map to the ratio's P90/P50/P10 (worst demand at P90)
                qq = {"p10": 0.9, "p50": 0.5, "p90": 0.1}[q]
                sh = shortfall_at(g, st.ratio_probs, st.ratio_vals, qq)
            z["contingent"] += np.where(in_term, sh * f, 0.0)
        else:
            raise ValueError(kind)
    return Flows(yrs, **z)


def pv(x: np.ndarray, st: Settings, yrs: np.ndarray) -> float:
    return float(np.dot(x, dfs(st, int(yrs[-1]))))


def base_kind(model_kind: str) -> str:
    return {
        "public": "public",
        "availability": "availability",
        "demand_concession": "demand_concession",
        "public_plus_lvc": "public",
        "availability_plus_lvc": "availability",
    }[model_kind]


# --------------------------------------------------------------------------- metrics
def exposure(b: Basis, st: Settings, model: str, model_kind: str) -> dict[str, Any]:
    """All five fiscal-exposure metrics for one entity and model (every population case)."""
    kind = base_kind(model_kind)
    out: dict[str, Any] = {"entity": b.entity, "model": model, "kind": model_kind, "by_pop": {}}
    for pop in POPS:
        res: dict[str, Any] = {}
        for h in HORIZONS:
            nfc = {}
            for q in QS:
                # one method per series (verify-R7 F2): the judge's own fiscal cost where the
                # score has every horizon (layouts), else the cash-flow engine (corridors)
                if kind == "public" and all((pop, hh) in b.rows for hh in HORIZONS):
                    row = b.rows[(pop, h)]
                    if q == "p50":
                        nfc[q] = row["fiscal_cost_p50"]
                    else:
                        rv = row["pv_residual_p50"] * b.capex[q] / b.capex["p50"]
                        nfc[q] = row[f"pvc_{q}"] + rv
                else:
                    fl = flows(b, st, kind, pop, h, q)
                    nfc[q] = pv(fl.total(), st, fl.yrs)
            lo, mid, hi = sorted(nfc.values())
            res[f"net_fiscal_cost_{h}y"] = {"p10": lo, "p50": mid, "p90": hi}
            fe = flows(b, st, kind, pop, h, "p50", expected=True)
            res[f"net_fiscal_cost_{h}y"]["expected"] = pv(fe.total(), st, fe.yrs)
        h = 60
        up = {}
        for q in QS:
            fl = flows(b, st, kind, pop, h, q)
            pub = fl.capex + fl.grant  # state capex plus any viability-gap grant
            up[q] = {"sum": float(pub.sum()), "pv": pv(pub, st, fl.yrs)}
        res["upfront_public_capex"] = up
        # budget share: annual firm payments (AP or grant, plus public capex) / total expenditure
        shares = {}
        for q in QS:
            fl = flows(b, st, kind, pop, h, q)
            firm = fl.capex + fl.ap + fl.grant + fl.opex + fl.txn - fl.fares
            for tag, g in (
                ("central", None),
                ("low_growth", st_param(st, "low", "budget_growth_nominal")),
                ("high_growth", st_param(st, "high", "budget_growth_nominal")),
            ):
                e = budget_real(st, fl.yrs, g)
                sh = np.where(e > 0, firm / e, 0.0)
                i = int(np.argmax(sh))
                shares.setdefault(q, {})[tag] = {
                    "peak_pct": 100 * float(sh[i]),
                    "peak_year": int(fl.yrs[i]),
                    "mean_pct_operating_years": 100
                    * float(sh[fl.yrs >= min(p.phase for p in b.parts)].mean()),
                }
        res["budget_share"] = shares
        # contingent liabilities (memorandum, PFRAM): expected and P90
        fe = flows(b, st, kind, pop, h, "p50", expected=True)
        f90 = flows(b, st, kind, pop, h, "p90")
        cl = {
            "expected_pv": pv(fe.contingent, st, fe.yrs),
            "p90_pv": pv(f90.contingent, st, f90.yrs),
            "termination_worst_case_pv": 0.0,
            "termination_expected_pv": 0.0,
        }
        if kind in ("availability", "demand_concession"):
            r = st.c["sovereign_real_rate"] + st.c["private_finance_premium"]
            s = st.c["public_contribution_availability"] if kind == "availability" else 0.0
            worst = 0.0
            for p in b.parts:
                kc = b.capex["base_p50"] * p.w_base * (1 + st.c["bid_contingency"])
                fin = sum((1 - s) * kc / 3.0 * (1 + r) ** k for k in (3, 2, 1))
                worst += fin * dfs(st, p.phase)[-1]
            cl["termination_worst_case_pv"] = worst
            cl["termination_expected_pv"] = st.c["termination_probability"] * worst
        if kind == "public":
            cl["retained_overrun_p90_pv"] = up["p90"]["pv"] - up["p50"]["pv"]
        res["contingent_liabilities"] = cl
        # timing profile (P50 capex, central growth): five-year buckets of firm public payments
        fl = flows(b, st, kind, pop, h, "p50")
        firm = fl.capex + fl.ap + fl.grant + fl.opex + fl.txn - fl.fares
        buckets = {}
        for a in range(2026, int(fl.yrs[-1]) + 1, 5):
            m = (fl.yrs >= a) & (fl.yrs < a + 5)
            if m.any():
                buckets[f"{a}-{a + 4}"] = float(firm[m].sum())
        res["timing_p50_5y"] = buckets
        out["by_pop"][pop] = res
    if model_kind.endswith("_plus_lvc"):
        rp = POPS[0]
        out["lvc_break_even_pv"] = out["by_pop"][rp]["net_fiscal_cost_60y"]["p50"]
    return out


def st_param(st: Settings, which: str, name: str) -> float:
    p = load_params()["params"][name]
    return float(p[which])


def candidates(params: dict[str, Any], corridor: str) -> list[str]:
    fam = corridor.split("-", 1)[1].split("-")[0] if corridor.startswith("S") else ""
    return params["candidates"][fam]


def build_all(params: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    st = settings(params)
    cors = corridor_bases(params, root)
    progs = programme_bases(params, cors, root)
    out: dict[str, Any] = {
        "label": LABEL,
        "units": "SAR million, 2025 prices; PV at 2026 on the Green Book 2026 schedule",
        "robust_case": params["appraisal"]["robust_case"],
        "corridors": {},
        "programmes": {},
        "baseline_s1": baseline_s1(root),
    }
    for cid, b in cors.items():
        out["corridors"][cid] = {
            "basis": basis_summary(b),
            "models": {
                m: exposure(b, st, m, params["fiscal_kind"][m]) for m in candidates(params, cid)
            },
        }
    for sid, b in progs.items():
        models = sorted(
            {m for p in b.parts for m in candidates(params, p.corridor)}
            & {"fully_public_sar", "ppp_dbfom_availability", "ppp_dbfom_demand_risk"}
        )
        out["programmes"][sid] = {
            "basis": basis_summary(b),
            "models": {m: exposure(b, st, m, params["fiscal_kind"][m]) for m in models},
        }
    return out


def basis_summary(b: Basis) -> dict[str, Any]:
    return {
        "score": b.score_path,
        "judge_sha256": b.judge,
        "capex": b.capex,
        "robust_npv": b.robust_npv,
        "bcr_p10_60y": b.bcr_p10,
        "npv_at_p90_cost_60y": b.npv_at_p90_cost,
        "parts": [p.__dict__ for p in b.parts],
        "farebox_cover_60y": {
            p: b.rows[(p, 60)]["pv_fare_revenue_p50"]
            / (b.rows[(p, 60)]["pv_capex_p50"] + b.rows[(p, 60)]["pv_opex_renewals_p50"])
            for p in POPS
        },
        "pv_fare_revenue_p50_60y": {p: b.rows[(p, 60)]["pv_fare_revenue_p50"] for p in POPS},
        "judge_fiscal_cost_p50_60y": {p: b.rows[(p, 60)]["fiscal_cost_p50"] for p in POPS},
        "fiscal_series_method": (
            "judge fiscal_cost (all horizons)"
            if all((p, h) in b.rows for p in POPS for h in HORIZONS)
            else "cash-flow engine (all horizons); judge 60 y fiscal cost as cross-check"
        ),
        "pv_opex_renewals_p50_60y": {p: b.rows[(p, 60)]["pv_opex_renewals_p50"] for p in POPS},
        "fare_over_opex_60y": {
            p: b.rows[(p, 60)]["pv_fare_revenue_p50"] / b.rows[(p, 60)]["pv_opex_renewals_p50"]
            for p in POPS
        },
    }


def baseline_s1(root: Path = REPO_ROOT) -> dict[str, Any]:
    d = json.loads((root / inputs.S1_CBA / "results.json").read_text())
    out = {"case": d["case"], "run": str(inputs.S1_CBA), "rows": {}}
    for r in d["results"]:
        if r["rate_case"] == d["central_rate_case"]:
            out["rows"][f"{r['population']}|{r['horizon']}"] = {
                "fiscal_cost": r["fiscal_cost"],
                "firr": r["firr"],
                "pv_capex": r["pv_capex"],
                "pv_fare_revenue": r.get("pv_fare_revenue"),
            }
    return out


# --------------------------------------------------------------------------- CLI
app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Fiscal exposure (R7)."""


@app.command("build")
def build_cmd(
    seed: int = typer.Option(1, "--seed", help="recorded only: every input is a seed-1 judge run"),
    out: Path = typer.Option(OUT, "--out"),
) -> None:
    """Compute every corridor x model and programme x model exposure; write fiscal.json + meta."""
    from common.runmeta import write_meta

    params = load_params()
    res = build_all(params)
    res["seed"] = seed
    res["assumption_ids"] = sorted({v["id"] for v in params["params"].values()})
    o = REPO_ROOT / out
    o.mkdir(parents=True, exist_ok=True)
    (o / "fiscal.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    write_meta(o, seed, params, extra={"label": LABEL, "inputs": "funding.inputs list"})
    n = sum(len(v["models"]) for v in res["corridors"].values())
    n_p = len(res["programmes"])
    typer.echo(f"wrote {out}/fiscal.json: {n} corridor x model, {n_p} programmes")


if __name__ == "__main__":
    app()
