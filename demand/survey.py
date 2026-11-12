"""Stated-preference survey design generator (W7, R1d). DESIGN ONLY: nothing here fields a survey.

Builds a D-efficient labelled choice design for a multinomial logit (MNL) with fixed literature
priors, by coordinate exchange over level indices from several seeded random starts, then splits
the tasks into blocks and appends one dominance-check task per block.

    uv run python -m demand.survey validate --config docs/survey/design.yaml
    uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 \
        --out docs/survey/choice_sets.csv

Config schema: `docs/survey/design.yaml` (documented in `docs/survey/design.md`). Every prior and
every attribute carries `source:` (an S-id) or `assumption:` (an A-id); the numbers live in the
YAML, never here. The method follows the efficient-design literature cited in
`docs/survey/design.md` (MNL Fisher information, D-error = det(I^-1)^(1/K)).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Literal

import numpy as np
import typer
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from common.runmeta import build_meta, seed_option

FIELDING_NOTE = "designed, not fielded"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Cited(_Strict):
    source: str | None = None
    assumption: str | None = None

    @model_validator(mode="after")
    def _cited(self) -> _Cited:
        if not (self.source or self.assumption):
            raise ValueError("needs `source:` (S-id) or `assumption:` (A-id)")
        return self


class Asc(_Cited):
    prior: float


class Attribute(_Cited):
    id: str
    label_en: str
    label_ar: str
    unit: str
    levels: list[float] = Field(min_length=2)
    level_labels_en: list[str] | None = None
    level_labels_ar: list[str] | None = None
    coding: Literal["linear", "dummy"]
    param: str
    prior: float | list[float]
    note: str | None = None

    @model_validator(mode="after")
    def _shape(self) -> Attribute:
        n = len(self.levels)
        if len(set(self.levels)) != n:
            raise ValueError(f"{self.id}: levels must be distinct")
        for name in ("level_labels_en", "level_labels_ar"):
            labels = getattr(self, name)
            if labels is not None and len(labels) != n:
                raise ValueError(f"{self.id}: {name} must have {n} entries")
        if self.coding == "linear" and not isinstance(self.prior, float | int):
            raise ValueError(f"{self.id}: linear coding needs a single float prior")
        if self.coding == "dummy" and (
            not isinstance(self.prior, list) or len(self.prior) != n - 1
        ):
            raise ValueError(f"{self.id}: dummy coding needs {n - 1} priors (one per level > 0)")
        return self

    def utilities(self) -> np.ndarray:
        """Prior utility contribution of each level (dummy: level 0 is the base)."""
        if self.coding == "linear":
            return float(self.prior) * np.asarray(self.levels, dtype=float)
        return np.concatenate([[0.0], np.asarray(self.prior, dtype=float)])


class Alternative(_Strict):
    id: str
    label_en: str
    label_ar: str
    asc: Asc
    reference: bool = False
    attributes: list[Attribute] = Field(default_factory=list)
    note: str | None = None


class DesignSettings(_Strict):
    n_tasks: int = Field(ge=2)
    n_blocks: int = Field(ge=1)
    dominance_task: bool = True
    starts: int = Field(default=10, ge=1)
    max_sweeps: int = Field(default=30, ge=1)

    @model_validator(mode="after")
    def _blocks(self) -> DesignSettings:
        if self.n_tasks % self.n_blocks:
            raise ValueError("n_tasks must be divisible by n_blocks")
        return self


class SurveyDesign(_Strict):
    version: str
    label: str
    reference_trip: str | None = None
    priors_file: str | None = None
    design: DesignSettings
    alternatives: list[Alternative] = Field(min_length=2)

    @model_validator(mode="after")
    def _rules(self) -> SurveyDesign:
        if FIELDING_NOTE not in self.label:
            raise ValueError(f"label must say '{FIELDING_NOTE}' (rule 7)")
        ids = [a.id for a in self.alternatives]
        if len(set(ids)) != len(ids):
            raise ValueError("alternative ids must be unique")
        refs = [a for a in self.alternatives if a.reference]
        if len(refs) != 1:
            raise ValueError("exactly one alternative must have `reference: true`")
        if refs[0].asc.prior != 0.0:
            raise ValueError("the reference alternative's ASC prior must be 0.0")
        params: dict[str, tuple[str, int]] = {}
        for alt in self.alternatives:
            attr_ids = [t.id for t in alt.attributes]
            if len(set(attr_ids)) != len(attr_ids):
                raise ValueError(f"{alt.id}: attribute ids must be unique")
            for t in alt.attributes:
                shape = (t.coding, len(t.levels))
                if t.param in params and params[t.param] != shape:
                    raise ValueError(f"generic parameter {t.param}: coding/levels differ")
                if t.param in params and t.coding == "dummy":
                    first = self._attr_by_param(t.param)
                    if list(first.prior) != list(t.prior):  # type: ignore[arg-type]
                        raise ValueError(f"generic parameter {t.param}: priors differ")
                if t.param in params and t.coding == "linear":
                    first = self._attr_by_param(t.param)
                    if float(first.prior) != float(t.prior):  # type: ignore[arg-type]
                        raise ValueError(f"generic parameter {t.param}: priors differ")
                params.setdefault(t.param, shape)
        return self

    def _attr_by_param(self, param: str) -> Attribute:
        for alt in self.alternatives:
            for t in alt.attributes:
                if t.param == param:
                    return t
        raise KeyError(param)

    def columns(self) -> list[tuple[int, Attribute]]:
        """Design columns: one per (alternative index, attribute)."""
        return [(j, t) for j, alt in enumerate(self.alternatives) for t in alt.attributes]

    def parameters(self) -> list[str]:
        """Parameter names: ASCs of non-reference alternatives, then attribute parameters."""
        names = [f"asc_{a.id}" for a in self.alternatives if not a.reference]
        for _, t in self.columns():
            if t.coding == "linear":
                names.append(t.param)
            else:
                names.extend(f"{t.param}[{k}]" for k in range(1, len(t.levels)))
        return list(dict.fromkeys(names))


def load_design(path: Path) -> SurveyDesign:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return SurveyDesign.model_validate(data)


class _Model:
    """Precomputed coded values and priors for fast D-error evaluation."""

    def __init__(self, cfg: SurveyDesign) -> None:
        self.cfg = cfg
        self.n_alt = len(cfg.alternatives)
        self.params = cfg.parameters()
        pidx = {p: i for i, p in enumerate(self.params)}
        self.n_par = len(self.params)
        self.beta = np.zeros(self.n_par)
        self.asc_rows = np.zeros((self.n_alt, self.n_par))
        for j, alt in enumerate(cfg.alternatives):
            if not alt.reference:
                k = pidx[f"asc_{alt.id}"]
                self.asc_rows[j, k] = 1.0
                self.beta[k] = alt.asc.prior
        self.cols = cfg.columns()
        # coded[c][level] -> vector over parameters (only the alternative's own row is affected)
        self.coded: list[np.ndarray] = []
        self.n_levels: list[int] = []
        for _, t in self.cols:
            n = len(t.levels)
            mat = np.zeros((n, self.n_par))
            if t.coding == "linear":
                k = pidx[t.param]
                mat[:, k] = np.asarray(t.levels, dtype=float)
                self.beta[k] = float(t.prior)  # type: ignore[arg-type]
            else:
                for lvl in range(1, n):
                    k = pidx[f"{t.param}[{lvl}]"]
                    mat[lvl, k] = 1.0
                    self.beta[k] = float(t.prior[lvl - 1])  # type: ignore[index]
            self.coded.append(mat)
            self.n_levels.append(n)

    def task_x(self, row: np.ndarray) -> np.ndarray:
        x = self.asc_rows.copy()
        for c, (j, _) in enumerate(self.cols):
            x[j] += self.coded[c][row[c]]
        return x

    def task_info(self, row: np.ndarray) -> np.ndarray:
        x = self.task_x(row)
        v = x @ self.beta
        p = np.exp(v - v.max())
        p /= p.sum()
        xm = x - p @ x
        return (xm * p[:, None]).T @ xm

    def d_error_of_info(self, info: np.ndarray) -> float:
        sign, logdet = np.linalg.slogdet(info)
        if sign <= 0 or not np.isfinite(logdet):
            return float("inf")
        return float(np.exp(-logdet / self.n_par))

    def d_error(self, design: np.ndarray) -> float:
        return self.d_error_of_info(sum(self.task_info(r) for r in design))


def _balanced_start(model: _Model, n_tasks: int, rng: np.random.Generator) -> np.ndarray:
    design = np.empty((n_tasks, len(model.cols)), dtype=int)
    for c, n in enumerate(model.n_levels):
        reps = -(-n_tasks // n)
        design[:, c] = rng.permutation(np.tile(np.arange(n), reps)[:n_tasks])
    return design


def _coordinate_exchange(
    model: _Model, design: np.ndarray, max_sweeps: int
) -> tuple[np.ndarray, float]:
    task_infos = [model.task_info(r) for r in design]
    total = sum(task_infos)
    best = model.d_error_of_info(total)
    for _ in range(max_sweeps):
        improved = False
        for r in range(design.shape[0]):
            for c, n in enumerate(model.n_levels):
                current = design[r, c]
                for lvl in range(n):
                    if lvl == current:
                        continue
                    design[r, c] = lvl
                    new_info = model.task_info(design[r])
                    candidate = total - task_infos[r] + new_info
                    d = model.d_error_of_info(candidate)
                    if d < best - 1e-12:
                        best, current, improved = d, lvl, True
                        total, task_infos[r] = candidate, new_info
                    else:
                        design[r, c] = current
                design[r, c] = current
        if not improved:
            break
    return design, model.d_error(design)


def _assign_blocks(
    design: np.ndarray, n_blocks: int, rng: np.random.Generator, tries: int = 200
) -> np.ndarray:
    """Blocks of equal size; picks the random split with the least block-attribute correlation."""
    n = design.shape[0]
    base = np.repeat(np.arange(n_blocks), n // n_blocks)
    if n_blocks == 1:
        return base
    best, best_score = base, float("inf")
    for _ in range(tries):
        blocks = rng.permutation(base)
        score = 0.0
        for c in range(design.shape[1]):
            col = design[:, c].astype(float)
            if col.std() == 0:
                continue
            score += abs(np.corrcoef(blocks, col)[0, 1])
        if score < best_score:
            best, best_score = blocks, score
    return best


def _dominance_row(model: _Model, cfg: SurveyDesign) -> np.ndarray:
    """Rail at its best level on every attribute, all other alternatives at their worst."""
    target = "rail" if any(a.id == "rail" for a in cfg.alternatives) else cfg.alternatives[-1].id
    row = np.empty(len(model.cols), dtype=int)
    for c, (j, t) in enumerate(model.cols):
        u = t.utilities()
        row[c] = int(np.argmax(u)) if cfg.alternatives[j].id == target else int(np.argmin(u))
    return row


def generate(cfg: SurveyDesign, seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return the long-format choice-set rows and a summary (D-error, balance, blocks)."""
    rng = np.random.default_rng(seed)
    model = _Model(cfg)
    s = cfg.design
    best_design, best_d = None, float("inf")
    start_errors = []
    for _ in range(s.starts):
        start = _balanced_start(model, s.n_tasks, rng)
        design, d = _coordinate_exchange(model, start, s.max_sweeps)
        start_errors.append(d)
        if d < best_d:
            best_design, best_d = design.copy(), d
    assert best_design is not None
    if not np.isfinite(best_d):
        raise ValueError("design is not estimable (singular information matrix): add tasks")
    blocks = _assign_blocks(best_design, s.n_blocks, rng)
    dom = _dominance_row(model, cfg) if s.dominance_task else None

    rows: list[dict[str, Any]] = []
    for b in range(s.n_blocks):
        tasks = [best_design[i] for i in np.flatnonzero(blocks == b)]
        entries = [("design", t) for t in tasks]
        if dom is not None:
            entries.append(("dominance", dom))
        for task_no, (kind, task) in enumerate(entries, start=1):
            for c, (j, t) in enumerate(model.cols):
                lvl = int(task[c])
                rows.append(
                    {
                        "block": b + 1,
                        "task": task_no,
                        "task_type": kind,
                        "alternative": cfg.alternatives[j].id,
                        "attribute": t.id,
                        "level_index": lvl,
                        "level_value": _fmt(t.levels[lvl]),
                        "level_label_en": (t.level_labels_en or [None] * len(t.levels))[lvl] or "",
                        "level_label_ar": (t.level_labels_ar or [None] * len(t.levels))[lvl] or "",
                    }
                )
    s_est = s_estimate(model, best_design, s.n_blocks)
    balance = {
        f"{cfg.alternatives[j].id}.{t.id}": np.bincount(
            best_design[:, c], minlength=len(t.levels)
        ).tolist()
        for c, (j, t) in enumerate(model.cols)
    }
    summary = {
        "fielding": FIELDING_NOTE,
        "d_error": round(best_d, 8),
        "d_error_per_start": [round(x, 8) for x in start_errors],
        "n_parameters": model.n_par,
        "parameters": model.params,
        "n_tasks": s.n_tasks,
        "n_blocks": s.n_blocks,
        "tasks_per_respondent": s.n_tasks // s.n_blocks + (1 if s.dominance_task else 0),
        "level_balance": balance,
        "s_estimate": s_est,
    }
    return rows, summary


# Two-sided 5% critical value of the standard normal (method constant, not a real-world value).
_T_005 = 1.96


def s_estimate(model: _Model, design: np.ndarray, n_blocks: int) -> dict[str, Any]:
    """Sample-size lower bound per parameter (Ngene manual eq. 7.9; Bliemer and Rose).

    N_k = (t * se_k / beta_k)^2, with se_k from the MNL covariance of ONE replicate of the full
    design at the priors. A replicate is answered by `n_blocks` respondents, so respondents_k =
    N_k * n_blocks. A lower bound only: it assumes the priors are true and choices independent.
    """
    cov = np.linalg.inv(sum(model.task_info(r) for r in design))
    per: dict[str, float] = {}
    for k, name in enumerate(model.params):
        if model.beta[k] == 0.0:
            continue
        reps = (_T_005**2) * cov[k, k] / model.beta[k] ** 2
        per[name] = round(float(reps * n_blocks), 1)
    binding = max(per, key=per.__getitem__)
    return {
        "method": "Ngene eq. 7.9 lower bound, t = 1.96, MNL at the priors",
        "respondents_per_parameter": per,
        "binding_parameter": binding,
        "max_respondents": per[binding],
    }


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else repr(float(v))


FIELDS = [
    "block",
    "task",
    "task_type",
    "alternative",
    "attribute",
    "level_index",
    "level_value",
    "level_label_en",
    "level_label_ar",
]


def write_csv(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


app = typer.Typer(add_completion=False, help="Survey design generator (design only, rule 7).")


@app.command()
def validate(config: Path = typer.Option(..., "--config", exists=True)) -> None:
    """Validate a design YAML (schema, priors, citations)."""
    cfg = load_design(config)
    typer.echo(
        f"OK {config}: {len(cfg.alternatives)} alternatives, "
        f"{len(cfg.columns())} attribute columns, {len(cfg.parameters())} parameters"
    )


@app.command()
def design(
    config: Path = typer.Option(..., "--config", exists=True),
    out: Path = typer.Option(..., "--out"),
    seed: int = seed_option(),
) -> None:
    """Generate the D-efficient choice sets (CSV) and `<out>.meta.json`."""
    raw = yaml.safe_load(config.read_text(encoding="utf-8"))
    cfg = SurveyDesign.model_validate(raw)
    rows, summary = generate(cfg, seed)
    write_csv(rows, out)
    meta = build_meta(seed, raw, extra={"config": str(config), "design": summary})
    meta.pop("created_utc", None)  # keep the committed meta byte-stable across reruns
    meta_path = out.with_suffix(out.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    typer.echo(
        f"{FIELDING_NOTE}: wrote {out} ({len(rows)} rows; {summary['n_blocks']} blocks × "
        f"{summary['tasks_per_respondent']} tasks; D-error {summary['d_error']:.6g}); "
        f"meta {meta_path}"
    )


if __name__ == "__main__":
    app()
