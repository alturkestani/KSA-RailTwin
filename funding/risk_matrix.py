"""Risk-allocation matrix and fiscal-exposure metric definitions (W6; template at R1d, filled
per corridor family at R7). Schema and validation for
`cities/ksa/funding/risk_matrix_template.yaml` and `risk_matrix_<corridor>.yaml`.

    uv run python -m funding.risk_matrix validate [--path ...]
    uv run python -m funding.risk_matrix render [--path ...]     # Markdown table
    uv run python -m funding.risk_matrix build --corridor <id> --model <id> --out <yaml>   # R7
    uv run python -m funding.risk_matrix build-all                # every CP7 corridor x model
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from common import REPO_ROOT
from common.labels import LABEL
from funding.models import RISK_KEYS
from funding.sources import SOURCES_DIR, known_source_ids, unknown_ids

DEFAULT_PATH = REPO_ROOT / "cities" / "ksa" / "funding" / "risk_matrix_template.yaml"
COLUMNS = ["public", "private", "shared"]
REQUIRED_METRICS = [
    "upfront_public_capex",
    "availability_payments_share_of_budget",
    "contingent_liabilities",
    "net_fiscal_cost_horizon",
    "value_for_money_psc",
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RiskRow(_Strict):
    risk: str
    scope: str
    public: str | None = None
    private: str | None = None
    shared: str | None = None
    mechanism_options: list[str] = Field(min_length=1)
    mechanism: str | None = None  # the chosen clause type, in a filled matrix
    note: str = ""
    precedents: list[str] = Field(default_factory=list)

    def marks(self) -> list[str]:
        return [c for c in COLUMNS if (getattr(self, c) or "").strip().lower() == "x"]


class Metric(_Strict):
    id: str
    definition: str
    formula: str
    unit: str
    inputs: list[str] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)
    note: str | None = None


class RiskMatrix(_Strict):
    version: str
    template: bool
    corridor_family: str | None = None
    delivery_model: str | None = None
    corridor: str | None = None
    programme: str | None = None
    label: str | None = None
    evidence: dict | None = None
    columns: list[str]
    rows: list[RiskRow]
    fiscal_exposure_metrics: list[Metric] = Field(default_factory=list)
    note: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> RiskMatrix:
        if self.columns != COLUMNS:
            raise ValueError(f"columns must be {COLUMNS}")
        if [r.risk for r in self.rows] != RISK_KEYS:
            raise ValueError(f"rows must be, in order: {RISK_KEYS}")
        for r in self.rows:
            for c in COLUMNS:
                v = getattr(r, c)
                if v not in (None, "") and v.strip().lower() != "x":
                    raise ValueError(f"{r.risk}.{c}: cells hold 'x' or nothing")
            n = len(r.marks())
            if self.template and n:
                raise ValueError(f"{r.risk}: a template leaves the allocation empty")
            if not self.template:
                if n != 1:
                    raise ValueError(f"{r.risk}: exactly one of public/private/shared is 'x'")
                if not r.mechanism or not r.precedents:
                    raise ValueError(f"{r.risk}: a filled row names its mechanism and precedents")
        if not self.template and not (self.corridor_family and self.delivery_model):
            raise ValueError("a filled matrix names its corridor_family and delivery_model")
        if self.template:
            ids = [m.id for m in self.fiscal_exposure_metrics]
            missing = [m for m in REQUIRED_METRICS if m not in ids]
            if missing:
                raise ValueError(f"template misses fiscal-exposure metrics: {missing}")
        return self

    def cited(self) -> list[str]:
        ids = [p for r in self.rows for p in r.precedents]
        return ids + [s for m in self.fiscal_exposure_metrics for s in m.sources]


def load_matrix(path: Path = DEFAULT_PATH) -> RiskMatrix:
    return RiskMatrix.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def render(m: RiskMatrix) -> str:
    head = "| risk | scope | public | private | shared | mechanism (options) | precedents |"
    lines = [head, "|---|---|---|---|---|---|---|"]
    for r in m.rows:
        cells = [(getattr(r, c) or "").strip() for c in COLUMNS]
        mech = r.mechanism or "; ".join(r.mechanism_options)
        prec = ", ".join(r.precedents) or "—"
        lines.append(f"| {r.risk} | {r.scope} | {' | '.join(cells)} | {mech} | {prec} |")
    return "\n".join(lines)


# --------------------------------------------------------------------------- R7 build
FUNDING_DIR = REPO_ROOT / "cities" / "ksa" / "funding"
FISCAL_JSON = REPO_ROOT / "runs" / "r7" / "fiscal" / "fiscal.json"
VFM_JSON = REPO_ROOT / "runs" / "r7" / "vfm" / "vfm.json"
FAMILY = {"S3": "branch_spur", "S4": "commuter_belt", "S5": "station_addition"}


def _f(x: float) -> str:
    return f"{x:,.0f}"


def _rng(d: dict) -> str:
    return f"{_f(d['p10'])} / {_f(d['p50'])} / {_f(d['p90'])}"


def evidence_notes(entity: dict, vfm: dict, model: str, ex: dict, rp: str) -> dict[str, str]:
    """Per-risk corridor evidence (numbers from runs/r7/fiscal and runs/r7/vfm, robust case)."""
    b = entity["basis"]
    cx = b["capex"]
    r = ex["by_pop"][rp]
    cl = r["contingent_liabilities"]
    run = b["score"]
    bcr = " / ".join(
        f"{b['bcr_p10_60y'][p]:.2f}" for p in ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
    )
    p90 = " / ".join(
        _f(b["npv_at_p90_cost_60y"][p]) for p in ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
    )
    kind = ex["kind"]
    con = (
        f"Capex P10/P50/P90 {_f(cx['p10'])} / {_f(cx['p50'])} / {_f(cx['p90'])} SAR m (base P50 "
        f"{_f(cx['base_p50'])}; P90/P50 {cx['p90'] / cx['p50']:.2f}; {run}). NPV at P90 cost, "
        f"low / medium / high: {p90}."
    )
    if kind.startswith("public"):
        ret = _f(cl.get("retained_overrun_p90_pv", 0))
        con += f" The state carries the outturn: P90 minus P50 capex in PV {ret}."
    else:
        con += (
            f" Overrun above the private absorption capacity (A-fund-102) returns to the state: "
            f"expected PV {_f(cl['expected_pv'])}, at P90 capex {_f(cl['p90_pv'])} "
            "(runs/r7/fiscal)."
        )
    dem = (
        f"BCR P10 (60 y, without WEIs) low / medium / high {bcr}; PV fares / PV opex+renewals "
        f"{b['fare_over_opex_60y'][rp]:.2f} ({rp})."
    )
    if kind == "demand_concession":
        dem += (
            " MRG at A-fund-104 on the A-rcf-029 outturn ratio: expected PV "
            f"{_f(cl['expected_pv'])}"
            f" incl. overrun, P90 {_f(cl['p90_pv'])}."
        )
        if min(b["bcr_p10_60y"].values()) < 1:
            dem += " P10 BCR < 1: a demand-risk PPP is not a fit at P10 demand (skill rule)."
    rev = (
        f"PV fare revenue P50 {_f(b['pv_fare_revenue_p50_60y'][rp])} against PV opex+renewals "
        f"{_f(b['pv_opex_renewals_p50_60y'][rp])} SAR m (60 y, {rp}); a negative value means the "
        "addition lowers fare revenue on the host network in the model."
    )
    fin = (
        f"Net fiscal cost 60 y P10/P50/P90 {_rng(r['net_fiscal_cost_60y'])}; VfM vs public "
        f"{_f(vfm['central']['vfm'])} SAR m (runs/r7/vfm, > 0 favours the PPP)."
    )
    if cl["termination_worst_case_pv"]:
        fin += (
            f" Termination at opening, worst case PV {_f(cl['termination_worst_case_pv'])}; "
            f"probability-weighted (A-fund-006) {_f(cl['termination_expected_pv'])} (memorandum)."
        )
    host = host_note(entity)
    return {
        "construction": con,
        "demand": dem,
        "revenue": rev,
        "financing": fin,
        "operations": host,
        "land": host,
        "regulatory_force_majeure": "",
    }


def corridor_yaml(cid: str, root: Path = REPO_ROOT) -> dict:
    hits = list((root / "cities/ksa/corridors").glob(f"*/{cid}.yaml"))
    return yaml.safe_load(hits[0].read_text(encoding="utf-8")) if hits else {}


def line_layer(line: str, root: Path = REPO_ROOT) -> str:
    p = root / "cities/ksa/lines" / f"{line}.yaml"
    if not p.exists():
        return "unknown"
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    return f"{d.get('layer')}, status {d.get('status')}, source {d.get('source')}"


def host_note(entity: dict, root: Path = REPO_ROOT) -> str:
    """Where the corridor attaches: the host line and its layer (stations) or the route length."""
    out = []
    for p in entity["basis"]["parts"]:
        c = corridor_yaml(p["corridor"], root)
        name = c.get("name_en", p["corridor"])
        if c.get("family") == "station_addition" and " on " in name:
            line = name.split(" on ", 1)[1].split(" ")[0]
            out.append(f"{name}: host line {line} ({line_layer(line, root)}).")
        else:
            out.append(f"{name}: {c.get('length_km', 'n/a')} km, {c.get('line_type', '')}.")
    return " ".join(out)


def build_matrix(corridor: str, model: str, root: Path = REPO_ROOT) -> dict:
    """Fill the template for one corridor (or CP7 programme id S6-Lx) and candidate model."""
    params = yaml.safe_load(
        (root / "cities/ksa/assumptions/funding_r7.yaml").read_text(encoding="utf-8")
    )
    tpl = load_matrix(root / "cities/ksa/funding/risk_matrix_template.yaml")
    fis = json.loads((root / "runs/r7/fiscal/fiscal.json").read_text())
    vfm = json.loads((root / "runs/r7/vfm/vfm.json").read_text())
    grp = "programmes" if corridor.startswith("S6-") else "corridors"
    ent = fis[grp][corridor]
    rp = fis["robust_case"]
    ex = ent["models"][model]
    notes = evidence_notes(ent, vfm[grp][corridor], model, ex, rp)
    rules = params["allocation"][model]
    rows = []
    for row in tpl.rows:
        rule = rules[row.risk]
        d = row.model_dump()
        for c in COLUMNS:
            d[c] = "x" if rule["mark"] == c else ""
        d["mechanism"] = rule["mechanism"]
        d["precedents"] = list(dict.fromkeys(rule["precedents"]))
        d["note"] = " ".join(x for x in (rule["why"] + ".", notes[row.risk]) if x).strip()
        rows.append(d)
    fam = "programme" if grp == "programmes" else FAMILY[corridor.split("-")[0]]
    return {
        "version": "1.0",
        "template": False,
        "corridor_family": fam,
        "delivery_model": model,
        "corridor": corridor if grp == "corridors" else None,
        "programme": corridor if grp == "programmes" else None,
        "label": LABEL,
        "evidence": {
            "score": ent["basis"]["score"],
            "judge_sha256": ent["basis"]["judge_sha256"],
            "fiscal_run": "runs/r7/fiscal/fiscal.json",
            "vfm_run": "runs/r7/vfm/vfm.json",
            "population_case": rp,
        },
        "columns": COLUMNS,
        "rows": rows,
        "note": (
            "Allocation per cities/ksa/assumptions/funding_r7.yaml (allocation, A-fund-001); "
            "evidence from the judge v3 runs named above. Not a recommendation for any entity "
            "(rule 9); the recommendation is in cities/ksa/funding/recommendations.yaml."
        ),
    }


def matrix_path(corridor: str, model: str, root: Path = REPO_ROOT) -> Path:
    return root / "cities/ksa/funding" / f"risk_matrix_{corridor}--{model}.yaml"


def write_matrix(m: dict, out: Path) -> None:
    head = (
        f"# > **Document version:** {out.name} v1.1 | 4 Nov 2026 | Author: R7 builder "
        "(funding.risk_matrix build; generated, do not edit by hand) | Status: draft\n"
        f"# Label: {LABEL}\n"
    )
    RiskMatrix.model_validate(m)
    out.write_text(head + yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=100))


app = typer.Typer(add_completion=False, help="Risk-allocation matrix and fiscal-exposure metrics.")


@app.command()
def validate(
    path: Path = typer.Option(DEFAULT_PATH, "--path", exists=True),
    sources_dir: Path = typer.Option(SOURCES_DIR, "--sources-dir"),
) -> None:
    """Schema, row order, one allocation per row (filled) and every S-id resolving."""
    m = load_matrix(path)
    missing = unknown_ids(m.cited(), known_source_ids(sources_dir))
    if missing:
        typer.echo(f"FAIL: S-ids with no row in {sources_dir}/*.csv: {', '.join(missing)}")
        raise typer.Exit(1)
    kind = "template" if m.template else f"{m.corridor_family} / {m.delivery_model}"
    typer.echo(f"OK {path}: {kind}; {len(m.rows)} risks; {len(m.fiscal_exposure_metrics)} metrics")


@app.command("render")
def render_cmd(path: Path = typer.Option(DEFAULT_PATH, "--path", exists=True)) -> None:
    """Print the matrix as a Markdown table."""
    typer.echo(render(load_matrix(path)))


@app.command("build")
def build_cmd(
    corridor: str = typer.Option(..., "--corridor", help="corridor id or CP7 programme S6-Lx"),
    model: str = typer.Option(..., "--model", help="delivery model id from models.yaml"),
    out: Path = typer.Option(None, "--out"),
) -> None:
    """Fill the template for one corridor and model from runs/r7/fiscal and runs/r7/vfm."""
    p = out or matrix_path(corridor, model)
    write_matrix(build_matrix(corridor, model), Path(p))
    typer.echo(f"wrote {p}")


@app.command("build-all")
def build_all_cmd() -> None:
    """Every CP7 corridor x candidate model and every programme x model in runs/r7/fiscal."""
    fis = json.loads(FISCAL_JSON.read_text())
    n = 0
    for grp in ("corridors", "programmes"):
        for ent, v in fis[grp].items():
            for model in v["models"]:
                write_matrix(build_matrix(ent, model), matrix_path(ent, model))
                n += 1
    typer.echo(f"wrote {n} risk matrices under cities/ksa/funding/")


if __name__ == "__main__":
    app()
