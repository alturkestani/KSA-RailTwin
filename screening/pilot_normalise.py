"""One-off rewrite of the 13 pilot registers to the canonical `RegionRow` schema.

Coordinator decision, 30 Oct 2026 (PILOT_MERGE, `prompts/PILOT_MERGE.md` "Coordinator decisions" 2):
- `pop_type: secondary` becomes `pop_type: official` + `pop_source_status: secondary` +
  `primary_to_find` (every pilot population is a GASTAT Census 2022 figure relayed by
  citypopulation.de or Wikipedia; none is an aggregator's own estimate, so none becomes `derived`).
  Rows already written as `official` from the same aggregator get the same status fields.
- Pilot columns map to the new optional fields (`threshold_50k`, `pilot_sample`, `dist_method`,
  `road_min_method`, `nearest_metro_tier`, `notes`, `osm_type`); every other extra column is kept
  verbatim inside `notes` as `<column>: <value>`, so nothing a pilot recorded is lost.
- Makkah wrote its populations to the CSV only (`population_secondary`); they are restored from it.
- A row without coordinates cannot be a `RegionRow` (lat/lon required); it is withheld and listed
  in the report so `docs/coverage.md` can carry it (rule 2: no silent omission).

uv run python -m screening.pilot_normalise \
  --pattern "cities/ksa/regions/archive/pilot/pilot-*.parquet"
"""

from __future__ import annotations

import glob
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.schemas import TAG_5K, TAG_10K, TAG_50K, RegionRow, _plain

PRIMARY_DEFAULT = "GASTAT Census 2022 locality or governorate table (portal unreachable, S-090)"
# A-screen-013 (Tariq, 30 Oct 2026); matched on lower-case substrings of the pilot's metro name.
METRO_TIERS: dict[str, int] = {
    "riyadh": 1,
    "jeddah": 1,
    "jiddah": 1,
    "makkah": 1,
    "madinah": 1,
    "dammam": 1,
    "khobar": 1,
    "dhahran": 1,
    "taif": 2,
    "buraidah": 2,
    "buraydah": 2,
    "tabuk": 2,
    "abha": 2,
    "khamis": 2,
    "jazan": 3,
    "jizan": 3,
    "najran": 3,
    "najrān": 3,
}
NOTE_COLUMNS = (
    "sample_reason",
    "pilot_reason",
    "terrain_basis",
    "terrain_source",
    "terrain_status",
    "osm_place_tag",
    "coord_flag",
    "coords_method",
    "screen_stage",
    "assumption_id",
    "dist_station_qassim_km",
    "row_id",
)
FIELDS = set(RegionRow.model_fields)

app = typer.Typer(add_completion=False, help=__doc__)


def _missing(v: Any) -> bool:
    v = _plain(v)
    return v is None or (isinstance(v, float) and math.isnan(v)) or v == ""


def metro_tier(name: Any) -> int | None:
    if _missing(name):
        return None
    low = str(name).lower()
    # the first metro word in the string wins ("Dammam–Khobar–Dhahran (Dammam ...)")
    hits = [(low.find(k), t) for k, t in METRO_TIERS.items() if k in low]
    return min(hits)[1] if hits else None


def _bool(v: Any) -> bool | None:
    v = _plain(v)
    if _missing(v):
        return None
    if isinstance(v, str):
        return v.strip().lower() in ("true", "y", "yes", "1")
    return bool(v)


def normalise_record(rec: dict[str, Any], makkah_csv: dict[str, Any] | None = None) -> dict:
    """Return a canonical `RegionRow` dict and the list of changes made."""
    rec = {k: _plain(v) for k, v in rec.items()}
    notes: list[str] = []
    if not _missing(rec.get("notes")):
        notes.append(str(rec["notes"]))
    if makkah_csv is not None:  # restore Makkah's CSV-only populations and pilot columns
        rec["osm_type"] = makkah_csv.get("osm_type")
        if not _missing(makkah_csv.get("population_secondary")):
            rec["population"] = int(makkah_csv["population_secondary"])
            rec["pop_source"] = makkah_csv["pop_source_secondary"]
            rec["pop_year"] = 2022
            rec["pop_type"] = "secondary"
        for k in ("threshold_50k", "pilot_sample", "sample_reason", "coords_method"):
            rec[k] = makkah_csv.get(k)
        if not _missing(makkah_csv.get("notes")):
            notes.append(str(makkah_csv["notes"]))
    if not _missing(rec.get("distance_method")) and _missing(rec.get("dist_method")):
        rec["dist_method"] = rec["distance_method"]
    if not _missing(rec.get("name_osm_type")) and _missing(rec.get("osm_type")):
        rec["osm_type"] = rec["name_osm_type"]
    for col in NOTE_COLUMNS:
        if not _missing(rec.get(col)):
            label = "sample" if col in ("sample_reason", "pilot_reason") else col
            notes.append(f"{label}: {rec[col]}")
    out = {k: rec.get(k) for k in FIELDS if k in rec}
    out["notes"] = " | ".join(notes) if notes else None
    out["fixture"] = bool(rec.get("fixture") or False)
    for k in ("threshold_50k", "pilot_sample", "is_governorate_centre", "screened"):
        if k in out:
            out[k] = _bool(out[k])
    if out.get("pilot_sample") and not out.get("notes"):
        out["notes"] = "sample: reason not recorded by the pilot"
    for k in list(out):
        if _missing(out[k]) and k not in ("economic_roles", "sources"):
            out[k] = None
    if out.get("osm_type") not in (None, "node", "way", "relation"):
        out["notes"] = f"{out.get('notes') or ''} | osm_type: {out['osm_type']}".strip(" |")
        out["osm_type"] = None
    if out.get("osm_id") is not None:
        out["osm_id"] = int(out["osm_id"])
    pop = out.get("population")
    if pop is not None:
        out["population"] = pop = int(pop)
        if out.get("pop_type") in ("secondary", "official", None):
            out["pop_type"] = "official"
            out["pop_source_status"] = "secondary"
            out["primary_to_find"] = out.get("primary_to_find") or PRIMARY_DEFAULT
        out["pop_year"] = int(out["pop_year"]) if out.get("pop_year") else 2022
        out["tag_10k"], out["tag_5k"] = pop >= TAG_10K, pop >= TAG_5K
        out["threshold_50k"] = pop >= TAG_50K
    else:
        out["pop_type"] = None
        out["pop_source_status"] = None
        out["tag_10k"] = out["tag_5k"] = False
        out["threshold_50k"] = False if out.get("threshold_50k") is not None else None
    if out.get("nearest_metro_tier") is None:
        out["nearest_metro_tier"] = metro_tier(out.get("nearest_metro"))
    else:
        out["nearest_metro_tier"] = int(out["nearest_metro_tier"])
    if out.get("dist_method") is None and any(
        out.get(k) is not None for k in ("dist_existing_km", "dist_committed_km", "dist_metro_km")
    ):
        out["dist_method"] = "haversine (A-screen-pilot-001 of this region)"
    if out.get("road_min_method") is None:
        out["road_min_method"] = "pending R1a skims"
    out["economic_roles"] = list(out.get("economic_roles") or [])
    out["sources"] = list(out.get("sources") or [])
    return out


def normalise_file(path: Path) -> dict[str, Any]:
    df = pd.read_parquet(path)
    file_meta = pq.read_schema(path).metadata or {}
    csv_path = path.with_suffix(".csv")
    makkah = None
    if path.name == "pilot-makkah.parquet":
        makkah = pd.read_csv(csv_path).to_dict(orient="records")
        if [int(r["osm_id"]) for r in makkah] != [int(x) for x in df["osm_id"]]:
            raise ValueError("Makkah CSV and Parquet rows are not aligned")
    rows, withheld = [], []
    for i, rec in enumerate(df.to_dict(orient="records")):
        out = normalise_record(rec, makkah[i] if makkah else None)
        if out.get("lat") is None or out.get("lon") is None:
            withheld.append({"name_en": out["name_en"], "governorate": out["governorate"]})
            continue
        rows.append(RegionRow.model_validate(out).model_dump(mode="json"))
    new = pd.DataFrame(rows)
    keep = {k: v for k, v in file_meta.items() if not k.startswith(b"pandas")}
    if withheld:
        keep[b"withheld_rows"] = json.dumps(withheld, ensure_ascii=False).encode()
    table = pa.Table.from_pandas(new, preserve_index=False)
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **keep})
    pq.write_table(table, path)
    flat = new.copy()
    flat["economic_roles"] = flat["economic_roles"].map(
        lambda rs: ";".join(f"{r['role']}:{r['source']}" for r in rs)
    )
    flat["sources"] = flat["sources"].map(";".join)
    flat.to_csv(csv_path, index=False)
    return {
        "file": path.name,
        "rows_in": len(df),
        "rows_out": len(new),
        "withheld": withheld,
        "pop_rows": int(new["population"].notna().sum()),
    }


@app.command()
def main(
    pattern: str = typer.Option("cities/ksa/regions/archive/pilot/pilot-*.parquet", "--pattern"),
) -> None:
    """Rewrite every matching register (Parquet and CSV) in the canonical schema."""
    for f in sorted(glob.glob(pattern)):
        typer.echo(json.dumps(normalise_file(Path(f)), ensure_ascii=False))


if __name__ == "__main__":
    app()
