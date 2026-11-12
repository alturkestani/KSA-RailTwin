"""Value-for-money logic: public sector comparator (PSC) vs availability PPP (W6, R7).

PSC-style reasoning (Green Book 2026 A.13-A.14, S-fund-024; optimism bias S-fund-025):

    VfM = E[net fiscal cost, public delivery] - E[net fiscal cost, availability PPP]

both in PV at 2026 on the appraisal schedule over 60 years, robust population case, from the same
cash-flow engine (`funding.fiscal.flows`, expected values over the capex distribution, A-fund-108).
VfM > 0 favours the PPP on cost. The PSC carries the uplifted capex (reference-class optimism
bias, already inside the judge's capex draws); the PPP carries the fixed-price bid (base capex x
(1 + bid contingency)), private finance at sovereign + premium, transaction costs, and the
overrun beyond the private absorption capacity as a retained contingent liability.

For every parameter VfM depends on, the switching value (VfM = 0) is solved with Brent's method;
parameters with no Saudi source are flagged.

    uv run python -m funding.vfm build [--out runs/r7/vfm]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from scipy.optimize import brentq

from common import REPO_ROOT
from common.labels import LABEL
from funding import fiscal

OUT = Path("runs/r7/vfm")
# Sourcing states (R8, verify-R7 O11): "sourced" for Saudi Arabia; "reference_class" = sourced
# from a foreign reference class whose transfer to Saudi Arabia is unclear; "assumption".
SOURCED, REFERENCE_CLASS, ASSUMPTION = "sourced", "reference_class", "assumption"
SOURCING_TEXT = {
    SOURCED: "sourced",
    REFERENCE_CLASS: "sourced, reference class — unclear for Saudi Arabia",
    ASSUMPTION: "no (assumption)",
}
# parameter -> (bracket searched for a switching value, sourcing state)
DRIVERS: dict[str, tuple[tuple[float, float], str]] = {
    "bid_contingency": ((-0.95, 3.0), ASSUMPTION),
    "private_finance_premium": ((-0.035, 0.15), REFERENCE_CLASS),  # NAO 2018 (UK), S-fund-r7-001
    "transaction_cost": ((-1.0, 1.0), ASSUMPTION),
    "absorption_capacity": ((0.0, 5.0), ASSUMPTION),
    "public_contribution_availability": ((0.0, 1.0), ASSUMPTION),
}


def nfc_expected(b: fiscal.Basis, st: fiscal.Settings, kind: str, pop: str, h: int = 60) -> float:
    fl = fiscal.flows(b, st, kind, pop, h, "p50", expected=True)
    return fiscal.pv(fl.total(), st, fl.yrs)


def vfm(
    b: fiscal.Basis,
    params: dict[str, Any],
    pop: str,
    rate_case: str | None = None,
    **override: float,
) -> dict[str, float]:
    st = fiscal.settings(params, rate_case=rate_case, **override)
    psc = nfc_expected(b, st, "public", pop)
    ppp = nfc_expected(b, st, "availability", pop)
    return {"psc": psc, "ppp": ppp, "vfm": psc - ppp, "vfm_pct_psc": 100 * (psc - ppp) / psc}


def switching_value(
    b: fiscal.Basis, params: dict[str, Any], pop: str, name: str, bracket: tuple[float, float]
) -> float | None:
    """Value of `name` at which VfM = 0 (others central), or None if no sign change in bracket."""

    def g(x: float) -> float:
        return vfm(b, params, pop, **{name: x})["vfm"]

    lo, hi = bracket
    a, z = g(lo), g(hi)
    if a == 0:
        return lo
    if a * z > 0:
        return None
    return float(brentq(g, lo, hi, xtol=1e-6))


def assess(b: fiscal.Basis, params: dict[str, Any], pop: str) -> dict[str, Any]:
    p = params["params"]
    res: dict[str, Any] = {"central": vfm(b, params, pop), "drivers": {}}
    for name, (bracket, sourcing) in DRIVERS.items():
        lo, hi = float(p[name]["low"]), float(p[name]["high"])
        sv = switching_value(b, params, pop, name, bracket)
        inside = sv is not None and lo <= sv <= hi
        res["drivers"][name] = {
            "id": p[name]["id"],
            "central": float(p[name]["value"]),
            "range": [lo, hi],
            "vfm_at_low": vfm(b, params, pop, **{name: lo})["vfm"],
            "vfm_at_high": vfm(b, params, pop, **{name: hi})["vfm"],
            "switching_value": sv,
            "switch_within_range": inside,
            "sourced": sourcing == SOURCED,
            "sourcing": sourcing,
            "bracket_searched": list(bracket),
        }
    # discounting sensitivity: the appraisal schedule is the central case (Green Book: the PSC is
    # not charged a financing cost); flat 5 % (EC Guide, A-cba-002) and the sovereign real rate
    sov = float(p["sovereign_real_rate"]["value"])
    res["rate_sensitivity"] = {
        rc: vfm(b, params, pop, rate_case=rc)["vfm"] for rc in ("flat_5", f"const:{sov}")
    }
    c = res["central"]["vfm"]
    flips = [k for k, d in res["drivers"].items() if d["switch_within_range"]]
    res["sign_central"] = "favours PPP" if c > 0 else "favours public delivery"
    # anything not sourced for Saudi Arabia counts, so a reference-class driver can be named (O11)
    res["depends_on_unsourced"] = [k for k in flips if not res["drivers"][k]["sourced"]]
    res["not_sourced_for_ksa"] = [k for k, d in res["drivers"].items() if not d["sourced"]]
    res["sign_robust_to_registered_ranges"] = not flips
    return res


def build_all(params: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    cors = fiscal.corridor_bases(params, root)
    progs = fiscal.programme_bases(params, cors, root)
    pop = params["appraisal"]["robust_case"]
    out: dict[str, Any] = {
        "label": LABEL,
        "units": "SAR million PV at 2026, 2025 prices, 60 years, expected values",
        "population_case": pop,
        "definition": "VfM = E[NFC public] - E[NFC availability PPP]; > 0 favours the PPP",
        "corridors": {k: assess(b, params, pop) for k, b in cors.items()},
        "programmes": {k: assess(b, params, pop) for k, b in progs.items()},
    }
    return out


app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Value-for-money logic (R7)."""


@app.command("build")
def build_cmd(
    seed: int = typer.Option(1, "--seed", help="recorded only: every input is a seed-1 judge run"),
    out: Path = typer.Option(OUT, "--out"),
) -> None:
    """Write runs/r7/vfm/vfm.json (central VfM, one-at-a-time ranges, switching values)."""
    from common.runmeta import write_meta

    params = fiscal.load_params()
    res = build_all(params)
    res["seed"] = seed
    o = REPO_ROOT / out
    o.mkdir(parents=True, exist_ok=True)
    (o / "vfm.json").write_text(json.dumps(res, indent=1) + "\n")
    write_meta(o, seed, params, extra={"label": LABEL})
    for grp in ("corridors", "programmes"):
        for k, v in res[grp].items():
            typer.echo(f"{k}: VfM {v['central']['vfm']:,.0f} SAR m ({v['sign_central']})")


if __name__ == "__main__":
    app()
