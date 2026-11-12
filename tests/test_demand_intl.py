"""R4 international-visitor segment: the drop-in airport split table and the GASTAT readers."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from common import REPO_ROOT
from demand import intl


def test_new_year_row_is_picked_up(tmp_path: Path) -> None:
    dst = tmp_path / intl.SPLIT
    dst.parent.mkdir(parents=True)
    shutil.copy(REPO_ROOT / intl.SPLIT, dst)
    base = intl.airport_split(2025, tmp_path)
    assert base["year_row"] == "default" and base["status"] == "assumed"
    doc = yaml.safe_load(dst.read_text(encoding="utf-8"))
    doc["years"] = {
        2024: {"status": "sourced", "source": "test row", "shares": {"JED": 0.5, "MED": 0.5}}
    }
    dst.write_text(yaml.safe_dump(doc), encoding="utf-8")
    got = intl.airport_split(2025, tmp_path)
    assert got["year_row"] == 2024 and got["shares"] == {"JED": 0.5, "MED": 0.5}
    assert intl.airport_split(2023, tmp_path)["year_row"] == "default"


def test_default_shares_sum_to_one() -> None:
    s = intl.airport_split(2025, REPO_ROOT)["shares"]
    assert abs(sum(s.values()) - 1.0) < 1e-3
    lo_hi = intl.airport_split(2025, REPO_ROOT)["range"]
    assert all(lo_hi[k][0] <= v + 1e-9 <= lo_hi[k][1] + 2e-9 for k, v in s.items())


def test_port_table_total_matches_bulletin() -> None:
    t = intl.port_table("1440", REPO_ROOT)
    tot = t[t.port.str.lower() == "total"].total.iloc[0]
    assert tot == 7457663  # 1440 AH foreign Umrah performers, GASTAT Table 3
