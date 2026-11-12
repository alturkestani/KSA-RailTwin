> **Document version:** docs/stations-siting.md v0.2 | 6 Nov 2026 | Author: FIX_HHR_JEDDAH (coordinator run on `main`); FIX_HHR_REROUTE (adoption, P1–P5 applied, generator check) | Status: reviewed

**Adopted by Tariq, 6 Nov 2026, in the words written.** A-station-001 is adopted; no station moved; no corridor re-scored for siting.

# Station siting: city stations and airport halts

This is a new file. Before it, `docs/` had no general station-siting note. Site records and research live in `docs/network.md` §2 (station-site research, CP2_PREP item 6), `rail/station_research.yaml` and `docs/geo-verify.md`, and those stay as they are. **Nothing was moved or re-scored in this run.** The rule below was proposed in FIX_HHR_JEDDAH and adopted by Tariq on 6 Nov 2026 in the words written (FIX_HHR_REROUTE); its text is unchanged.

## 1. Rule (A-station-001; adopted by Tariq, 6 Nov 2026)

In Tariq's words (6 Nov 2026):

> Do not colocate main stations on airport land. It is better that they are not colocated. Follow the pattern the Haramain already uses in this repo: a **city station** that serves the urban catchment and, when the line passes an airport, a **separate airport station on a short branch**. **An airport stop is an extra halt, not a substitute for the city station.**

He also said not to search for "best practice" for putting city stations on airport land. None was searched, and none is cited.

**Precedent (existing layer).** Haramain High Speed Railway, Jeddah:
- City station `hhr:jeddah` "Al-Sulimaniyah - Jeddah", class `major`, 21.517643 N, 39.245363 E (S-001; OSM way/485762503).
- Airport station `hhr:kaia` "Airport - Jeddah", class `airport`, 21.660504 N, 39.173818 E (S-001; OSM node/7227897402). It sits on the airport branch (S-004, secondary), which leaves the main line at a junction north of the city (21.6234465 N, 39.215395 E; OSM "Haramain high-speed rail (Jeddah Airport branch line)"). The branch is 6.69 km of OSM track (S-002 says 3.75 km; conflict C-fixhhr-001). `docs/network.md` §HHR geometry has the geometry.

**How to apply it (for any later station work; not applied here).** A main or intercity station goes on a city site inside the urban catchment of the town it serves. If the line passes an airport, a separate halt of class `airport` may be added on a short branch or spur, as an extra stop. The airport halt never replaces the city station, and a main station is not sited on airport land. "On airport land" in the inventory below means within 1.5 km of the airport point. The prompt says "of the terminal", but the repository holds no terminal positions, so the inventory uses the airport point, a stated proxy (§2).

## 2. Inventory (`uv run python -m rail.station_inventory`; `runs/fix-hhr/stations-inventory.csv`, gitignored)

**Scope.** 284 rows:
- all 153 stations of `cities/ksa/lines/stations.geojson`: existing 119, committed 10, historical 24;
- the 131 new stations of the 72 S2–S5 corridor files (`cities/ksa/corridors/*/*.yaml`), at 53 distinct sites. Host stations that point back to `stations.geojson` (39 rows) are not repeated;
- the S6 layouts (`scenarios/S6-L1…L5.yaml`), recorded in the column `in_s6` for each corridor station they include;
- `cities/ksa/candidates.parquet`, which supplies the served-town point of every corridor station sourced `register <row_key>`.

**Airports.** The 27 GACA airports in `cities/ksa/zones/economic_nodes.parquet` (S-cp1-100; positions from OSM aerodrome features, ODbL). These points are aerodrome centroids, not terminal buildings: HHR's KAIA station, which serves the terminal, is 2.65 km from the JED point.

**Served town.**
- Corridor stations: their register row (its point) or the metro reference point (A-screen-013).
- `stations.geojson` rows: the nearest OSM city or town in `settlements.parquet`. This is a proxy; metro stations get a district name.

**Flags.**
- `unplaced`: `located: false` or an `unlocated:*` or centroid-proxy method.
- `airport`: class `airport`.
- `on-airport-land`: within 1.5 km of an airport point.
- `city`: everything else.

`near_airport_5km` lists stations within 5 km of an airport point, for review.

| layer | city | airport | on-airport-land | unplaced | total |
|---|---|---|---|---|---|
| existing | 112 | 1 | 3 | 3 | 119 |
| committed / under procurement | 0 | 0 | 0 | 10 | 10 |
| historical | 24 | 0 | 0 | 0 | 24 |
| hypothetical (ours, S2–S5) | 131 | 0 | 0 | 0 | 131 |
| **total** | **267** | **1** | **3** | **13** | **284** |

The 15 stations within 5 km of an airport point and the 13 unplaced stations:

| station | layer | class | site (lat, lon) | placement | nearest airport (km) | flag |
|---|---|---|---|---|---|---|
| hhr:kaia (Airport - Jeddah) | existing | airport | 21.660504, 39.173818 | OSM node | JED 2.65 | airport (the precedent) |
| riyadh-metro-l4:airport-t1-2 | existing | terminal | 24.961066, 46.699022 | OSM node | RUH 0.79 | on-airport-land (metro airport station) |
| riyadh-metro-l4:airport-t3-4 | existing | intermediate | 24.955800, 46.702376 | OSM node | RUH 0.54 | on-airport-land (metro airport station) |
| riyadh-metro-l4:airport-t5 | existing | intermediate | 24.940534, 46.710499 | OSM node | RUH 2.08 | city by the distance rule (an airport metro station by name) |
| sar-north-passenger:al-qurayyat | existing | terminal | 31.420715, 37.289301 | OSM node | URY 1.39 | on-airport-land by the proxy: unverified (the airport point is an aerodrome centroid; no visual check made) |
| Bisha (5 corridors: S3 spur; S2 Abha–Khamis–Bisha, Al-Kharj–Bisha, Riyadh–Bisha, Taif–Bisha) | hypothetical | terminal | 20.000000, 42.600000 | register town point | BHH 3.14 | city |
| Rafha (S3 spur; S2 Arar–Hafar al-Batin) | hypothetical | terminal / intermediate | 29.632419, 43.517868 | register town point | RAH 2.80 | city |
| Jazan (S4 belts 090, 315; S2 Jazan–Najran) | hypothetical | terminal | 16.894719, 42.557976 | metro reference point (A-screen-013) | GIZ 2.59 | city |
| landbridge:jeddah "Jeddah (terminal site not published)" | committed | planned | 21.55044, 39.17424 | `town_centroid:osm:node/1933393717 (Jeddah city)`, `located: false`, `site_status: inferred`, `uncertainty_km` 13.9 | JED 14.77 | unplaced |
| landbridge:riyadh, :dawadmi, :muwai, :al-jumum | committed | planned | town centroids | `town_centroid:*`, `located: false` | RUH 35.59, DWD 26.71, TIF 164.50, JED 55.57 | unplaced |
| gcc-railway-ksa:kuwait-border, :dammam, :uae-border | committed | planned | town centroids | `town_centroid:*`, `located: false` | 30.8–246.5 | unplaced |
| riyadh-rail-link:north-south-connection, :eastern-network-connection | committed | planned | proxies | `unlocated:town_centroid_proxy:*` | RUH 12.87, 34.47 | unplaced |
| sar-east-freight-legacy:dammam-port, :riyadh-dry-port; sar-north-freight:ras-al-khair | existing | freight | published / adjacent-to-facility / town centroid | `located: false` as recorded | 34.5–121.9 | unplaced |

**Landbridge Jeddah.** The committed Landbridge Jeddah terminal is still the unpublished town-centroid placeholder at 21.55044 N, 39.17424 E. It carries `location_method` `town_centroid:osm:node/1933393717 (Jeddah city)`, `located: false`, `site_status: inferred` and `uncertainty_km` 13.9. The confidence field is as recorded in `stations.geojson`; its notes say "Haramain stations (Jeddah Central, airport) are existing and not Landbridge sites". On this scale it is `unplaced`. The point is 14.77 km from the JED airport point, 12.24 km from HHR's KAIA station and 8.21 km from HHR's Al-Sulaimaniyah station. It is therefore not on airport land, but the point is not a site.

**Hypothetical (ours) stations.** None of the 131 is an airport halt or within 1.5 km of an airport point. Three town points lie within 2.6–3.2 km of an airport point: Bisha, Rafha and Jazan. They are register or metro reference points, not chosen sites. None of the stations in an S6 layout is within 5 km of an airport point; the nearest is the Al-Hawiyah station of S4 Makkah belt 045, at 5.98 km from the Ta'if airport point (S6-L4, S6-L5).

## 3. Proposals P1–P5 (written in FIX_HHR_JEDDAH; applied as written by FIX_HHR_REROUTE, §4)

The rule would affect these stations. For each, the options are (a) keep, (b) move to a city site, (c) add a separate airport halt on a branch. The rescoring each option would need is listed.

| # | station(s) | why | options | rescoring if (b) or (c) |
|---|---|---|---|---|
| P1 | Landbridge Jeddah (committed, unplaced) | the only committed terminal in a city with an airport; its site is not published, and press items about airport stations are unverified and not used | (a) keep the placeholder until SAR publishes a site (recommended by the rule: no site is invented); when a site is published, check it against the rule. (b) and (c) are not ours to choose for a committed line: a published site replaces the placeholder | S1 baseline (committed programme) and so every scenario: R3/R4 demand and the rail graph (Jeddah transfer to HHR), R4 access (Jeddah isochrones), R5 every CBA case against S1, R6 judge back-test and layouts, R7/R8 figures |
| P2 | Bisha, Rafha, Jazan (hypothetical town points 2.6–3.1 km from an airport point) | not on airport land; listed because a later site search near these towns should apply the rule | (a) keep (the town point is the city side); (b) not needed; (c) an airport halt only if a corridor is taken forward and air–rail access is wanted | per corridor: R4_ALIGN routing of the corridor, R4 running time and access, R5 CBA cases `CBA-S2/S3/S4-*` for the corridors listed above. None is in S6-L1…L5, so R6/R7 only if a layout gains them |
| P3 | sar-north-passenger:al-qurayyat (existing) | 1.39 km from the URY aerodrome point by the proxy | (a) keep: existing stations are facts, not our choice. The rule does not apply to existing stations; a visual check of whether the station is on airport land is open | none (existing layer) |
| P4 | Riyadh Metro L4 airport stations (existing) | metro stations serving the terminals | (a) keep: existing, and urban metro airport stations are outside a rule about intercity main stations | none |
| P5 | Future station additions near airports (rule for R6+ and any re-run of `screening.corridors` station additions, A-corr-011) | the generator places S5 stations at register town points and could later snap to a line passing an airport | adopt A-station-001 as a generator check: reject a main station within 1.5 km of an airport point; allow an `airport` class halt only as an additional stop on a branch | `screening.corridors` re-run → S5 set; then R4_ALIGN, R5, R6 for any changed corridor |

No station in the current S2–S5 sets or S6 layouts would have to move under the rule. The decision for Tariq is (1) whether to adopt A-station-001, and (2) P1: keep the Landbridge Jeddah placeholder until a published site exists.

## 4. Applied (FIX_HHR_REROUTE, 6 Nov 2026)

Tariq adopted A-station-001 and P1–P5 as written. **A-station-001 adopted; no station moved; no corridor re-scored for siting.**

- **P1.** Landbridge Jeddah keeps the town-centroid placeholder (21.55044, 39.17424; `located: false`) until SAR publishes a site, which will then be checked against the rule. Not moved.
- **P2.** Bisha, Rafha and Jazan stay town points. Not moved.
- **P3.** Al-Qurayyat (existing) is kept. The visual check of whether the station is on airport land is still open.
- **P4.** The Riyadh Metro airport stations (existing) are kept.
- **P5.** The rule is now a check in `screening.corridors` (`siting_check`, called by `generate` after the R5 exclusions; airport points from `cities/ksa/zones/economic_nodes.parquet`; threshold `rail.station_inventory.ON_AIRPORT_KM` = 1.5 km).
  - Every station the generator adds (any station not taken from `stations.geojson`, and not of class `airport`) is tested against the airport points.
  - A **station addition (S5)** whose new station lies on airport land is **refused** and recorded as a decision row.
  - In the other families (S2–S4), such a station is **flagged** in a `siting_flags` field and recorded as a decision row, but not moved and not dropped. Dropping a terminal would remove a corridor, which would be re-scoring for siting, and that is outside this run.
  - Existing and committed stations (P3, P4) and `airport`-class halts pass. The generator creates no `airport`-class stations. The check does not test whether an airport halt sits on a branch.
  - Tests: `tests/test_fix_hhr_reroute.py` (a fixture station on airport land is refused in S5 and flagged in S4; existing and airport stations pass; the live corridors are unaffected).
  - With the check in place, `screening.corridors generate` reproduces every corridor YAML, `decisions.csv` and S2–S5 byte for byte. The closest generator-added station to an airport point is 2.59 km away.
  - The line is also in the `corridor-generator` skill.

