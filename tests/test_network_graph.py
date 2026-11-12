"""Scenario rail graph on the fixture corridor (temporary scenarios and line dirs in tmp_path)."""

import json
import math

import pytest
import yaml

from network.graph import LayerError, build, load_params, segment_minutes

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
FX_ID = "S2-trunk_gap-fixture-corridor"


def _scenario(tmp_path, sid, layers, baseline, include) -> object:
    p = tmp_path / f"{sid}.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "id": sid,
                "kind": "scenario",
                "title": "fixture",
                "layers": layers,
                "baseline": baseline,
                "lines": {"include": include},
                "seed": 1,
                "labels": [LABEL],
                "source": "fixture",
            }
        )
    )
    return p


def _lines_dir(tmp_path, fixtures, extra: list[dict] | None = None):
    d = tmp_path / "lines"
    d.mkdir(exist_ok=True)
    base = yaml.safe_load((fixtures / "corridor.yaml").read_text())
    (d / f"{FX_ID}.yaml").write_text(yaml.safe_dump(base, allow_unicode=True))
    for e in extra or []:
        (d / f"{e['id']}.yaml").write_text(yaml.safe_dump(e, allow_unicode=True))
    return d, base


def test_segment_minutes_hand_values() -> None:
    # 55 km at 200 km/h, a = 0.5, b = 0.6: v = 55.556 m/s, d_ab = 3086.4 + 2572.0 m,
    # t = 111.11 + 92.59 + (55000 - 5658.4) / 55.556 = 1091.85 s = 18.1975 min
    assert segment_minutes(55, 200, 0.5, 0.6) == pytest.approx(18.1975, abs=1e-3)
    # 1 km never reaches cruise: v_p = sqrt(2 L a b / (a + b)) = 23.355 m/s; t = 85.63 s
    assert segment_minutes(1, 200, 0.5, 0.6) == pytest.approx(1.42725, abs=1e-4)
    assert segment_minutes(0, 200, 0.5, 0.6) == 0.0
    assert math.isnan(segment_minutes(10, float("nan"), 0.5, 0.6))


def test_fixture_corridor_graph(tmp_path, fixtures) -> None:
    lines, _ = _lines_dir(tmp_path, fixtures)
    scn = _scenario(tmp_path, "S2", ["existing", "committed", "hypothetical"], "S1", [FX_ID])
    out = tmp_path / "g"
    summary = build(scn, out, 1, lines_dir=lines)
    hyp = summary["layers"]["hypothetical"]
    assert hyp == {"lines": 1, "line_ids": [FX_ID], "stations": 3, "edges": 2, "km": 120.0}
    data = json.loads((out / "graph.json").read_text())
    ids = sorted(n["id"] for n in data["nodes"])
    assert ids == [f"{FX_ID}:fx-a", f"{FX_ID}:fx-b", f"{FX_ID}:fx-c"]
    kms = sorted(e["km"] for e in data["edges"])
    assert kms == [55.0, 65.0]
    e = next(e for e in data["edges"] if e["km"] == 55.0)
    assert e["run_min"] == pytest.approx(18.1975, abs=1e-3) and e["dwell_min"] == 2.0
    src = json.loads(e["params_source"])
    assert src["cruise_kmh"].startswith("line:") and src["dwell_s"].startswith("line:")
    meta = json.loads((out / "meta.json").read_text())
    assert meta["scenario"] == "S2" and meta["seed"] == 1 and LABEL in meta["label"]
    for f in ("nodes.parquet", "edges.parquet", "summary.json"):
        assert (out / f).exists()


def test_s0_rejects_committed_line(tmp_path, fixtures) -> None:
    base = yaml.safe_load((fixtures / "corridor.yaml").read_text())
    committed = {
        **base,
        "id": "fixture-committed",
        "layer": "committed",
        "status": "announced",
        "generated_from": None,
        "rules_hash": None,
    }
    lines, _ = _lines_dir(tmp_path, fixtures, [committed])
    scn = _scenario(tmp_path, "S0", ["existing"], None, ["fixture-committed"])
    with pytest.raises(LayerError, match="committed"):
        build(scn, tmp_path / "g", 1, lines_dir=lines)


def test_layer_not_allowed(tmp_path, fixtures) -> None:
    lines, _ = _lines_dir(tmp_path, fixtures)
    scn = _scenario(tmp_path, "S1", ["existing", "committed"], "S0", [FX_ID])
    with pytest.raises(LayerError, match="hypothetical"):
        build(scn, tmp_path / "g", 1, lines_dir=lines)


def test_missing_line_file(tmp_path, fixtures) -> None:
    lines, _ = _lines_dir(tmp_path, fixtures)
    scn = _scenario(tmp_path, "S2", ["hypothetical"], "S1", ["no-such-line"])
    with pytest.raises(FileNotFoundError):
        build(scn, tmp_path / "g", 1, lines_dir=lines)


def test_interchanges_and_defaults(tmp_path, fixtures) -> None:
    base = yaml.safe_load((fixtures / "corridor.yaml").read_text())
    walk = load_params()["interchange"]["walk_max_km"]["value"]
    # second fixture line: stations about 0.1 km east of fx-a and fx-c (within the walk
    # distance), no running_time_model -> design speed + default accel/decel/dwell
    twin = {
        **base,
        "id": "fixture-twin",
        "running_time_model": {},
        "services": [],
        "stations": [
            {**base["stations"][0], "id": "tw-a", "name_en": "Twin A", "lon": 40.001},
            {**base["stations"][2], "id": "tw-c", "name_en": "Twin C", "lon": 40.701},
        ],
    }
    lines, _ = _lines_dir(tmp_path, fixtures, [twin])
    scn = _scenario(tmp_path, "S2", ["hypothetical"], "S1", [FX_ID, "fixture-twin"])
    out = tmp_path / "g"
    summary = build(scn, out, 1, lines_dir=lines)
    assert summary["interchange_edges"] == 2
    data = json.loads((out / "graph.json").read_text())
    ic = [e for e in data["edges"] if e["kind"] == "interchange"]
    assert all(e["km"] < walk and e["reason"] == "walk_distance" for e in ic)
    tw = next(e for e in data["edges"] if e.get("line") == "fixture-twin")
    src = json.loads(tw["params_source"])
    assert src["cruise_kmh"] == "line:design_speed_kmh"
    assert src["accel_ms2"] == "default:A-r1a-033" and src["dwell_s"] == "default:A-r1a-035"
    meta = json.loads((out / "meta.json").read_text())
    assert {"A-r1a-030", "A-r1a-033", "A-r1a-035"} <= set(meta["assumptions"])


def test_group_id_expansion(tmp_path, fixtures) -> None:
    base = yaml.safe_load((fixtures / "corridor.yaml").read_text())
    parts = []
    for n, dlon in ((2, 1.0), (1, 2.0)):  # written out of order: expansion must sort
        parts.append(
            {
                **base,
                "id": f"fixture-grp-l{n}",
                "services": [],
                "stations": [
                    {**st, "id": f"g{n}-{st['id']}", "lon": st["lon"] + dlon}
                    for st in base["stations"]
                ],
            }
        )
    lines, _ = _lines_dir(tmp_path, fixtures, parts)
    scn = _scenario(tmp_path, "S2", ["hypothetical"], "S1", [FX_ID, "fixture-grp"])
    summary = build(scn, tmp_path / "g", 1, lines_dir=lines)
    assert summary["expanded_ids"] == {"fixture-grp": ["fixture-grp-l1", "fixture-grp-l2"]}
    assert summary["layers"]["hypothetical"]["lines"] == 3
    scn2 = _scenario(tmp_path, "S3", ["hypothetical"], "S1", ["no-such-group"])
    with pytest.raises(FileNotFoundError, match="no-such-group"):
        build(scn2, tmp_path / "g2", 1, lines_dir=lines)
