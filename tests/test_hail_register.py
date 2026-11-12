"""REGION_HAIL register: the built register validates and keeps its reconciled counts (r2-hail)."""

from __future__ import annotations

import pandas as pd
import pyarrow.parquet as pq

from common import REPO_ROOT
from screening import region_sweep
from screening.sweeps.hail import build_register

REG = REPO_ROOT / "cities/ksa/regions/hail.parquet"


def test_hail_register_validates_strict() -> None:
    errors, warnings, facts = region_sweep.validate_file(REG)
    assert errors == []
    assert warnings == []
    assert facts["governorates_in_rows"] == 9


def test_hail_header_reconciles_to_nine_governorates() -> None:
    md = pq.read_schema(REG).metadata or {}
    assert md[b"governorates_gastat"] == b"9"
    assert md[b"governorates_listed"] == b"9"


def test_hail_governorates_sum_to_region_total() -> None:
    # S-hail-009: nine primary governorate rows = Ḥā'il region total (S-hail-001)
    names = [v[1] for v in build_register.CENTRES.values()]
    primary = build_register._primary_governorates()
    assert sum(primary[n] for n in names) == build_register.REGION_TOTAL_S_HAIL_001


def test_hail_grid_rows_are_unverified_and_below_the_10k_test() -> None:
    # no grid row in Ḥā'il reaches 10,000, so none needs a second method (A-screen-031)
    df = pd.read_parquet(REG)
    grid = df[df["pop_type"] == "grid"]
    assert (grid["pop_source_status"] == "unverified").all()
    assert not grid["tag_10k"].any()


def test_hail_primary_figures_match_the_gastat_city_table() -> None:
    df = pd.read_parquet(REG).set_index("name_en")
    assert df.loc["Ha'il", "population"] == 448_623
    assert df.loc["Baqa", "population"] == 19_659
    assert df.loc["Turubah", "population"] == 8_590  # Ḥā'il Turubah, not the Makkah 28,279


def test_hail_csv_mirror_matches_parquet() -> None:
    df = pd.read_parquet(REG)
    c = pd.read_csv(REG.with_suffix(".csv"))
    assert list(c["name_en"]) == list(df["name_en"])


def test_hail_relayed_figures_take_precedence_over_grid_and_osm() -> None:
    # S-hail-001 relayed figures (checked live 31 Oct 2026) are below 5,000 and beat grid/OSM
    df = pd.read_parquet(REG)
    assert "Al Khuttah" not in set(df["name_en"])
    assert "Al Hulayfah Assofla" not in set(df["name_en"])
    assert "Al Qa`id" not in set(df["name_en"])
    assert int(df["tag_5k"].sum()) == 15
    assert len(df) == 17
