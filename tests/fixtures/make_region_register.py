"""Rebuild the mini-region register fixture: `uv run python tests/fixtures/make_region_register.py`.

Invented test data (tests/fixtures/README.md); not real towns or populations.
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))

from common.schemas import RegionRow  # noqa: E402


def rows() -> list[dict]:
    base = {
        "region": "makkah",
        "governorate_ar": "محافظة اختبار",
        "osm_id": None,
        "pop_year": 2022,
        "dist_existing_km": None,
        "road_min_existing": None,
        "nearest_existing": None,
        "dist_committed_km": None,
        "road_min_committed": None,
        "nearest_committed": None,
        "nearest_committed_station": None,
        "dist_metro_km": None,
        "road_min_metro": None,
        "nearest_metro": None,
        "terrain_class": "flat_desert",
        "exclusion_reason": None,
        "sources": ["fixture"],
        "fixture": True,
    }
    towns = [
        (
            "بلدة اختبار 1",
            "Fixture Town 1",
            "Fixture Governorate 1",
            True,
            40_000,
            ["administrative"],
        ),
        ("بلدة اختبار 2", "Fixture Town 2", "Fixture Governorate 1", False, 12_000, ["port"]),
        ("بلدة اختبار 3", "Fixture Town 3", "Fixture Governorate 2", True, 7_000, []),
        ("بلدة اختبار 4", "Fixture Town 4", "Fixture Governorate 2", False, 3_000, []),
        ("بلدة اختبار 5", "Fixture Town 5", "Fixture Governorate 3", True, None, []),
    ]
    out = []
    for i, (ar, en, gov, centre, pop, roles) in enumerate(towns):
        r = dict(base)
        r.update(
            name_ar=ar,
            name_en=en,
            governorate=gov,
            is_governorate_centre=centre,
            lat=21.0 + 0.2 * i,
            lon=40.0 + 0.2 * i,
            population=pop,
            pop_source="fixture" if pop is not None else None,
            pop_type="official" if pop is not None else None,
            pop_year=2022 if pop is not None else None,
            tag_10k=pop is not None and pop >= 10_000,
            tag_5k=pop is not None and pop >= 5_000,
            economic_roles=[{"role": role, "source": "fixture"} for role in roles],
            screened=pop is None or pop >= 5_000,
            exclusion_reason=None if (pop is None or pop >= 5_000) else "below 5k and no role",
        )
        RegionRow.model_validate(r)
        out.append(r)
    return out


def main() -> None:
    df = pd.DataFrame(rows())
    df["population"] = df["population"].astype("Int64")
    df["pop_year"] = df["pop_year"].astype("Int64")
    df.to_parquet(HERE / "region_register.parquet", index=False)


if __name__ == "__main__":
    main()
