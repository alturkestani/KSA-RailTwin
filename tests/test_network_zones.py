"""network.zones helpers on invented inputs (no data files needed)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from network.zones import _osm_population, choose_population, grid_allocate_nearest


def test_osm_population_parse():
    assert _osm_population({"population": "12,345", "population:date": "2010-04"}) == (
        12345,
        2010,
    )
    assert _osm_population({"population": "about 500"}) == (None, None)


def test_grid_allocation_has_no_double_counting():
    # 0.01 deg cells, 3x3 grid of 10 persons each; two settlements share the middle column
    arr = np.full((3, 3), 10.0, dtype="float32")
    transform = (40.0, 22.03, 0.01, 0.01)
    lats, lons = [22.015, 22.015], [40.005, 40.025]
    out = grid_allocate_nearest(arr, transform, lats, lons, [5.0, 5.0])
    assert out.sum() == arr.sum()
    assert sorted(out) == [30.0, 60.0]  # the equidistant middle column goes to one side only
    out_small = grid_allocate_nearest(arr, transform, lats, lons, [0.1, 0.1])
    assert out_small.sum() == 20.0  # only the cell under each point is within 100 m


def test_population_priority_and_quality():
    df = pd.DataFrame(
        {
            "place": ["town", "village", "hamlet"],
            "lat": [22.015, 22.015, 22.025],
            "lon": [40.005, 40.025, 40.025],
            "osm_id": [1, 2, 3],
            "pilot_population": [1000, None, None],
            "pilot_pop_year": [2022, None, None],
            "pilot_pop_type": ["official", None, None],
            "pilot_pop_source": ["S-fixture", None, None],
            "pilot_pop_status": ["secondary", None, None],
            "osm_population": [None, 500, None],
            "osm_population_year": [None, None, None],
        }
    )
    params = {"grid_radius_km": {"value": {"default": 0.1, "town": 0.1}, "assumption_id": "A-x"}}
    arr = np.zeros((3, 3), dtype="float32")
    out = choose_population(
        df,
        (arr, (40.0, 22.03, 0.01, 0.01)),
        params,
        {"year": 2020, "manifest_id": "g", "licence": "CC-BY-4.0"},
    )
    assert out.population.tolist() == [1000, 500, 0]
    assert out.pop_quality.tolist() == ["tabulated_secondary", "osm_tag", "grid_zero"]
    assert out.pop_type.tolist() == ["official", "derived", "grid"]


def test_econ_rows_need_a_source_and_valid_role():
    from network.econ import validate

    df = pd.DataFrame(
        {
            "node_id": ["a", "b", "c", "d"],
            "role": ["port", "port", "spaceport", "airport"],
            "region": ["makkah", "makkah", "makkah", "riyadh"],
            "lat": ["21.5", "21.5", "21.5", ""],
            "lon": ["39.1", "39.1", "39.1", ""],
            "location_method": ["osm:node/1", "osm:node/2", "osm:node/3", "unlocated"],
            "source_id": ["S-1", "", "S-3", "S-4"],
        }
    )
    out, problems = validate(df)
    assert out.node_id.tolist() == ["a", "d"]
    assert out.located.tolist() == [True, False]
    assert len(problems) == 2
