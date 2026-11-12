"""National primary-city matching at the R2 merge (Tariq, 31 Oct 2026 16:25; `prompts/R2.md`).

Every GASTAT primary Census 2022 city of 5,000 or more (TA1 export, 271 rows, S-cp2-gastat-008)
gets a register row or is listed as unmatched with its population, so no official city drops
silently (rule 2). Tiers, strictest first (A-r2-001):

1. `cp2` the CP2_PREP match (`runs/gastat/primary/city_matches.csv`, tiers of A-screen-038), carried
   to the register row with the same OSM object (name-keyed rows: the same name within 2 km);
2. `sweep` a register row whose sweep already wrote this city's primary figure (S-cp2-gastat-008);
3. `relay bridge` the city's total appears once in a locally archived citypopulation.de Census 2022
   page (registered relays of the same census, D11a) with an Arabic name and region; the OSM place
   with that Arabic name (normalised) in that region takes the city;
4. `identical figure` a register row holding the same figure from a relay under another name, with
   the figure unique in the primary table (C-gastat-003/004: primary wins, both names logged);
5. `arabic skeleton` the consonant skeleton of the export spelling equals the skeleton of exactly
   one unclaimed OSM place's Arabic name (>= 3 consonants), and that place passes the plausibility
   guard (A-r2-002).

A match found only in the settlement universe creates a register row from the universe (R1a
distances, skims and governorate; roles not assessed). Matched rows carry the primary figure as
`pop_type: official`, `pop_source_status: verified`, and `tag_10k` on that figure alone.

uv run python -m screening.primary_match --register cities/ksa/candidates.parquet --seed 1
Label: screening input, not a forecast.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common.runmeta import write_meta
from common.schemas import TAG_5K, TAG_10K
from screening.gastat import key_skeleton, read_city_primary

app = typer.Typer(add_completion=False, help=__doc__)

CP2_MATCHES = Path("runs/gastat/primary/city_matches.csv")
UNIVERSE = Path("cities/ksa/zones/settlements.parquet")
PRIMARY_SRC = "S-cp2-gastat-008"
# Locally archived citypopulation.de Census 2022 pages (manifest rows; facts only, D11a), with the
# region each page covers (None = national page: the region is read from the row).
RELAYS: dict[str, tuple[str | None, str]] = {
    "data/ksa/regions-pilot/citypop-eastern-census2022.html": ("eastern", "S-eastern-001"),
    "data/ksa/pilot-qassim/raw/citypop_qasim_region.html": ("qassim", "S-qassim-001"),
    "data/ksa/hail/citypop_hail_census2022.csv": ("hail", "S-hail-001"),
    # national cities page (INTEGRATE_R2 item 1): region from the page's region code; a row also
    # on a regional page (same figure, same Arabic name) is dropped in favour of the regional row
    "data/ksa/pilot-qassim/raw/citypop_cities.html": (None, "S-qassim-003"),
}
# citypopulation.de region codes on the national page -> register region slugs
REGION_CODES = {
    "RYD": "riyadh", "MKM": "makkah", "MDM": "madinah", "QSM": "qassim", "SHQ": "eastern",
    "ASI": "asir", "TBK": "tabuk", "HAL": "hail", "HDS": "northern_borders", "JAZ": "jazan",
    "NJR": "najran", "BAH": "al_baha", "JWF": "al_jouf",
}  # fmt: skip
GUARD = (0.105, 2.103)  # A-r2-002: size hint / primary total; 5th-95th pct of the CP2 back-test
GUARD_NATIONAL = (0.37, 1.157)  # A-r2-002: IQR of the same back-test, for name-only matches
NAME_KM = 2.0  # A-r2-001: a name-keyed register row is the same place within this distance
TIERS = ["cp2", "judgement", "sweep", "relay bridge", "identical figure", "arabic skeleton"]
DECISIONS = Path("screening/primary_match_decisions.yaml")
# CP3 4a (Tariq, 31 Oct 2026): a place found only by OSM name (created from the OSM extract) or by
# judgement carries the primary figure as `pop_type: derived` (the figure is TA1, the location is
# derived); a judgement decision may say `pop_type: official` where the evidence is direct
DERIVED_TIERS = ("relay bridge (OSM extract)", "judgement")
# OSM place rank, used only to break a tie between same-name places in one region (A-r2-003)
PLACE_RANK = {"city": 0, "town": 1, "village": 2, "suburb": 3, "quarter": 3, "neighbourhood": 4,
              "hamlet": 5, "locality": 6, "isolated_dwelling": 7, "farm": 7}  # fmt: skip

_AR_DROP = set("اأإآٱءئؤوىيع") | {"ـ"}
_AR_MAP = {
    "ب": "b", "ت": "t", "ث": "t", "ج": "j", "ح": "h", "خ": "k", "د": "d", "ذ": "d", "ر": "r",
    "ز": "d", "س": "s", "ش": "s", "ص": "s", "ض": "d", "ط": "t", "ظ": "d", "غ": "g", "ف": "f",
    "ق": "k", "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "ة": "h",
}  # fmt: skip  # mirrors key_skeleton's reductions (kh->k, q->k, dh->d, th->t, sh->s, z->d)


def ar_norm(s: Any) -> str:
    """Arabic name key: diacritics and tatweel removed; hamza forms, ى/ي and ة/ه unified."""
    if not isinstance(s, str):
        return ""
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.replace("ـ", "")
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ٱ", "ا"), ("ى", "ي"), ("ة", "ه")):
        s = s.replace(a, b)
    s = re.sub(r"^محافظة\s+", "", s.strip())
    return re.sub(r"\s+", " ", s)


def ar_skeleton(s: Any) -> str:
    """Consonant skeleton of an Arabic name in the alphabet of `key_skeleton` (leading ال dropped,
    long vowels, hamza and ع dropped, a final ة/ه dropped, doubles collapsed)."""
    s = ar_norm(s)
    s = s[2:] if s.startswith("ال") and len(s) > 3 else s
    out = "".join(_AR_MAP.get(c, "") for c in s if c not in _AR_DROP)
    if s.endswith("ه"):  # ة/ه ending (TA1 writes "uh"/"h", which key_skeleton drops)
        out = out[:-1]
    return re.sub(r"(.)\1+", r"\1", out)


def haversine_km(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> Any:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = (
        np.sin((p2 - p1) / 2) ** 2
        + np.cos(p1) * np.cos(p2) * np.sin((np.radians(lon2) - np.radians(lon1)) / 2) ** 2
    )
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


OSM_PLACES = Path("data/ksa/osm/gcc-places.geojsonseq")  # manifest osm-gcc-places-extract-*
# place polygons (ways/relations), manifest osm-gcc-place-areas-extract-* (INTEGRATE_R2 item 1)
OSM_PLACE_AREAS = Path("data/ksa/osm/gcc-place-areas.geojsonseq")
GOVS = Path("cities/ksa/zones/governorates.geojson")
STATIONS = Path("cities/ksa/lines/stations.geojson")
INTERCITY = ("hhr", "sar-north-passenger", "sar-east-passenger")  # A-r1a-008


def read_osm_places(path: Path = OSM_PLACES, areas: Path | None = OSM_PLACE_AREAS) -> pd.DataFrame:
    """Every OSM place node of the GCC extract (incl. suburb/neighbourhood, which the R1a universe
    leaves out), plus, where the areas extract exists, every place polygon (way/relation) at its
    representative point (INTEGRATE_R2 item 1: Al-Ahsa villages are mapped as polygons), with its
    governorate and region from the OSM polygons (point in polygon)."""
    from shapely.geometry import Point, shape
    from shapely.strtree import STRtree

    gj = json.loads(GOVS.read_text(encoding="utf-8"))["features"]
    polys = [shape(f["geometry"]) for f in gj]
    tree = STRtree(polys)
    rows = []
    for src in (path, areas):
        if src is None or not src.exists():
            continue
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip().lstrip("\x1e")
            if not line:
                continue
            f = json.loads(line)
            q = f["properties"]
            if f["geometry"]["type"] == "Point":
                lon, lat = f["geometry"]["coordinates"]
            else:
                rp = shape(f["geometry"]).representative_point()
                lon, lat = rp.x, rp.y
            rows.append({"osm_type": q.get("@type"), "osm_id": int(q["@id"]),
                         "place": q.get("place"), "name_ar": q.get("name:ar") or q.get("name"),
                         "name_en": q.get("name:en"), "lat": float(lat),
                         "lon": float(lon)})  # fmt: skip
    d = pd.DataFrame(rows)
    gov = []
    for lat, lon in zip(d.lat, d.lon, strict=True):
        pt = Point(lon, lat)
        hit = [i for i in tree.query(pt) if polys[i].contains(pt)]
        gov.append(gj[hit[0]]["properties"] if hit else {})
    d["region"] = [g.get("region") for g in gov]
    d["gov_name_en"] = [g.get("name_en") for g in gov]
    d["gov_name_ar"] = [g.get("name_ar") for g in gov]
    d = d[d.region.notna()].reset_index(drop=True)
    d["an"] = d.name_ar.map(ar_norm)
    return d


def station_distances(lat: float, lon: float) -> dict[str, Any]:
    """Great-circle distances to the nearest intercity existing and committed station
    (A-r1a-008 line set; committed stops partly unlocated proxies, A-r1a-007)."""
    feats = json.loads(STATIONS.read_text(encoding="utf-8"))["features"]
    out: dict[str, Any] = {}
    for layer, keep in (("existing", lambda q: q["line_id"] in INTERCITY),
                        ("committed", lambda q: True)):  # fmt: skip
        best = (np.inf, None, None)
        for f in feats:
            q = f["properties"]
            if q["layer"] != layer or not keep(q):
                continue
            x, y = f["geometry"]["coordinates"]
            d = float(haversine_km(lat, lon, y, x))
            if d < best[0]:
                best = (d, q["station_uid"], q["line_id"])
        out[f"dist_{layer}_km"] = round(best[0], 2)
        out[f"nearest_{layer}"] = best[1] if layer == "existing" else best[2]
        if layer == "committed":
            out["nearest_committed_station"] = best[1]
    return out


# ----------------------------------------------------------------------------- relays
def _cells(row_html: str) -> list[str]:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S)
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in cells]


def read_relays(files: dict[str, tuple[str | None, str]] = RELAYS) -> pd.DataFrame:
    """Rows of the archived relay pages: name, Arabic name, region, governorate, numbers."""
    out = []
    for f, (region, src) in files.items():
        p = Path(f)
        if not p.exists():
            continue
        if p.suffix == ".csv":
            lines = p.read_text(encoding="utf-8").splitlines()
            head = lines[0].split(",")
            d = pd.DataFrame([dict(zip(head, ln.split(",", 7), strict=False)) for ln in lines[1:]])
            for r in d.itertuples():
                out.append({"file": f, "source": src, "region": region, "name": r.label_en,
                            "name_ar": r.label_ar, "governorate": r.governorate_en,
                            "unit": r.unit_type, "pop_2022": int(r.population_2022)})  # fmt: skip
            continue
        text = re.sub(r'<td class="noviz">.*?</td>', "", p.read_text(encoding="utf-8"))
        for row in re.findall(r"<tr.*?</tr>", text, flags=re.S):
            c = [x for x in _cells(row) if x and x not in ("→", "...")]
            nums = [int(x.replace(",", "")) for x in c if re.fullmatch(r"\d{1,3}(,\d{3})+|\d+", x)]
            ar = next((x for x in c if re.search(r"[؀-ۿ]", x)), None)
            if not nums or ar is None:
                continue
            unit = next((x for x in c if x in ("Place", "Governorate", "City", "Town")), None)
            gov = c[c.index(unit) + 1] if unit == "Place" and c.index(unit) + 1 < len(c) else None
            reg = region or next((REGION_CODES[x] for x in c if x in REGION_CODES), None)
            out.append({"file": f, "source": src, "region": reg, "name": c[0], "name_ar": ar,
                        "governorate": gov, "unit": unit, "pop_2022": nums[-1],
                        "national": region is None})  # fmt: skip
    d = pd.DataFrame(out)
    if d.empty or "national" not in d:
        return d
    d["national"] = d.national.fillna(False).astype(bool)
    regional = {(int(p), ar_norm(a)) for p, a, n in zip(d.pop_2022, d.name_ar, d.national,
                                                       strict=True) if not n}  # fmt: skip
    dup = [n and (int(p), ar_norm(a)) in regional
           for p, a, n in zip(d.pop_2022, d.name_ar, d.national, strict=True)]  # fmt: skip
    return d[~pd.Series(dup, index=d.index)].reset_index(drop=True)


# ----------------------------------------------------------------------------- matching
def _pop_hint(row: pd.Series) -> float | None:
    """Best non-primary size hint of a place: its own official/derived figure, else the grid."""
    for c in ("population", "grid_population"):
        v = row.get(c)
        if v is not None and pd.notna(v) and float(v) > 0:
            return float(v)
    return None


def plausible(hint: float | None, total: int, band: tuple[float, float] = GUARD) -> bool:
    return hint is not None and band[0] <= hint / total <= band[1]


def match(
    reg: pd.DataFrame,
    univ: pd.DataFrame,
    cities: pd.DataFrame,
    cp2: pd.DataFrame,
    relays: pd.DataFrame | None = None,
    osm: pd.DataFrame | None = None,
    decisions: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """One record per primary city: tier, register row_key (or universe settlement to create),
    evidence and reason."""
    reg = reg.copy()
    reg["sk"] = reg.name_ar.map(ar_skeleton)
    reg["an"] = reg.name_ar.map(ar_norm)
    univ = univ.copy()
    univ["sk"] = univ.name_ar.map(ar_skeleton)
    univ["an"] = univ.name_ar.map(ar_norm)
    by_osm = {
        (t, int(i)): k
        for t, i, k in zip(reg.osm_type, reg.osm_id, reg.row_key, strict=True)
        if pd.notna(i)
    }
    totals = cities.total.value_counts()
    relays = read_relays() if relays is None else relays
    if osm is None and OSM_PLACES.exists():
        osm = read_osm_places()
    recs: dict[str, dict[str, Any]] = {}
    claimed_rows: dict[str, str] = {}
    claimed_sids: set[str] = set()

    def take(city: str, total: int, tier: str, row_key: str | None, sid: str | None, ev: str):
        recs[city] = {"city": city, "total": total, "tier": tier, "row_key": row_key,
                      "settlement_id": sid, "evidence": ev, "reason": None,
                      "region_hint": None}  # fmt: skip
        if row_key:
            claimed_rows[row_key] = city
        if sid:
            claimed_sids.add(sid)

    def reg_for_sid(sid: str) -> str | None:
        u = univ[univ.settlement_id == sid]
        if u.empty:
            return None
        u = u.iloc[0]
        if pd.notna(u.osm_id) and (u.osm_type, int(u.osm_id)) in by_osm:
            return by_osm[(u.osm_type, int(u.osm_id))]
        near = reg[
            (reg.region == u.region)
            & (haversine_km(reg.lat, reg.lon, u.lat, u.lon) <= NAME_KM)
            & (reg.name_en.map(key_skeleton) == key_skeleton(u.name_en))
        ]
        return near.row_key.iloc[0] if len(near) == 1 else None

    # judgement decisions (screening/primary_match_decisions.yaml)
    if decisions is None and DECISIONS.exists():
        decisions = yaml.safe_load(DECISIONS.read_text(encoding="utf-8"))
    dec = decisions or {}
    for c in cities.itertuples():
        d = (dec or {}).get(c.name)
        if d is None:
            continue
        if "unplaced" in d:
            recs[c.name] = {"city": c.name, "total": c.total, "tier": None, "row_key": None,
                            "settlement_id": None, "evidence": None,
                            "reason": f"judgement: {d['unplaced']}",
                            "region_hint": None}  # fmt: skip
            continue
        key = (d["osm_type"], int(d["osm_id"]))
        u = univ[(univ.osm_type == key[0]) & (univ.osm_id == key[1])]
        sid = u.settlement_id.iloc[0] if len(u) == 1 else None
        take(c.name, c.total, "judgement", by_osm.get(key), sid, d["evidence"])
        recs[c.name]["pop_type"] = d.get("pop_type", "derived")
        if by_osm.get(key) is None and sid is None:
            # an OSM place outside the register and the R1a universe (INTEGRATE_R2 item 1)
            o = osm[(osm.osm_type == key[0]) & (osm.osm_id == key[1])] if osm is not None else []
            if len(o) != 1:
                raise ValueError(f"judgement for {c.name}: OSM {key} not in the place extracts")
            recs[c.name]["osm"] = o.iloc[0].to_dict()
    # tier 1: CP2 matches
    m = cp2.set_index("city")
    for c in cities.itertuples():
        sid = m.settlement_id.get(c.name) if c.name in m.index else None
        if isinstance(sid, str) and c.name not in recs:
            take(c.name, c.total, "cp2", reg_for_sid(sid), sid, f"CP2 tier: {m.tier[c.name]}")
    # tier 2: sweep wrote the primary figure
    for c in cities.itertuples():
        if c.name in recs or totals[c.total] > 1:
            continue
        hit = reg[(reg.pop_source == PRIMARY_SRC) & (reg.population == c.total)]
        hit = hit[~hit.row_key.isin(claimed_rows)]
        if len(hit) == 1:
            take(c.name, c.total, "sweep", hit.row_key.iloc[0], None,
                 f"sweep wrote {PRIMARY_SRC} {c.total:,} on {hit.name_en.iloc[0]}")  # fmt: skip

    def skeleton_cands(sk: str, region: str | None) -> list[tuple]:
        """Unclaimed places whose Arabic skeleton is `sk` (in `region` if given)."""
        rows = []
        for frame, key in ((reg, "row_key"), (univ, "settlement_id")):
            cand = frame[frame.sk == sk]
            if region:
                cand = cand[cand.region == region]
            for _, x in cand.iterrows():
                if key == "row_key" and x.row_key in claimed_rows:
                    continue
                if key == "settlement_id" and x.settlement_id in claimed_sids:
                    continue
                rk = x.row_key if key == "row_key" else reg_for_sid(x.settlement_id)
                if rk is not None and rk in claimed_rows:
                    continue
                sid = None if key == "row_key" else x.settlement_id
                rows.append((rk, sid, x.name_ar, x.region, _pop_hint(x)))
        return list({(r[0] or r[1]): r for r in rows}.values())  # a place may be in both frames

    def unmatched(c: Any, why: str, ev: str | None = None, region: str | None = None) -> None:
        recs[c.name] = {"city": c.name, "total": c.total, "tier": None, "row_key": None,
                        "settlement_id": None, "evidence": ev, "reason": why,
                        "region_hint": region}  # fmt: skip

    # tier 3: relay bridge (identical figure in an archived Census 2022 relay page): the relay
    # gives the Arabic name and the region; exact Arabic name first, then the Arabic skeleton
    relay_region: dict[str, str] = {}
    for c in cities.itertuples():
        if c.name in recs or totals[c.total] > 1 or relays.empty:
            continue
        rl = relays[relays.pop_2022 == c.total]
        if len(rl) != 1:
            continue
        rl = rl.iloc[0]
        an, region = ar_norm(rl.name_ar), rl.region
        relay_region[c.name] = region
        gname = rl.governorate if isinstance(rl.governorate, str) and rl.governorate else region
        ev = f"relay {rl.source}: {rl['name']} / {rl.name_ar} ({gname})"
        done = False
        for frame, key in ((reg, "row_key"), (univ, "settlement_id")):
            cand = frame[(frame.region == region) & (frame.an == an)]
            cand = cand[~cand[key].isin(claimed_rows if key == "row_key" else claimed_sids)]
            if len(cand) == 1:
                k = cand[key].iloc[0]
                rk, sid = (k, None) if key == "row_key" else (reg_for_sid(k), k)
                take(c.name, c.total, "relay bridge", rk, sid, ev + "; same Arabic name")
                done = True
                break
        if done:
            continue
        # same Arabic name in the full OSM place extract (suburb/neighbourhood included), inside the
        # relay's region; several -> the one inside the relay's governorate
        o = osm[(osm.region == region) & (osm.an == an)] if osm is not None else None
        gov = rl.governorate if isinstance(rl.governorate, str) and rl.governorate else None
        if o is not None and len(o) > 1 and gov:
            o = o[o.gov_name_en.map(key_skeleton) == key_skeleton(gov)]
        if o is not None and len(o) > 1:
            # place nodes first (the R2 rule); polygons only where no node carries the name
            nodes = o[o.osm_type == "node"]
            o = nodes if len(nodes) else o
        if o is not None and len(o) > 1:
            # A-r2-003: same name several times in the region -> the unique highest place rank
            rank = o.place.map(PLACE_RANK).fillna(9)
            top = o[rank == rank.min()]
            if len(top) == 1 and (rank > rank.min()).any():
                o = top
        if o is not None and len(o) == 1:
            o = o.iloc[0]
            k = (o.osm_type, int(o.osm_id))
            if k in by_osm and by_osm[k] not in claimed_rows:
                take(c.name, c.total, "relay bridge", by_osm[k], None, ev + "; same Arabic name")
            elif k not in by_osm:
                take(c.name, c.total, "relay bridge (OSM extract)", None, None,
                     f"{ev}; OSM {o.place} {o.osm_type}/{o.osm_id} {o.name_ar} in "
                     f"{o.gov_name_en} (point in polygon); not in the R1a universe")  # fmt: skip
                recs[c.name]["osm"] = o.to_dict()
            if c.name in recs:
                continue
        sk = ar_skeleton(rl.name_ar)
        ok = [r for r in skeleton_cands(sk, region) if plausible(r[4], c.total)]
        if len(sk) >= 3 and len(ok) == 1:
            rk, sid, ar, _, hint = ok[0]
            take(c.name, c.total, "relay bridge", rk, sid,
                 f"{ev}; Arabic skeleton '{sk}' = {ar}; size hint {hint:,.0f}")  # fmt: skip
        else:
            unmatched(c, f"relay places it in {region} ({gname}) as {rl.name_ar}; no "
                      "OSM place with that name in the governorate and "
                      f"{len(ok)} plausible places with its skeleton in the region",
                      ev, region)  # fmt: skip
    # tier 4: identical figure under another name (C-gastat-003/004)
    for c in cities.itertuples():
        if c.name in recs or totals[c.total] > 1:
            continue
        hit = reg[(reg.population == c.total) & (reg.pop_type == "official")]
        hit = hit[~hit.row_key.isin(claimed_rows)]
        if len(hit) == 1:
            h = hit.iloc[0]
            take(c.name, c.total, "identical figure", h.row_key, None,
                 f"{h.name_en} / {h.name_ar} holds {c.total:,} from {h.pop_source}")  # fmt: skip
    # tier 5: Arabic consonant skeleton of the export spelling, unique and plausible nationally
    shared = cities.name.map(key_skeleton).value_counts()
    for c in cities.itertuples():
        if c.name in recs:
            continue
        sk = key_skeleton(c.name)
        if len(sk) < 3:
            unmatched(c, f"skeleton '{sk}' too short to match safely (< 3 consonants)")
            continue
        if shared[sk] > 1:
            unmatched(c, f"skeleton '{sk}' is shared by {shared[sk]} primary cities")
            continue
        cands = skeleton_cands(sk, None)
        # no regional evidence: the size hint must fall in the back-test IQR (A-r2-002)
        ok = [r for r in cands if plausible(r[4], c.total, GUARD_NATIONAL)]
        if len(ok) == 1:
            rk, sid, ar, region, hint = ok[0]
            take(c.name, c.total, "arabic skeleton", rk, sid,
                 f"skeleton '{sk}' = {ar} ({region}); size hint {hint:,.0f}")  # fmt: skip
        elif ok:
            regs = sorted({r[3] for r in ok})
            unmatched(c, f"{len(ok)} plausible candidates ({', '.join(regs)})",
                      region=regs[0] if len(regs) == 1 else None)  # fmt: skip
        elif cands:
            near = ", ".join(f"{r[2]} ({r[3]}, {r[4] or 0:,.0f})" for r in cands[:3])
            unmatched(c, f"no plausible OSM place with skeleton '{sk}': {len(cands)} outside the "
                      f"size band ({near})")  # fmt: skip
        else:
            unmatched(c, f"no OSM place with skeleton '{sk}' (facility, farm area or name variant)")
    t = pd.DataFrame([recs[c] for c in cities.name])
    if "pop_type" not in t:
        t["pop_type"] = None
    t["pop_type"] = t.pop_type.where(
        t.pop_type.notna(),
        np.where(t.tier.isin(DERIVED_TIERS), "derived", np.where(t.tier.notna(), "official", None)),
    )
    t["status"] = np.select(
        [t.tier.isna(), t.row_key.notna()], ["unmatched", "matched"], default="created"
    )
    if "osm" not in t:
        t["osm"] = None
    return t


def create_row(u: pd.Series, city: str, total: int) -> dict[str, Any]:
    """A register row from a universe settlement (R1a fields), for a primary city match."""
    tier = u.get("nearest_metro_tier")
    return {
        "row_key": f"{u.region}:{u.osm_type}:{int(u.osm_id)}"
        if pd.notna(u.osm_id)
        else f"{u.region}:name:{u.name_en}@{u.lat:.3f},{u.lon:.3f}",
        "name_ar": u.name_ar if isinstance(u.name_ar, str) else u.name_en,
        "name_en": u.name_en if isinstance(u.name_en, str) else u.name_ar,
        "region": u.region,
        "governorate": u.governorate,
        "governorate_ar": u.governorate_ar,
        "is_governorate_centre": False,
        "osm_id": int(u.osm_id) if pd.notna(u.osm_id) else None,
        "osm_type": u.osm_type if pd.notna(u.osm_id) else None,
        "lat": float(u.lat),
        "lon": float(u.lon),
        "dist_existing_km": u.dist_existing_km,
        "road_min_existing": u.road_min_existing,
        "nearest_existing": u.nearest_existing,
        "dist_committed_km": u.dist_committed_km,
        "road_min_committed": u.road_min_committed,
        "nearest_committed": u.nearest_committed,
        "nearest_committed_station": None,
        "dist_metro_km": u.dist_metro_city_km,
        "road_min_metro": u.road_min_metro_city,
        "nearest_metro": u.nearest_metro_city,
        "nearest_metro_tier": int(tier) if pd.notna(tier) else None,
        "economic_roles": [],
        "terrain_class": None,
        "screened": True,
        "exclusion_reason": None,
        "sources": [PRIMARY_SRC, "S-r1a-505"],
        "fixture": False,
        "road_min_method": u.existing_method,
        "dist_method": "R1a settlement universe (great circle; OSRM skims where present)",
        "notes": f"created at the R2 merge for primary city {city} ({total:,}); roles and terrain "
        "not assessed (row from the R1a universe)",
    }


def create_row_osm(o: dict[str, Any], city: str, total: int) -> dict[str, Any]:
    """A register row from an OSM place node outside the R1a universe (suburb/neighbourhood)."""
    d = station_distances(o["lat"], o["lon"])
    return {
        "row_key": f"{o['region']}:{o['osm_type']}:{int(o['osm_id'])}",
        "name_ar": o["name_ar"],
        "name_en": o["name_en"] if isinstance(o["name_en"], str) else city,
        "region": o["region"],
        "governorate": o["gov_name_en"],
        "governorate_ar": re.sub(r"^محافظة\s+", "", o["gov_name_ar"] or ""),
        "is_governorate_centre": False,
        "osm_id": int(o["osm_id"]),
        "osm_type": o["osm_type"],
        "lat": o["lat"],
        "lon": o["lon"],
        **d,
        "road_min_existing": None,
        "road_min_committed": None,
        "dist_metro_km": None,
        "road_min_metro": None,
        "nearest_metro": None,
        "nearest_metro_tier": None,
        "economic_roles": [],
        "terrain_class": None,
        "screened": True,
        "exclusion_reason": None,
        "sources": [PRIMARY_SRC, "osm-gcc-places-extract-2026-10-14"],
        "fixture": False,
        "road_min_method": "pending skims",
        "dist_method": "haversine to the nearest intercity existing station (A-r1a-008) and "
        "committed stop (A-r1a-007), R2 merge",
        "notes": f"created at the R2 merge for primary city {city} ({total:,}); OSM place="
        f"{o['place']} (outside the R1a universe, which keeps city..hamlet); governorate by "
        "point in "
        "polygon; roles and terrain not assessed",
    }


def apply(reg: pd.DataFrame, t: pd.DataFrame, univ: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """Primary figure on every matched row; new rows for universe-only matches; change log."""
    reg = reg.copy()
    for col in ("primary_city", "primary_match_tier"):
        if col not in reg:
            reg[col] = None
    created = []
    for r in t[t.status == "created"].itertuples():
        if isinstance(r.osm, dict):
            row = create_row_osm(r.osm, r.city, int(r.total))
        else:
            row = create_row(univ[univ.settlement_id == r.settlement_id].iloc[0], r.city, r.total)
        if row["row_key"] in set(reg.row_key):
            raise ValueError(f"created row {row['row_key']} already exists")
        # the register's own governorate spelling (same region, same Arabic name key)
        same = reg[
            (reg.region == row["region"])
            & (reg.governorate_ar.map(ar_norm) == ar_norm(row["governorate_ar"]))
        ]
        if len(same):
            row["governorate"], row["governorate_ar"] = same.iloc[0][
                ["governorate", "governorate_ar"]
            ]
        created.append(row)
        t.loc[t.city == r.city, "row_key"] = row["row_key"]
    if created:
        reg = pd.concat([reg, pd.DataFrame(created)], ignore_index=True)
    log = []
    idx = reg.set_index("row_key").index
    if "pop_type" not in t:
        t = t.assign(pop_type=None)
    hit = t[t.row_key.notna()]
    grp = hit.groupby("row_key", sort=False).agg(
        total=("total", "sum"),
        city=("city", " + ".join),
        tier=("tier", "first"),
        pop_type=("pop_type", "first"),
    )  # a declared combination (CP2 combined_with, e.g. Alhufuf + Almubriz) holds the sum
    for r in grp.itertuples():
        i = int(np.flatnonzero(idx == r.Index)[0])
        old, old_src = reg.at[i, "population"], reg.at[i, "pop_source"]
        if pd.isna(old) or int(old) != int(r.total) or old_src != PRIMARY_SRC:
            log.append({"row_key": r.Index, "name_en": reg.at[i, "name_en"],
                        "name_ar": reg.at[i, "name_ar"], "primary_city": r.city,
                        "tier": r.tier, "previous": None if pd.isna(old) else int(old),
                        "previous_source": old_src, "previous_type": reg.at[i, "pop_type"],
                        "primary": int(r.total),
                        "diff_pct": None if pd.isna(old) or not old else
                        round(100 * (int(r.total) - float(old)) / float(old), 1)})  # fmt: skip
        reg.at[i, "population"] = int(r.total)
        reg.at[i, "pop_source"] = PRIMARY_SRC
        reg.at[i, "pop_year"] = 2022
        reg.at[i, "pop_type"] = r.pop_type if isinstance(r.pop_type, str) else "official"
        reg.at[i, "pop_source_status"] = "verified"
        reg.at[i, "primary_to_find"] = None
        reg.at[i, "pop_corroboration"] = None
        reg.at[i, "pop_corroboration_value"] = None
        reg.at[i, "tag_10k"] = int(r.total) >= TAG_10K
        reg.at[i, "tag_5k"] = int(r.total) >= TAG_5K
        reg.at[i, "primary_city"] = r.city
        reg.at[i, "primary_match_tier"] = r.tier
        src = list(reg.at[i, "sources"]) if reg.at[i, "sources"] is not None else []
        if PRIMARY_SRC not in src:
            reg.at[i, "sources"] = [PRIMARY_SRC, *src]
    # rows that carry a primary figure no city claims any more (a sweep or the pilot attached a
    # figure that a stricter tier gave to another row): flag, keep the figure, say so
    stray = reg[(reg.pop_source == PRIMARY_SRC) & reg.primary_city.isna()].row_key.tolist()
    claimed_cities = set(t[t.row_key.notna()].city)
    reg["primary_unclaimed"] = reg.row_key.isin(stray)
    for i in reg.index[reg.primary_unclaimed]:
        # its figure belongs to a city another row now holds: a duplicate of that place
        hit = t[(t.total == reg.at[i, "population"]) & t.city.isin(claimed_cities)]
        if len(hit) == 1:
            h = hit.iloc[0]
            reg.at[i, "screened"] = False
            reg.at[i, "exclusion_reason"] = (
                f"duplicate of {h.row_key} (primary city {h.city}, R2 merge); figure counted once"
            )
            reg.at[i, "notes"] = f"{reg.at[i, 'notes']} | previous population {int(h.total):,} "
            f"({PRIMARY_SRC}) moved to {h.row_key}"
            for c in ("population", "pop_source", "pop_year", "pop_type", "pop_source_status"):
                reg.at[i, c] = None
            reg.at[i, "tag_10k"], reg.at[i, "tag_5k"] = False, False
    return reg, log


@app.command()
def main(
    register: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--register"),
    universe: Path = typer.Option(UNIVERSE, "--universe"),
    cp2: Path = typer.Option(CP2_MATCHES, "--cp2"),
    run_dir: Path = typer.Option(Path("runs/r2/primary_match"), "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0, help="recorded in meta.json (matching is exact)"),
    out: Path | None = typer.Option(None, "--out", help="default: overwrite --register"),
) -> None:
    """Match the 271 primary cities to the register; write the register and the tables."""
    reg, univ = pd.read_parquet(register), pd.read_parquet(universe)
    cities, other = read_city_primary()
    t = match(reg, univ, cities, pd.read_csv(cp2))
    new, log = apply(reg, t, univ)
    region_of = new.set_index("row_key").region
    t["region"] = t.row_key.map(region_of)
    run_dir.mkdir(parents=True, exist_ok=True)
    t.to_csv(run_dir / "primary_cities.csv", index=False)
    pd.DataFrame(log).to_csv(run_dir / "changes.csv", index=False)
    summary = {
        "primary_cities": int(len(t)),
        "persons": int(t.total.sum()),
        "other_lt_5000": other,
        "by_status": {k: int(v) for k, v in t.status.value_counts().items()},
        "by_tier": {k: int(v) for k, v in t.tier.value_counts().items()},
        "unmatched_persons": int(t[t.status == "unmatched"].total.sum()),
        "unmatched_ge_10k": int(((t.status == "unmatched") & (t.total >= TAG_10K)).sum()),
        "changes": len(log),
        "unclaimed_primary_rows": int(new.primary_unclaimed.sum()),
        "register_rows": int(len(new)),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    new.drop(columns=[c for c in ("sk", "an") if c in new]).to_parquet(out or register, index=False)
    write_meta(run_dir, seed, {"register": str(register), "cp2": str(cp2)},
               {"step": "screening.primary_match", "summary": summary})  # fmt: skip
    typer.echo(json.dumps(summary))


if __name__ == "__main__":
    app()
