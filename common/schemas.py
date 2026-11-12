"""Pydantic schemas for the registers and YAML files, written from the skills' field lists.

- `LineSpec`     line YAML (`.claude/skills/line-yaml`)
- `RegionRow`    region register row (`.claude/skills/region-sweep`)
- `CostItem`     cost register item (`.claude/skills/cost-register`)
- `UpliftSpec`   reference-class uplift (`.claude/skills/reference-class-forecasting`; R1c)
- `CbaCase`      CBA case YAML (`.claude/skills/cba-appraisal`)
- `Scenario`     scenario YAML (`.claude/skills/scenario-yaml`)
- `ZoneProps`    zone GeoJSON feature properties
- `SourceRow`    data manifest row (`docs/versioning.md`)
- `Param`        a real-world parameter: rejected unless it carries `source` or an assumption
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

REGIONS = (
    "riyadh",
    "makkah",
    "madinah",
    "eastern",
    "qassim",
    "asir",
    "tabuk",
    "hail",
    "northern_borders",
    "jazan",
    "najran",
    "al_baha",
    "al_jouf",
)
Region = Literal[
    "riyadh",
    "makkah",
    "madinah",
    "eastern",
    "qassim",
    "asir",
    "tabuk",
    "hail",
    "northern_borders",
    "jazan",
    "najran",
    "al_baha",
    "al_jouf",
]
Layer = Literal["existing", "committed", "hypothetical", "historical"]
Terrain = Literal["flat_desert", "dunes", "sabkha", "escarpment_mountain", "coastal", "mixed"]
LABEL_TEXT = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
# Registered in docs/assumptions.md (approval pending CP1 for the thresholds):
TAG_10K = 10_000  # A-screen-001: inclusion threshold (PROJECT.md W2)
TAG_5K = 5_000  # A-screen-002: sensitivity threshold (PROJECT.md W2)
TAG_50K = 50_000  # A-screen-014: pilot sampling cut-off, not a screening threshold
KSA_LAT = (16.0, 33.0)  # A-data-001: coordinate sanity box (catches swapped lat/lon)
KSA_LON = (34.0, 56.0)  # A-data-001


# CP2 P1a (Tariq, 31 Oct 2026; additive). Population basis precedence official > derived
# corroborated > grid (A-screen-031). A grid-only figure passes the >= 10k test only if a second
# independent method agrees within the band (A-screen-032), using an allowed method (A-screen-033).
CORROBORATION_BAND = 0.30  # A-screen-032: abs(grid - other) / grid <= 0.30
CORROBORATION_TOL = 1e-12  # float tolerance so a ratio of exactly 0.30 passes (not a parameter)
CORROBORATION_METHODS = ("buildings_x_occupancy", "ghs_pop_sum", "viirs_calibrated")  # A-screen-033
# CP2_PREP item 1 addendum (additive): Census 2010 city grown by governorate ratio (A-screen-035)
CORROBORATION_METHODS = (*CORROBORATION_METHODS, "gastat2010_city_growth")
GRID_UNCORROBORATED = "grid-only population, uncorroborated"


def corroborates(grid: float | None, other: float | None, band: float = CORROBORATION_BAND) -> bool:
    """True if `other` lies within `band` of the grid figure: abs(grid - other) / grid <= band."""
    if grid is None or other is None or grid != grid or other != other or grid <= 0:
        return False
    return abs(grid - other) / grid <= band + CORROBORATION_TOL


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


# --------------------------------------------------------------------------- parameters
class Param(Strict):
    """A number with real-world meaning: needs `source` or `assumption`/`assumption_id`."""

    value: float | int | str | bool | None
    source: str | None = None
    assumption: str | None = None
    assumption_id: str | None = None

    @model_validator(mode="after")
    def _sourced(self) -> Param:
        if not (self.source or self.assumption or self.assumption_id):
            raise ValueError("parameter needs `source:` or `assumption:`/`assumption_id:`")
        return self


# --------------------------------------------------------------------------- lines
class Station(Strict):
    id: str
    name_en: str
    name_ar: str
    km_post: float = Field(ge=0)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    class_: Literal["terminal", "major", "intermediate", "airport", "halt", "planned"] = Field(
        alias="class"
    )
    source: str


class Service(Strict):
    id: str
    stops: Literal["all"] | list[str]
    headway_min: float = Field(gt=0)
    span: str | None = None
    sampled: dt.date
    source: str


class FareBand(Strict):
    low: float = Field(ge=0)
    high: float = Field(ge=0)

    @model_validator(mode="after")
    def _ordered(self) -> FareBand:
        if self.low > self.high:
            raise ValueError("fare low > high")
        return self


class Fare(Strict):
    from_: str = Field(alias="from")
    to: str
    economy: FareBand | None = None
    business: FareBand | None = None
    sampled: dt.date
    source: str


class Observed(Strict):
    pair: list[str] = Field(min_length=2, max_length=2)
    minutes: float = Field(gt=0)
    implied_avg_kmh: float | None = None
    source: str


class LineSpec(Strict):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$|^S\d+-[a-z0-9_-]+$")
    name_en: str
    name_ar: str
    layer: Layer
    operator: str | None = None
    status: Literal[
        "in_service",
        "announced",
        "design",
        "procurement",
        "construction",
        "abandoned",
        "generated",
    ]
    source: str
    source_date: dt.date | None = None
    accessed: dt.date | None = None
    # CP2 P4a (additive): `freight` for lines a cited source calls freight-only.
    line_type: Literal[
        "hsr", "conventional_passenger", "mixed", "commuter", "metro", "upgrade", "freight"
    ]
    design_speed_kmh: float | None = Field(default=None, gt=0)
    track: Literal["single", "double", "multiple"] | None = None
    electrified: bool | None = None
    gauge_mm: int | None = None
    length_km: float | None = Field(default=None, gt=0)
    alignment: str | None = None
    stations: list[Station] = Field(min_length=2)
    services: list[Service] = []
    fares_sar: list[Fare] = []
    running_time_model: dict[str, Param] = {}
    observed_performance: list[Observed] = []
    generated_from: str | None = None
    rules_hash: str | None = None
    uncertainty_km: float | None = None
    fixture: bool = False
    notes: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> LineSpec:
        if self.layer == "existing" and (not self.operator or self.status != "in_service"):
            raise ValueError("layer existing requires operator and status in_service")
        if self.layer == "committed" and not self.source_date:
            raise ValueError("layer committed requires source_date")
        if self.layer == "hypothetical" and not (self.generated_from and self.rules_hash):
            raise ValueError("layer hypothetical requires generated_from and rules_hash")
        if self.layer != "existing" and self.status == "in_service":
            raise ValueError("only layer existing may have status in_service (rule 5)")
        ids = [s.id for s in self.stations]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate station ids")
        kms = [s.km_post for s in self.stations]
        if any(b <= a for a, b in zip(kms, kms[1:], strict=False)):
            raise ValueError("station km_post values must increase strictly")
        if self.length_km is not None and kms[-1] > self.length_km + 2:
            raise ValueError("last km_post exceeds length_km by more than 2 km")
        known = set(ids)
        for svc in self.services:
            if isinstance(svc.stops, list) and not set(svc.stops) <= known:
                raise ValueError(f"service {svc.id} stops at unknown stations")
        return self


# --------------------------------------------------------------------------- region register
EconomicRoleName = Literal[
    "port",
    "industrial_city",
    "mining",
    "tourism",
    "heritage",
    "hajj_umrah",
    "airport",
    "university",
    "giga_project",
    "agriculture",
    "border_crossing",
    "military",
    "administrative",
    "energy",  # refineries, oil/gas processing, export terminals (Q21; CP1_PREP A-screen-010)
]


class EconomicRole(Strict):
    role: EconomicRoleName
    source: str


class RegionRow(Strict):
    name_ar: str
    name_en: str
    region: Region
    governorate: str
    governorate_ar: str
    is_governorate_centre: bool
    osm_id: int | None = None
    osm_type: Literal["node", "way", "relation"] | None = None  # node/way/relation ids overlap
    lat: float = Field(ge=KSA_LAT[0], le=KSA_LAT[1])
    lon: float = Field(ge=KSA_LON[0], le=KSA_LON[1])
    population: int | None = Field(default=None, ge=0)
    pop_source: str | None = None
    pop_year: int | None = None
    pop_type: Literal["official", "derived", "grid"] | None = None
    # Coordinator decision 30 Oct 2026 (PILOT_MERGE): a GASTAT figure relayed by an aggregator is
    # pop_type official + pop_source_status secondary + primary_to_find; an aggregator's own
    # estimate is pop_type derived + pop_source_status secondary.
    pop_source_status: Literal["verified", "secondary", "unverified"] | None = None
    primary_to_find: str | None = None
    # CP2 P1a (additive): second independent method for a grid-only figure (A-screen-033) and its
    # value; gates tag_10k for pop_type grid (A-screen-031/032).
    pop_corroboration: (
        Literal[
            "buildings_x_occupancy", "ghs_pop_sum", "viirs_calibrated", "gastat2010_city_growth"
        ]
        | None
    ) = None
    pop_corroboration_value: float | None = Field(default=None, ge=0)
    tag_10k: bool
    tag_5k: bool
    dist_existing_km: float | None = None
    road_min_existing: float | None = None
    nearest_existing: str | None = None
    dist_committed_km: float | None = None
    road_min_committed: float | None = None
    nearest_committed: str | None = None
    nearest_committed_station: str | None = None
    dist_metro_km: float | None = None
    road_min_metro: float | None = None
    nearest_metro: str | None = None
    economic_roles: list[EconomicRole] = []
    terrain_class: Terrain | None = None
    screened: bool
    exclusion_reason: str | None = None
    sources: list[str] = []
    fixture: bool = False
    # Pilot columns (coordinator decision 30 Oct 2026; optional, also used by the R2 sweep):
    threshold_50k: bool | None = None
    pilot_sample: bool | None = None
    nearest_metro_tier: Literal[1, 2, 3] | None = None  # A-screen-013
    road_min_method: str | None = None
    dist_method: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> RegionRow:
        if self.population is not None:
            if not self.pop_source or not self.pop_type or not self.pop_year:
                raise ValueError("population requires pop_source, pop_type and pop_year")
            expect_10k = self.population >= TAG_10K
            if self.pop_type == "grid":  # CP2 P1a: corroboration gate (A-screen-031/032)
                expect_10k = expect_10k and corroborates(
                    self.population, self.pop_corroboration_value
                )
            if self.tag_10k != expect_10k or self.tag_5k != (self.population >= TAG_5K):
                raise ValueError("tag_10k / tag_5k disagree with population")
        elif self.pop_type is not None or self.tag_10k or self.tag_5k:
            raise ValueError("no population: pop_type must be null and tags false")
        if not self.screened and not self.exclusion_reason:
            raise ValueError("screened = false requires exclusion_reason")
        if self.threshold_50k is not None and self.threshold_50k != (
            self.population is not None and self.population >= TAG_50K
        ):
            raise ValueError("threshold_50k disagrees with population")
        if self.pop_source_status is not None and self.population is None:
            raise ValueError("pop_source_status needs a population")
        if (
            self.pop_type == "official"
            and self.pop_source_status == "secondary"
            and not self.primary_to_find
        ):
            raise ValueError("official figure from a secondary source needs primary_to_find")
        if self.pilot_sample and not self.notes:
            raise ValueError("pilot_sample = true requires the sampling reason in notes")
        # CP2 P1a (additive)
        if (self.pop_corroboration is None) != (self.pop_corroboration_value is None):
            raise ValueError("pop_corroboration and pop_corroboration_value go together")
        if self.pop_corroboration is not None and self.pop_type != "grid":
            raise ValueError("pop_corroboration applies to pop_type grid only (A-screen-031)")
        if self.pop_type == "grid":
            if self.pop_source_status != "unverified":
                raise ValueError("pop_type grid requires pop_source_status unverified (P1a)")
            gated = (
                self.population is not None
                and self.population >= TAG_10K
                and not corroborates(self.population, self.pop_corroboration_value)
            )
            if gated and GRID_UNCORROBORATED not in (self.exclusion_reason or ""):
                raise ValueError(f"grid row >= 10k without corroboration: {GRID_UNCORROBORATED!r}")
        return self


# --------------------------------------------------------------------------- cost register
class CostItem(Strict):
    id: str = Field(pattern=r"^C-[a-z0-9-]+$")
    item: str
    category: Literal[
        "line_type",
        "terrain",
        "structure",
        "system",
        "station",
        "depot",
        "rolling_stock",
        "signalling",
        "electrification",
        "power",
        "land",
        "utilities",
        "design_pm",
        "contingency",
        "opex",
        "renewal",
        "financing",
        "programme",  # R1c (additive): whole-programme top-down figures (KSA data points)
    ]
    line_type: Literal["hsr", "conventional_passenger", "mixed", "commuter", "upgrade", "n/a"]
    terrain: Literal["flat_desert", "dunes", "sabkha", "escarpment_mountain", "coastal", "n/a"]
    unit: Literal[
        "SAR_m_per_km",
        "SAR_m_per_station",
        "SAR_m_per_trainset",
        "SAR_m_per_yr",
        "SAR_per_train_km",
        "pct_of_capex",
        "pct_per_yr",
        "SAR_m_lump",
        # R1c (additive). The `SAR` token names the base currency; until `costs.register
        # normalise` runs, values are millions (or units) of `currency`, at `price_year`.
        "SAR_m_per_km_per_yr",
        "SAR_m_per_unit",
        "SAR_per_kwh",
        "kwh_per_train_km",
        "SAR_per_fte_yr",
        "fte_per_km",
        "SAR_per_m2",
        "pct",
        "years",
    ]
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    price_year: int = Field(ge=1950, le=2100)
    low: float | None = None
    central: float | None = None
    high: float | None = None
    source: str
    status: Literal["sourced", "derived", "assumed", "unknown"]
    derivation: str | None = None
    assumption_id: str | None = None
    notes: str | None = None
    # R1c (additive, all optional)
    approach: Literal["top_down", "bottom_up", "parameter"] | None = None
    scope: str | None = None
    layer: Literal["existing", "committed", "hypothetical", "n/a"] | None = None
    extra_sources: list[str] = []
    price_year_basis: Literal["stated", "award_year", "publication_year", "assumed"] | None = None
    searched: str | None = None  # where an `unknown` item was searched

    @model_validator(mode="after")
    def _rules(self) -> CostItem:
        vals = (self.low, self.central, self.high)
        if self.status == "unknown":
            if any(v is not None for v in vals):
                raise ValueError("status unknown: leave low/central/high null (never guess)")
            return self
        if any(v is None for v in vals):
            raise ValueError("low, central and high are required unless status is unknown")
        if not self.low <= self.central <= self.high:  # type: ignore[operator]
            raise ValueError("expected low <= central <= high")
        if self.status == "derived" and not self.derivation:
            raise ValueError("status derived requires derivation (name the index used)")
        if self.status == "sourced" and self.source in ("assumed", "fixture", ""):
            raise ValueError("status sourced requires a source id")
        return self


def load_cost_register(path: Path) -> list[CostItem]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    out = [CostItem.model_validate(i) for i in items]
    ids = [i.id for i in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate cost item ids")
    return out


# ------------------------------------------------------------------ uplifts (R1c, additive)
class UpliftSpec(Strict):
    """One reference-class uplift (`reference-class-forecasting` skill), in
    `cities/ksa/costs/uplifts.yaml`.

    Ratios are outcome / base estimate (capex, schedule) or actual / forecast (ridership).
    """

    id: str = Field(pattern=r"^U-[a-z0-9-]+$")
    applies_to: Literal["capex", "schedule", "ridership"]
    line_type: Literal[
        "rail", "hsr", "conventional_passenger", "mixed", "commuter", "upgrade", "all"
    ]
    stage: Literal["strategic", "outline_business_case", "full_business_case", "n/a"]
    distribution: Literal["empirical", "lognormal", "normal", "triangular"]
    params: dict[str, Any]
    source: str
    extra_sources: list[str] = []
    status: Literal["sourced", "derived", "assumed"]
    derivation: str | None = None
    assumption_id: str
    role: Literal["default", "sensitivity"] = "default"  # only `default` entries are auto-selected
    notes: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> UpliftSpec:
        if self.status in ("sourced", "derived") and not self.source.startswith("S-"):
            raise ValueError("sourced/derived uplift needs an S- source id")
        if self.status == "derived" and not self.derivation:
            raise ValueError("derived uplift needs derivation")
        p = self.params
        need = {
            "empirical": ("percentiles",),
            "lognormal": ("median_ratio",),
            "normal": ("mean_ratio", "sd", "floor"),
            "triangular": ("low", "mode", "high"),
        }[self.distribution]
        missing = [k for k in need if k not in p]
        if missing:
            raise ValueError(f"{self.distribution} uplift needs params {missing}")
        if self.distribution == "lognormal" and not ("p80_ratio" in p or "sigma" in p):
            raise ValueError("lognormal uplift needs p80_ratio or sigma")
        if self.distribution == "empirical" and len(p["percentiles"]) < 2:
            raise ValueError("empirical uplift needs at least two percentiles")
        return self


def load_uplifts(path: Path) -> list[UpliftSpec]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = data["uplifts"] if isinstance(data, dict) else data
    out = [UpliftSpec.model_validate(i) for i in items]
    ids = [u.id for u in out]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate uplift ids")
    return out


# --------------------------------------------------------------------------- CBA case
class DiscountRate(Strict):
    rate: float = Field(ge=0, le=0.5)
    declining: list[tuple[int, int, float]] | None = None
    source: str | None = None
    assumption_id: str | None = None

    @model_validator(mode="after")
    def _sourced(self) -> DiscountRate:
        if not (self.source or self.assumption_id):
            raise ValueError("discount rate needs source or assumption_id")
        if self.declining:
            prev_end = -1
            for start, end, _ in self.declining:
                if start != prev_end + 1 or end < start:
                    raise ValueError("declining schedule must be contiguous year bands")
                prev_end = end
        return self


class DiscountRates(Strict):
    social: DiscountRate
    commercial: DiscountRate
    sensitivity: list[float] = []


class ResidualValue(Strict):
    method: str
    asset_lives: dict[str, int]
    source: str | None = None
    assumption_id: str | None = None


class MonteCarlo(Strict):
    draws: int = Field(ge=1)
    seed: int = Field(ge=0)
    inputs: list[str] = Field(min_length=1)


class CbaCase(Strict):
    id: str = Field(pattern=r"^CBA-")
    scenario: str
    baseline: str
    horizon_years: list[int] = Field(min_length=1)
    residual_value: ResidualValue
    price_year: int
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    discount_rates: DiscountRates
    costs: dict[str, str]
    benefits: dict[str, dict[str, Any]]
    monte_carlo: MonteCarlo
    fixture: bool = False
    # R5 (additive): what the case appraises and which runs it reads
    family: str | None = None
    candidate: str | None = None  # corridor YAML added to the baseline line set (None: S1 vs S0)
    population_scenarios: list[str] = []
    cost_run: str | None = None
    cost_spec: str | None = None
    cost_costing: str | None = None
    demand_runs: str | None = None
    rate_cases: list[str] = []

    @model_validator(mode="after")
    def _rules(self) -> CbaCase:
        if self.baseline == self.scenario:
            raise ValueError("a scenario cannot be its own matched baseline (rule 6)")
        if any(h <= 0 for h in self.horizon_years):
            raise ValueError("horizons must be positive")
        wei = self.benefits.get("wider_economic_impacts", {})
        if wei and not wei.get("report_separately", False):
            raise ValueError("wider impacts must be reported separately (no double counting)")
        luv = self.benefits.get("land_value_uplift", {})
        if luv and not luv.get("capture_only_if_not_counted_in_time_savings", False):
            raise ValueError("land value uplift is a capture potential only (no double counting)")
        return self


# --------------------------------------------------------------------------- scenarios
class ScenarioLines(Strict):
    include: list[str] = []


class Scenario(BaseModel):
    """Lenient on optional blocks (they fill in from R3 on); strict on identity and layers."""

    model_config = ConfigDict(extra="allow")
    id: str = Field(pattern=r"^S\d")
    kind: str
    title: str
    layers: list[Literal["existing", "committed", "hypothetical"]] = Field(min_length=1)
    baseline: str | None
    lines: ScenarioLines
    candidates: list[str] = []
    seed: int = Field(ge=0)
    labels: list[str]
    source: str

    @model_validator(mode="after")
    def _rules(self) -> Scenario:
        if self.id == "S0":
            if self.baseline is not None or self.layers != ["existing"]:
                raise ValueError("S0 is the baseline: baseline null, layers [existing]")
        elif not self.baseline:
            raise ValueError("every scenario except S0 names its matched baseline (rule 6)")
        if self.id == "S1" and "hypothetical" in self.layers:
            raise ValueError("S1 may not include hypothetical lines")
        if LABEL_TEXT not in self.labels:
            raise ValueError("scenario must carry the synthetic/uncalibrated label")
        return self


# --------------------------------------------------------------------------- zones, manifest
class ZoneProps(Strict):
    zone_id: str
    name_en: str
    name_ar: str | None = None
    region: Region | None = None
    population: int = Field(ge=0)
    pop_source: str
    fixture: bool

    @field_validator("pop_source")
    @classmethod
    def _src(cls, v: str) -> str:
        if not v:
            raise ValueError("pop_source required")
        return v


class SourceRow(Strict):
    id: str
    name: str
    publisher: str
    url: str
    edition: str
    licence: str
    accessed: dt.date
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    bytes: int | None = Field(default=None, ge=0)
    local_path: str | None = None
    used_in: list[str] = []
    notes: str | None = ""

    @field_validator("local_path")
    @classmethod
    def _relative(cls, v: str | None) -> str | None:
        if v and (v.startswith("/") or v.startswith("~")):
            raise ValueError("local_path must be relative to the repository")
        return v


def _plain(v: Any) -> Any:
    """Parquet/pandas cell -> plain Python (arrays to lists, NA to None)."""
    if hasattr(v, "tolist") and not isinstance(v, str):
        v = v.tolist()
    if isinstance(v, list):
        return [_plain(x) for x in v]
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    try:
        import pandas as pd

        if v is pd.NA or (isinstance(v, float) and v != v):
            return None
    except ImportError:  # pragma: no cover
        pass
    return v


def load_region_register(path: Path) -> list[RegionRow]:
    import pandas as pd

    df = pd.read_parquet(path)
    return [
        RegionRow.model_validate({k: _plain(v) for k, v in rec.items()})
        for rec in df.to_dict(orient="records")
    ]
