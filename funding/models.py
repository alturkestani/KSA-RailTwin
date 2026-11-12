"""Delivery and funding options register (W6, R1d): schema and validation for
`cities/ksa/funding/models.yaml` (`ppp-structuring` skill). An options landscape, not a
recommendation (rule 9).

    uv run python -m funding.models validate [--path cities/ksa/funding/models.yaml]
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from common import REPO_ROOT
from funding.sources import SOURCE_ID, SOURCES_DIR, known_source_ids, unknown_ids

DEFAULT_PATH = REPO_ROOT / "cities" / "ksa" / "funding" / "models.yaml"

RISK_KEYS = [
    "construction",
    "demand",
    "revenue",
    "operations",
    "financing",
    "land",
    "regulatory_force_majeure",
]
REQUIRED_IDS = [
    "fully_public_budget",
    "fully_public_pif",
    "fully_public_sar",
    "public_with_private_om",
    "ppp_dbfom_availability",
    "ppp_dbfom_demand_risk",
    "ppp_dbfm",
    "vertical_separation_infra_public_ops_private",
    "integrated_concession",
    "private_concession",
    "lvc_station_area_development",
    "lvc_betterment_levy",
    "lvc_tax_increment",
]
Allocation = Literal["public", "private", "shared", "varies"]
Family = Literal["public", "public_private", "ppp", "private", "land_value_capture", "hybrid"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Term(_Strict):
    low: int | None = None
    high: int | None = None
    source: str | None = None
    note: str = ""

    @model_validator(mode="after")
    def _rules(self) -> Term:
        if (self.low is not None or self.high is not None) and not self.source:
            raise ValueError("a term range needs a `source:`")
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError("term low > high")
        if self.low is None and self.high is None and not self.note:
            raise ValueError("an empty term needs a `note:` (e.g. 'varies; no source')")
        return self


class Option(_Strict):
    id: str
    name: str
    family: Family
    definition: str = Field(min_length=20)
    who_pays: str
    who_owns: str
    who_operates: str
    typical_term_years: Term
    risk_allocation: dict[str, Allocation]
    fiscal_treatment: str
    when_it_fits: str
    examples: list[str] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)
    mix: list[str] | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> Option:
        if sorted(self.risk_allocation) != sorted(RISK_KEYS):
            missing = set(RISK_KEYS) ^ set(self.risk_allocation)
            raise ValueError(f"{self.id}: risk_allocation keys differ: {sorted(missing)}")
        if self.family == "hybrid":
            if not self.id.startswith("hybrid_"):
                raise ValueError(f"{self.id}: a hybrid option id starts with 'hybrid_'")
            if not self.mix or len(self.mix) < 2:
                raise ValueError(f"{self.id}: a hybrid lists its component options in `mix:`")
        elif self.mix:
            raise ValueError(f"{self.id}: `mix:` is only for family: hybrid")
        for s in [*self.examples, *self.sources, self.typical_term_years.source]:
            if s is not None and not SOURCE_ID.match(s):
                raise ValueError(f"{self.id}: '{s}' is not an S-id")
        return self

    def cited(self) -> list[str]:
        ids = [*self.examples, *self.sources]
        if self.typical_term_years.source:
            ids.append(self.typical_term_years.source)
        return ids


class ModelsRegister(_Strict):
    version: str
    label: str
    risk_keys: list[str]
    options: list[Option]

    @model_validator(mode="after")
    def _rules(self) -> ModelsRegister:
        if self.risk_keys != RISK_KEYS:
            raise ValueError(f"risk_keys must be {RISK_KEYS}")
        ids = [o.id for o in self.options]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"duplicate option ids: {dupes}")
        missing = [i for i in REQUIRED_IDS if i not in ids]
        if missing:
            raise ValueError(f"missing required options: {missing}")
        if not any(o.family == "hybrid" for o in self.options):
            raise ValueError("at least one hybrid_<name> option is required")
        for o in self.options:
            for m in o.mix or []:
                if m not in ids or m == o.id:
                    raise ValueError(f"{o.id}: mix component '{m}' is not another option id")
        return self


def load_models(path: Path = DEFAULT_PATH) -> ModelsRegister:
    return ModelsRegister.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def check_sources(reg: ModelsRegister, sources_dir: Path = SOURCES_DIR) -> list[str]:
    known = known_source_ids(sources_dir)
    return unknown_ids([s for o in reg.options for s in o.cited()], known)


app = typer.Typer(
    add_completion=False, help="Delivery and funding options register (W6).", no_args_is_help=True
)


@app.callback()
def _main() -> None:
    """Keep `validate` an explicit subcommand."""


@app.command()
def validate(
    path: Path = typer.Option(DEFAULT_PATH, "--path", exists=True),
    sources_dir: Path = typer.Option(SOURCES_DIR, "--sources-dir"),
) -> None:
    """Schema, required options, hybrid mixes and every cited S-id resolving to a source row."""
    reg = load_models(path)
    missing = check_sources(reg, sources_dir)
    if missing:
        typer.echo(f"FAIL: S-ids with no row in {sources_dir}/*.csv: {', '.join(missing)}")
        raise typer.Exit(1)
    families = sorted({o.family for o in reg.options})
    typer.echo(f"OK {path}: {len(reg.options)} options ({', '.join(families)}); sources resolve")


if __name__ == "__main__":
    app()
