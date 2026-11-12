"""CP2_PREP item 6: `rail.lines build` merges stations.geojson; `apply-sites` writes research."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from rail.lines import apply_sites, preserve_located


def _feat(uid: str, method: str, lon: float, notes: str | None = None) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, 24.0]},
        "properties": {
            "station_uid": uid,
            "location_method": method,
            "located": not method.startswith("unlocated"),
            "uncertainty_km": 5.0,
            "snap_km": None,
            "site_status": "inferred",
            "confidence": None,
            "notes": notes,
        },
    }


def _write(path: Path, feats: list[dict]) -> None:
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), "utf-8")


def test_rebuild_preserves_located_stations(tmp_path: Path) -> None:
    old = tmp_path / "stations.geojson"
    _write(
        old,
        [
            _feat("l:geo", "osm_spur_end:way/1", 46.1, "geo-verify"),
            _feat("l:research", "town_centroid:osm:node/2", 46.2, "research"),
            _feat("l:osm", "osm:node/3", 46.3),
            _feat("l:still", "unlocated:town_centroid_proxy:osm:node/4", 46.4, "searched X"),
        ],
    )
    new = [
        _feat("l:geo", "unlocated:track_node_nearest_to_osm:node/9", 47.1),
        _feat("l:research", "unlocated:town_centroid_proxy:osm:node/2", 47.2),
        _feat("l:osm", "osm:node/3", 47.3),  # OSM moved the station: the new position wins
        _feat("l:still", "unlocated:town_centroid_proxy:osm:node/4", 47.4),
        _feat("l:new", "unlocated:x", 47.5),
    ]
    assert preserve_located(new, old) == 2
    by = {f["properties"]["station_uid"]: f for f in new}
    assert by["l:geo"]["geometry"]["coordinates"][0] == 46.1
    assert by["l:geo"]["properties"]["location_method"] == "osm_spur_end:way/1"
    assert by["l:research"]["properties"]["notes"] == "research"
    assert by["l:osm"]["geometry"]["coordinates"][0] == 47.3
    assert by["l:still"]["geometry"]["coordinates"][0] == 47.4
    assert by["l:still"]["properties"]["notes"] == "searched X"
    assert by["l:new"]["properties"]["location_method"] == "unlocated:x"
    assert preserve_located(new, tmp_path / "missing.geojson") == 0


def test_apply_sites(tmp_path: Path) -> None:
    lines = tmp_path / "cities/ksa/lines"
    lines.mkdir(parents=True)
    _write(
        lines / "stations.geojson",
        [_feat("l:a", "unlocated:p", 46.0), _feat("l:b", "unlocated:p", 46.0)],
    )
    sites = tmp_path / "research.yaml"
    entry = {"location_method": "town_centroid:osm:node/5", "confidence": "low"}
    sites.write_text(
        yaml.safe_dump(
            {
                "stations": [
                    {
                        "station_uid": "l:a",
                        "outcome": "low_confidence",
                        "lat": 25.0,
                        "lon": 45.0,
                        "uncertainty_km": 3.2,
                        "sources": ["S-x"],
                        **entry,
                    },
                    {
                        "station_uid": "l:b",
                        "outcome": "unlocated",
                        "lat": None,
                        "lon": None,
                        "sources": ["S-y"],
                        "notes": "nothing found",
                    },
                ]
            }
        ),
        "utf-8",
    )
    apply_sites(sites=sites, root=tmp_path)
    gj = json.loads((lines / "stations.geojson").read_text("utf-8"))
    a, b = gj["features"]
    assert a["geometry"]["coordinates"] == [45.0, 25.0]
    assert a["properties"]["located"] is False and a["properties"]["uncertainty_km"] == 3.2
    assert a["properties"]["confidence"] == "low"
    assert b["geometry"]["coordinates"] == [46.0, 24.0]
    assert b["properties"]["location_method"] == "unlocated:p"
    assert "nothing found" in b["properties"]["notes"]
