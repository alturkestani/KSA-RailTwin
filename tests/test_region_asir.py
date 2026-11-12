"""Asir region register (REGION_ASIR): reconciliation and gate rules on the committed register."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from common.schemas import GRID_UNCORROBORATED, RegionRow, load_region_register

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "cities/ksa/regions/asir.parquet"


def test_governorate_count_reconciles_to_gastat() -> None:
    meta = pq.read_schema(REG).metadata
    assert meta[b"governorates_gastat"] == meta[b"governorates_listed"] == b"18"
    rows = load_region_register(REG)
    centres = [r for r in rows if r.is_governorate_centre]
    assert len(centres) == len({r.governorate for r in centres}) == 18


def test_grid_only_rows_at_10k_are_held_out() -> None:
    df = pd.read_parquet(REG)
    grid = df[(df.pop_type == "grid") & (df.population >= 10_000)]
    assert len(grid) == 3
    assert not grid.tag_10k.any()
    assert grid.exclusion_reason.str.contains(GRID_UNCORROBORATED, regex=False).all()


def test_every_official_population_has_a_source_and_csv_mirrors_parquet() -> None:
    df = pd.read_parquet(REG)
    pops = df[df.population.notna()]
    assert pops.pop_source.notna().all() and pops.pop_type.notna().all()
    csv = pd.read_csv(REG.with_suffix(".csv"))
    assert len(csv) == len(df)
    assert sorted(csv.osm_id.astype(int)) == sorted(df.osm_id.astype(int))
    for r in load_region_register(REG):
        RegionRow.model_validate(r.model_dump())
