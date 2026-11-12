"""REGION_MAKKAH register (R2): Parquet and CSV validate against RegionRow and the header."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from screening.region_sweep import validate_file

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "cities/ksa/regions/makkah.parquet"


@pytest.mark.skipif(not REGISTER.exists(), reason="register not built")
def test_register_validates_strictly() -> None:
    errors, warnings, facts = validate_file(REGISTER)
    assert errors == []
    assert warnings == []
    assert facts["governorates_gastat"] == "17"
    assert facts["governorates_listed"] == "17"
    assert facts["governorates_in_rows"] == 17


@pytest.mark.skipif(not REGISTER.exists(), reason="register not built")
def test_every_official_city_of_10k_is_a_row_and_no_grid_row_passes_unverified() -> None:
    df = pd.read_parquet(REGISTER)
    official_10k = df[(df["pop_type"] == "official") & (df["population"] >= 10000)]
    assert len(official_10k) == 15
    assert df.loc[df["pop_type"] == "grid", "tag_10k"].sum() == 0


@pytest.mark.skipif(not REGISTER.exists(), reason="register not built")
def test_csv_mirror_agrees_with_parquet() -> None:
    df = pd.read_parquet(REGISTER)
    csv = pd.read_csv(REGISTER.with_suffix(".csv"))
    assert list(csv["name_en"]) == list(df["name_en"])
