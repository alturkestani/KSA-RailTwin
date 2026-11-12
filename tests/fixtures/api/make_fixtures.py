"""Rebuild the dashboard-API fixtures from the repo's registers and runs (tiny, trimmed copies).

    uv run python tests/fixtures/api/make_fixtures.py

Writes `tests/fixtures/api/{cities,scenarios}/...` and `tests/fixtures/api/run_outputs/...` (the
latter mirrors `runs/`, which is gitignored at every depth). Geometry is decimated, tables are cut
to a few rows and JSON documents keep only the rows the API reads. Values are copied, never edited.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUNS_OUT = OUT / "run_outputs"

CORRIDORS = [
    "branch_spur/S3-branch_spur-al-kharj",
    "commuter_belt/S4-commuter_belt-riyadh-225",
    "station_addition/S5-station_addition-al-jubayl",
    "station_addition/S5-station_addition-dhahran",
    "station_addition/S5-station_addition-duruma",
]
CBA_CASES = [
    "CBA-S1-committed-programme",
    "CBA-S3-branch_spur-al-kharj",
    "CBA-S5-station_addition-dhahran",
]
KEEP_ROWS = {("un_wpp_low", 60), ("un_wpp_medium", 60), ("un_wpp_high", 60), ("un_wpp_medium", 30)}


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _decimate(geom: dict, step: int) -> dict:
    def line(coords: list) -> list:
        if len(coords) <= 4:
            return coords
        kept = coords[::step]
        if kept[-1] != coords[-1]:
            kept.append(coords[-1])
        return [[round(x, 4), round(y, 4)] for x, y, *_ in kept]

    t = geom["type"]
    if t == "LineString":
        return {"type": t, "coordinates": line(geom["coordinates"])}
    if t == "MultiLineString":
        return {"type": t, "coordinates": [line(c) for c in geom["coordinates"]]}
    if t == "Polygon":
        return {"type": t, "coordinates": [line(r) for r in geom["coordinates"][:1]]}
    if t == "MultiPolygon":
        return {"type": "Polygon", "coordinates": [line(geom["coordinates"][0][0])]}
    return geom


def _geojson(src: str, dst: str, n: int, step: int, keep=None) -> None:
    fc = json.loads((REPO / src).read_text(encoding="utf-8"))
    feats = [f for f in fc["features"] if keep is None or keep(f)][:n]
    fc["features"] = [{**f, "geometry": _decimate(f["geometry"], step)} for f in feats]
    _write_json(OUT / dst, fc)


def lines_and_zones() -> None:
    d = "cities/ksa/lines/geojson"
    _geojson(f"{d}/existing.geojson", f"{d}/existing.geojson", 2, 40)
    _geojson(f"{d}/committed.geojson", f"{d}/committed.geojson", 3, 10)
    _geojson(f"{d}/historical.geojson", f"{d}/historical.geojson", 1, 60)
    _geojson("cities/ksa/lines/stations.geojson", "cities/ksa/lines/stations.geojson", 6, 1)
    _geojson("cities/ksa/zones/regions.geojson", "cities/ksa/zones/regions.geojson", 2, 200)
    for c in CORRIDORS:
        src = REPO / "cities/ksa/corridors" / f"{c}.yaml"
        dst = OUT / "cities/ksa/corridors" / f"{c}.yaml"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        cid = c.split("/")[1]
        a = f"cities/ksa/alignments/{cid}.geojson"
        if (REPO / a).exists():
            _geojson(a, a, 2, 25)


def register() -> None:
    cand = pd.read_parquet(REPO / "cities/ksa/candidates.parquet")
    ll = pd.read_parquet(REPO / "runs/r2/long-list/longlist.parquet")
    sc = pd.read_parquet(REPO / "runs/r2/score/scores.parquet")
    short = sc[sc["short_list"]]["row_key"].head(4).tolist()
    longl = sc[~sc["short_list"]]["row_key"].head(3).tolist()
    served = ll[ll["pass_threshold"] & ll["served"]]["row_key"].head(2).tolist()
    rest = cand[~cand["row_key"].isin(set(ll[ll["pass_threshold"]]["row_key"]))]
    other = rest["row_key"].head(3).tolist()
    keys = short + longl + served + other
    (OUT / "cities/ksa").mkdir(parents=True, exist_ok=True)
    cand[cand["row_key"].isin(keys)].to_parquet(OUT / "cities/ksa/candidates.parquet", index=False)
    (RUNS_OUT / "r2/long-list").mkdir(parents=True, exist_ok=True)
    (RUNS_OUT / "r2/score").mkdir(parents=True, exist_ok=True)
    ll[ll["row_key"].isin(keys)][["row_key", "pass_threshold", "served"]].to_parquet(
        RUNS_OUT / "r2/long-list/longlist.parquet", index=False
    )
    sc[sc["row_key"].isin(keys)][["row_key", "region", "short_list", "score", "rank"]].to_parquet(
        RUNS_OUT / "r2/score/scores.parquet", index=False
    )
    shutil.copyfile(REPO / "runs/r2/long-list/counts.json", RUNS_OUT / "r2/long-list/counts.json")


def scenarios() -> None:
    (OUT / "scenarios").mkdir(parents=True, exist_ok=True)
    for sid in ["S0", "S1", "S2", "S3", "S4", "S5"] + [f"S6-L{i}" for i in range(1, 7)]:
        shutil.copyfile(REPO / f"scenarios/{sid}.yaml", OUT / f"scenarios/{sid}.yaml")


def cba() -> None:
    for case in CBA_CASES:
        doc = json.loads((REPO / f"runs/cba/{case}/results.json").read_text(encoding="utf-8"))
        doc["results"] = [
            r
            for r in doc["results"]
            if (r["population"], r["horizon"]) in KEEP_ROWS and r["rate_case"] == "greenbook_2026"
        ]
        _write_json(RUNS_OUT / f"cba/{case}/results.json", doc)


def r6() -> None:
    top = RUNS_OUT / "r6/top5"
    top.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / "runs/r6/top5/top5.csv", top / "top5.csv")
    shutil.copyfile(REPO / "runs/r6/pareto_front.csv", RUNS_OUT / "r6/pareto_front.csv")
    for i in range(1, 6):
        shutil.copyfile(REPO / f"runs/r6/top5/L{i}.layout.yaml", top / f"L{i}.layout.yaml")
        s = json.loads((REPO / f"runs/r6/top5/L{i}/score.json").read_text(encoding="utf-8"))
        s.pop("accessibility", None)
        s["appraisal_rows"] = [
            r
            for r in s["appraisal_rows"]
            if (r["population"], r["horizon"]) in KEEP_ROWS and r["rate_case"] == "greenbook_2026"
        ]
        _write_json(top / f"L{i}/score.json", s)


def l6() -> None:
    """S6-L6 (R8_L6_PANEL): its own score directory, mirrored under run_outputs/r6/l6/, never
    copied into the top5 fixtures (it is not a top-5 layout)."""
    l6 = RUNS_OUT / "r6/l6"
    (l6 / "score").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / "runs/r6/l6/L6.layout.yaml", l6 / "L6.layout.yaml")
    shutil.copyfile(REPO / "runs/r6/l6/score/S6-L6.csv", l6 / "score/S6-L6.csv")
    s = json.loads((REPO / "runs/r6/l6/score/score.json").read_text(encoding="utf-8"))
    s.pop("accessibility", None)
    s["appraisal_rows"] = [
        r
        for r in s["appraisal_rows"]
        if (r["population"], r["horizon"]) in KEEP_ROWS and r["rate_case"] == "greenbook_2026"
    ]
    _write_json(l6 / "score/score.json", s)


def r7() -> None:
    f = json.loads((REPO / "runs/r7/fiscal/fiscal.json").read_text(encoding="utf-8"))
    for group in ("programmes", "corridors"):
        for body in f[group].values():
            for m in body["models"].values():
                for by in m["by_pop"].values():
                    for k in ("budget_share", "contingent_liabilities", "timing_p50_5y"):
                        by.pop(k, None)
    f["corridors"] = {k: v for k, v in f["corridors"].items() if k == "S5-station_addition-dhahran"}
    f["baseline_s1"]["rows"] = {
        k: v for k, v in f["baseline_s1"]["rows"].items() if k.endswith("|60")
    }
    _write_json(RUNS_OUT / "r7/fiscal/fiscal.json", f)
    v = json.loads((REPO / "runs/r7/vfm/vfm.json").read_text(encoding="utf-8"))
    v["corridors"] = {k: x for k, x in v["corridors"].items() if k == "S5-station_addition-dhahran"}
    _write_json(RUNS_OUT / "r7/vfm/vfm.json", v)


def main() -> None:
    for sub in ("cities", "scenarios", "run_outputs"):
        shutil.rmtree(OUT / sub, ignore_errors=True)
    lines_and_zones()
    register()
    scenarios()
    cba()
    r6()
    l6()
    r7()
    sizes = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"fixtures written under {OUT.relative_to(REPO)} ({sizes / 1024:.0f} KiB)")
    with (OUT / "MANIFEST.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "bytes"])
        for p in sorted(OUT.rglob("*")):
            if p.is_file() and p.name != "MANIFEST.csv" and p.suffix != ".pyc":
                w.writerow([str(p.relative_to(OUT)), p.stat().st_size])


if __name__ == "__main__":
    main()
