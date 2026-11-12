"""INTEGRATE_R2 (CP3 4a/5a): national relay page, OSM place polygons and the place-rank tie-break,
judgement placements outside the register, `pop_type: derived`, the zero-population grid drop and
the before/after check. Synthetic inputs (fictional places); runs in about a second.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from screening import control_total, integrate_r2_check, primary_match
from screening.merge import merge_frames

ROOT = Path(__file__).parents[1]
FIX = ROOT / "tests" / "fixtures" / "region_register.parquet"
NO_CP2 = pd.DataFrame(columns=["city", "settlement_id", "tier"])


def _reg() -> pd.DataFrame:
    merged, _ = merge_frames([FIX])
    return merged


def _univ(reg: pd.DataFrame) -> pd.DataFrame:
    u = reg[["name_en", "name_ar", "region", "lat", "lon", "population", "pop_type"]].copy()
    u["settlement_id"] = [f"U{i}" for i in range(len(u))]
    u["osm_type"], u["osm_id"] = None, None
    u["grid_population"] = u.population
    return u


def _cities(rows: list[tuple[str, int]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["name", "total"]).assign(saudi=0, non_saudi=0)


def _osm(rows: list[dict]) -> pd.DataFrame:
    d = pd.DataFrame(rows)
    d["name_en"] = None
    d["gov_name_en"], d["gov_name_ar"] = "Fixture Gov", "محافظة فكسشر"
    d["an"] = d.name_ar.map(primary_match.ar_norm)
    return d


def test_national_relay_page_reads_region_code_and_drops_regional_duplicates(tmp_path: Path):
    def row(name: str, code: str, ar: str, pop: str) -> str:
        return (f'<tr itemscope><td class="rname">{name}</td><td class="radm">{code}</td>'
                f'<td class="rnative">{ar}</td><td class="rpop">...</td><td class="rpop">{pop}'
                '</td><td class="noviz">0</td></tr>')  # fmt: skip

    nat = tmp_path / "national.html"
    nat.write_text(row("Qarya Uno", "RYD", "قرية أولى", "42,179") + row(
        "Qarya Dos", "SHQ", "قرية ثانية", "21,992"), encoding="utf-8")  # fmt: skip
    regional = tmp_path / "regional.html"
    regional.write_text(
        "<tr><td>Qarya Dos</td><td>قرية ثانية</td><td>Place</td><td>Al-Fixture</td>"
        "<td>21,992</td></tr>",
        encoding="utf-8",
    )
    r = primary_match.read_relays({str(nat): (None, "S-nat"), str(regional): ("eastern", "S-reg")})
    assert len(r) == 2  # the national copy of Qarya Dos is dropped
    uno = r[r.name == "Qarya Uno"].iloc[0]
    assert uno.region == "riyadh" and uno.pop_2022 == 42179 and bool(uno.national)
    assert r[r.name == "Qarya Dos"].iloc[0].source == "S-reg"


def test_relay_bridge_takes_highest_place_rank_and_is_derived():
    reg, cities = _reg(), _cities([("Qarya Uno", 42179)])
    relays = pd.DataFrame([{"source": "S-nat", "region": "riyadh", "name": "Qarya Uno",
                            "name_ar": "قرية أولى", "governorate": None,
                            "pop_2022": 42179}])  # fmt: skip
    osm = _osm([
        {"osm_type": "node", "osm_id": 11, "place": "hamlet", "name_ar": "قرية أولى",
         "lat": 24.1, "lon": 46.1, "region": "riyadh"},
        {"osm_type": "node", "osm_id": 12, "place": "town", "name_ar": "قرية أولى",
         "lat": 24.2, "lon": 46.2, "region": "riyadh"},
    ])  # fmt: skip
    t = primary_match.match(reg, _univ(reg), cities, NO_CP2, relays, osm, {})
    r = t.iloc[0]
    assert r.tier == "relay bridge (OSM extract)" and r.status == "created"
    assert r.osm["osm_id"] == 12 and r.pop_type == "derived"
    # a shared top rank is no match (A-r2-003)
    osm.loc[osm.osm_id == 11, "place"] = "town"
    t = primary_match.match(reg, _univ(reg), cities, NO_CP2, relays, osm, {})
    assert t.iloc[0].status == "unmatched"


def test_relay_bridge_prefers_node_over_polygon():
    reg, cities = _reg(), _cities([("Qarya Dos", 21992)])
    relays = pd.DataFrame([{"source": "S-reg", "region": "eastern", "name": "Qarya Dos",
                            "name_ar": "قرية ثانية", "governorate": None,
                            "pop_2022": 21992}])  # fmt: skip
    osm = _osm([
        {"osm_type": "way", "osm_id": 21, "place": "village", "name_ar": "قرية ثانية",
         "lat": 25.4, "lon": 49.6, "region": "eastern"},
        {"osm_type": "node", "osm_id": 22, "place": "neighbourhood", "name_ar": "قرية ثانية",
         "lat": 25.5, "lon": 49.7, "region": "eastern"},
    ])  # fmt: skip
    t = primary_match.match(reg, _univ(reg), cities, NO_CP2, relays, osm, {})
    assert t.iloc[0].osm["osm_type"] == "node"


def test_judgement_on_osm_place_outside_register_creates_row_with_decided_type():
    reg = _reg()
    cities = _cities([("Fixture Industrial City", 172233), ("Fixture Suburb", 10793)])
    osm = _osm([
        {"osm_type": "node", "osm_id": 31, "place": "locality", "name_ar": "مدينة صناعية",
         "lat": 27.07, "lon": 49.59, "region": "eastern"},
        {"osm_type": "node", "osm_id": 32, "place": "suburb", "name_ar": "ضاحية",
         "lat": 25.0, "lon": 46.6, "region": "riyadh"},
    ])  # fmt: skip
    dec = {
        "Fixture Industrial City": {"osm_type": "node", "osm_id": 31, "region": "eastern",
                                    "pop_type": "official", "evidence": "instruction"},
        "Fixture Suburb": {"osm_type": "node", "osm_id": 32, "region": "riyadh",
                           "evidence": "only place with that name"},
    }  # fmt: skip
    t = primary_match.match(reg, _univ(reg), cities, NO_CP2, pd.DataFrame(), osm, dec)
    got = t.set_index("city")
    assert list(got.status) == ["created", "created"]
    assert got.at["Fixture Industrial City", "pop_type"] == "official"
    assert got.at["Fixture Suburb", "pop_type"] == "derived"


def test_apply_writes_derived_pop_type():
    reg = _reg()
    key = reg.row_key.iloc[0]
    t = pd.DataFrame({"city": ["A"], "total": [20000], "tier": ["judgement"], "row_key": [key],
                      "settlement_id": [None], "status": ["matched"], "osm": [None],
                      "pop_type": ["derived"]})  # fmt: skip
    new, _ = primary_match.apply(reg, t, _univ(reg))
    row = new[new.row_key == key].iloc[0]
    assert row.pop_type == "derived" and row.pop_source_status == "verified"
    assert row.population == 20000 and bool(row.tag_10k)


def test_drop_zero_takes_only_raw_zero_grid_rows():
    reg = pd.DataFrame({"row_key": list("abcd"), "pop_type": ["grid", "grid", "official", "grid"],
                        "pop_grid_raw": [0.0, 0.4, None, 12.0],
                        "population": [0.0, 0.0, 0.0, 8.0]})  # fmt: skip
    # b rounds to 0 after scaling but its raw value is not 0; c is not a grid row
    assert list(control_total.drop_zero(reg).row_key) == ["a"]


def test_compare_scores_reports_entries_exits_and_moves():
    a = pd.DataFrame({"row_key": ["x", "y", "z"], "name_en": ["X", "Y", "Z"],
                      "rank": [1, 2, 3], "short_list": [True, True, False]})  # fmt: skip
    b = pd.DataFrame({"row_key": ["n", "x", "y", "z"], "name_en": ["N", "X", "Y", "Z"],
                      "rank": [1, 2, 4, 3], "short_list": [True, True, False, False]})  # fmt: skip
    c = integrate_r2_check.compare_scores(a, b)
    assert [e["row_key"] for e in c["enter"]] == ["n"]
    assert [e["row_key"] for e in c["leave"]] == ["y"]
    assert c["new_in_long_list"] == 1 and c["rank_changed"] == 2 and c["max_down"] == 2
    assert c["moved_up"] == []
