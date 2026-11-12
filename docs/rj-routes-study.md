> **Document version:** docs/rj-routes-study.md v1.1 | 6 Nov 2026 | Author: STUDY_RJ_FAMILIES (main track builder); §8 STUDY_RJ_SCORE | Status: draft

# Riyadh–Jeddah corridor study and all-families comparison layout

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Write "in the model, X changes by", never "will". Money is SAR billion, 2025 prices, from the cost register; every cost and time is a P10/P50/P90 range.

**Alignment limitation:** alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty (`docs/alignments.md` §0, §4).

**What this is.** A research and routing study requested by Tariq on 6 Nov 2026 (`prompts/STUDY_RJ_FAMILIES.md`). It is not a scored programme. The judge was not run, nothing is written into `runs/r6/top5/`, `runs/r7/`, the dashboard switcher or the R8 report, summaries, brief or figure index. S1, the committed Landbridge geometry, HHR, the interchange rules and the access model are unchanged. The Riyadh–Jeddah routes are **hypothetical (ours), user-proposed** (CP7-6): indicative engineering sketches, not designs. **Later (STUDY_RJ_SCORE, 6 Nov 2026):** the five sketches were scored by the frozen judge as Landbridge replacements; see section 8.

Run outputs (seed 1): `runs/study/families/`, `runs/study/rj/{align-s1, siting-s1, times-s1, costs-s1, legs-s1, summary-s1}/`. Reproduce:

```
uv run python -m study.families layout && uv run python -m study.families inventory && uv run python -m study.families map
uv run python -m study.rj corridors && uv run python -m study.rj route --seed 1 && uv run python -m study.rj sidecars --seed 1
uv run python -m study.rj markers && uv run python -m study.rj siting --seed 1
uv run python -m study.rj times --seed 1 && uv run python -m study.rj costs --seed 1 && uv run python -m study.rj legs --seed 1
uv run python -m study.rj summary --seed 1 && uv run python -m study.rj scenarios && uv run python -m study.rj maps --seed 1
```

Parameters: `cities/ksa/assumptions/rj_study.yaml` (assumptions A-rj-001…005 in `docs/study-rj/assumptions.md`; sources in `docs/sources/study-rj.csv`; both kept out of `docs/assumptions*.md` and `docs/sources/index.csv`, which feed the R8 report annexes). Sources: `docs/sources/study-rj.csv` (S-rj-001…033).

## 1. All-families comparison layout (S1 + S2 + S3 + S4 + S5)

`scenarios/study/all-families.yaml`, id `S1-S5-all-families`: **comparison layout, not the recommended programme**, and not an S6 search result. It is S1 as it stands (including the committed Landbridge sketch) plus every S2–S5 corridor of the R6_V3 library (`runs/r6/v3/library/library.json`, 73 base ids). Connectivity is neither a constraint nor an objective. The layout was not scored.

Inventory (`runs/study/families/inventory.json`):

| family | corridors | new route-km |
|---|---|---|
| S2 trunk gaps | 23 | 9,949.9 |
| S3 branches / spurs | 19 | 3,075.1 |
| S4 commuter belts | 20 | 1,935.8 |
| S5 station additions | 10 | 0 (stations on existing or committed lines) |
| **total drawn** | **72** | **14,960.9** |

- 72 of the 73 library ids are drawn. The 73rd, `S5-station_addition-jubail-two-stations`, is a CBA variant that combines two S5 additions already drawn. Drawing it too would place the same two stations twice.
- Route-km is a sum over corridors. Overlapping alternatives are each counted, so it is not a network length. For example, `S2-trunk_gap-riyadh-jeddah` (a library corridor) appears beside the committed Landbridge.
- Route-km for S2–S4 is the routed length under the frozen v1 weights (62 corridors).
- The Riyadh–Jeddah study routes in sections 3–6 are **not** in this layout. Adding them would draw two Riyadh–Jeddah trunks as one programme.

Map: `docs/study-rj/all-families-map.png`.

## 2. The announced Landbridge: what is published, what conflicts, what is not published

**Published (all secondary):**
- A new Riyadh–Jeddah line, delivered by SAR in phases to a 2034 target after PPP talks ended (S-059; S-rj-022, Arab News reporting the SRC CEO, 21 Jan 2026).
- Three named intermediate stations: Jumoum/Jamuma, Muwai/Moya and Dawadmi/Al-Doadmi (S-062; S-lb-018; MEED Projects profile updated Sep 2026, S-rj-027). No locations are given.
- That "Jamuma" is Al-Jumum is an owner statement (S-063), not a published SAR site.
- Passenger design speed 250 km/h, operating up to 220 km/h; freight design 140, operating 120 km/h (S-058, a 2011 trade article).
- The line is a **mixed passenger/freight** product.

**In conflict:**
- Length (C-002, open): 900 km (MEED, Jan 2026, S-054), 920 km (S-056), 950 km (S-055; Wikipedia infobox, S-rj-029) and 958 km (Wikipedia body, S-rj-029). MEED also gives about 1,500 km of new track for the whole Landbridge (S-057, S-rj-028), which is a programme total, not the Riyadh–Jeddah section.
- Makkah and Taif: a July 2017 news item, as cited on the MEED profile, names Mecca and Taif among the western cities (S-rj-031). The published three-stop list does not include them. This is uncertainty in the record. It is not evidence of an official via-Taif or via-Makkah alignment.

**Not published:** the track itself and the Riyadh and Jeddah terminal sites. Searches on 6 Nov 2026 found no official alignment, terminal sites or station sites (S-rj-030).

**How this study uses it.** The S1 Landbridge stays as it is. It is a **sketch through town-centroid proxies with the stated uncertainty**, not an official line. It is a great-circle chain of 874.3 km (Riyadh 0, Dawadmi 236.4, Muwai 588.3, Al-Jumum 819.5, Jeddah 874.3; `cities/ksa/lines/landbridge.yaml`), scaled to the announced 900 km by the route factor 1.029 (A-r4-rt-012). The Riyadh and Jeddah ends are placeholders (A-r1a-006, A-r4-acc-004).

For a like-for-like terrain comparison we also routed the same five proxies ourselves in the mixed class (1.25 % grade cap): **RJ-LB, 967.4 km**. That is longer than every published figure, for three reasons:
- the proxies are town centroids;
- the Riyadh–Dawadmi leg detours (ratio 1.20);
- the Muwai–Al-Jumum escarpment descent is developed at 1.25 %.

RJ-LB is our sketch, not the official alignment. As routed, the as-understood chain passes 20.7 km from `hhr:makkah` and 74.7 km from Taif (`runs/study/rj/summary-s1/summary.json`, offsets). It does not serve Taif or Makkah, and neither does the library's `S2-trunk_gap-riyadh-jeddah`. Al-Jumum is 24.45 km from `hhr:makkah`.

## 3. Hypothetical Riyadh–Jeddah alternatives (user-proposed; terrain-routed)

Every route was routed by `network.align.route_corridor` under the **frozen v1 weights** (hash `2b718ecb…`, checked before and after, recorded in every `meta.json`) on the corrected `existing.geojson`/`hhr.geojson`. All five profiles are feasible at their class cap. `rail.hhr_check.stitch_jumps` finds no stitched chords in any of them.

Terminals are the same Landbridge placeholders for every route, so the ends are comparable. A waypoint is a routing timing point (no stop, dwell or station cost; A-rj-002).

| id | stops | class (cap) | routed km | straight end to end | ratio | tunnel km | viaduct km | earthworks km | ruling grade | min curve speed (km/h) |
|---|---|---|---|---|---|---|---|---|---|---|
| RJ-LB | Riyadh, Dawadmi, Muwai, Al-Jumum, Jeddah | mixed (1.25 %) | 967.4 | 844.2 | 1.106 | 24.9 | 25.9 | 106.3 | 1.25 % | 100 |
| RJ-A speed-oriented | Riyadh, Jeddah | hsr (2.5 %) | 887.2 | 844.2 | 1.051 | 14.7 | 17.8 | 132.7 | 2.50 % | 230 |
| RJ-B via Taif, north-around | Riyadh, Taif, Jeddah | hsr (2.5 %) | 965.0 | 844.2 | 1.085 | 21.9 | 21.1 | 147.6 | 2.50 % | 110 |
| RJ-C1 via Taif + gateway SW | Riyadh, Taif, gateway SW, Jeddah | hsr (2.5 %) | 975.9 | 844.2 | 1.104 | 25.1 | 25.9 | 148.4 | 2.50 % | 80 |
| RJ-C2 via Taif + gateway NW | Riyadh, Taif, gateway NW, Jeddah | hsr (2.5 %) | 967.4 | 844.2 | 1.084 | 24.3 | 22.2 | 154.5 | 2.50 % | 110 |

Source: `cities/ksa/alignments-study/<id>.json` (`length_km`, `straight_km_end_to_end`, `detour_ratio`, `tunnel_km`, `viaduct_km`, `earthworks_km`, `formation_max_grade`, `min_curve_kmh`). The hsr class has R_min 7,000 m at 300 km/h; the mixed class has 4,861 m at 250 km/h (A-align-012). The minimum curve speeds below design are local sketch curves; running times include them (section 5).

**Offsets from the towns served** (nearest path point, km; `summary.json` offsets):
- Every stop is a leg end, so its offset is 0.
- RJ-A passes 0.5 km from the Muwai proxy and 0.7 km from the Al-Jumum proxy, but calls at neither. It passes 89.5 km from Dawadmi and 73.5 km from Taif.
- RJ-B and RJ-C2 pass about 1 km from Al-Jumum without a stop. RJ-C1 passes 34.7 km from it.

**The Taif escarpment** (`runs/study/rj/legs-s1/legs.csv`). Taif is a high city on the Hijaz escarpment: 1,879 m (S-rj-032, secondary), against 1,671 m of Copernicus GLO-30 ground at the Taif anchor point used here. Makkah is at 277 m (S-rj-033).

On the 2.5 % cap the descent from Taif is developed over a much longer path than the straight line:

| route | Taif leg | straight km | routed km | ratio | tunnel km | viaduct km | ground, m |
|---|---|---|---|---|---|---|---|
| RJ-B, RJ-C2 | Taif → north waypoint | 61.9 | 91.4 | 1.48 | 16.2 | 14.8 | 1,671 → 447 |
| RJ-C1 | Taif → south waypoint | 62.0 | 117.0 | 1.89 | 19.5 | 20.5 | 1,671 → 236 |

For comparison, the as-understood Landbridge chain also crosses the escarpment, between Muwai and Al-Jumum. At the mixed 1.25 % cap that leg has 21.5 km of tunnel and 23.1 km of viaduct.

A mixed passenger/freight line via Taif would need the 1.25 % cap (section 6). It was not routed.

All legs:

| route | leg | straight km | routed km | ratio | tunnel km | viaduct km | ground level start → end (max), m |
|---|---|---|---|---|---|---|---|
| RJ-LB | riyadh → dawadmi | 236.4 | 283.9 | 1.20 | 2.5 | 2.7 | 592 → 978 (978) |
| RJ-LB | dawadmi → muwai | 351.9 | 374.2 | 1.06 | 0.0 | 0.0 | 977 → 971 (1060) |
| RJ-LB | muwai → al-jumum | 231.2 | 241.9 | 1.05 | 21.5 | 23.1 | 972 → 206 (1072) |
| RJ-LB | al-jumum → jeddah | 54.8 | 67.4 | 1.23 | 0.9 | 0.1 | 205 → 13 (219) |
| RJ-A | riyadh → jeddah | 844.2 | 887.2 | 1.05 | 14.7 | 17.8 | 592 → 13 (1102) |
| RJ-B | riyadh → taif | 745.8 | 776.1 | 1.04 | 4.3 | 5.2 | 592 → 1671 (1675) |
| RJ-B | taif → wp-north | 61.9 | 91.4 | 1.48 | 16.2 | 14.8 | 1671 → 447 (1675) |
| RJ-B | wp-north → jeddah | 81.7 | 97.5 | 1.19 | 1.4 | 1.1 | 441 → 13 (483) |
| RJ-C1 | riyadh → taif | 745.8 | 776.1 | 1.04 | 4.3 | 5.2 | 592 → 1671 (1675) |
| RJ-C1 | taif → wp-south | 62.0 | 117.0 | 1.89 | 19.5 | 20.5 | 1671 → 236 (1692) |
| RJ-C1 | wp-south → gateway-sw | 26.2 | 26.5 | 1.01 | 1.0 | 0.2 | 237 → 142 (309) |
| RJ-C1 | gateway-sw → jeddah | 50.1 | 56.3 | 1.12 | 0.3 | 0.0 | 142 → 13 (185) |
| RJ-C2 | riyadh → taif | 745.8 | 776.1 | 1.04 | 4.3 | 5.2 | 592 → 1671 (1675) |
| RJ-C2 | taif → wp-north | 61.9 | 91.4 | 1.48 | 16.2 | 14.8 | 1671 → 447 (1675) |
| RJ-C2 | wp-north → gateway-nw | 52.2 | 64.2 | 1.23 | 2.3 | 1.8 | 441 → 183 (483) |
| RJ-C2 | gateway-nw → jeddah | 33.0 | 35.8 | 1.08 | 1.5 | 0.4 | 181 → 13 (366) |

## 4. Makkah siting study

**Constraint, stated as siting.** A through Riyadh–Jeddah service must keep its through track, and any through station, outside the Haram boundary, so that every ticketed passenger can complete the journey. HHR already serves Makkah: `hhr:makkah` is at 21.417656 N, 39.788532 E (Ar Rusayfah, inside the city). A Makkah-area call, if there is one, is therefore a gateway outside the boundary with an interchange to HHR. HHR stays the branch into Makkah, and city access remains on the existing HHR. No through station and no through track is placed inside the boundary. A-station-001 applies: no main station is placed on airport land. Neither gateway is on airport land.

**Boundary data.** No complete official open GIS boundary was found. About 1,104 boundary markers are reported in total, with maps in a 1433 AH Makkah History Centre atlas that is not an open GIS layer (S-rj-002, unverified search summary).

This study therefore uses the **49 marker boards mapped in OpenStreetMap** (`boundary=marker`, named as Haram-boundary boards in Arabic). They are extracted with osmium from the registered GCC extract (S-rj-001; `cities/ksa/alignments-study/haram_markers.geojson`, manifest row `osm-haram-markers-extract-2026-10-14`, ODbL). They cover:
- the north, the Shara'i/north-east, Arafat, the Taif (Al-Awali) road, the south and the Al-Laith road;
- the old Jeddah road at Al-Shumaisi (Al-Hudaybiyah) and the Jeddah expressway;
- two boards where **HHR crosses the boundary**, at 21.3403 N, 39.6479 E, which is 17.1 km along HHR from `hhr:makkah`.

**Coordinate precision:** these are OSM point positions of roadside boards (metres to tens of metres). A board marks where a road crosses the boundary, not the line between boards. The 49 boards are a road-crossing subset of the reported total. **No polygon is drawn.**

**Check (A-rj-004).** Within 45 km of the Masjid al-Haram point, every through-track point must be farther from the centre than every marker within ±15° of its bearing, plus a 2 km clearance. Where a bearing sector holds no marker, the two bracketing markers by bearing are used instead, and those points are reported separately. Results (`runs/study/rj/siting-s1/siting.json`):

| route | min distance from through track to a marker (km) | min sector margin (km) | points checked within 45 km | bracket-checked | not verifiable | stitched chords | outside |
|---|---|---|---|---|---|---|---|
| RJ-LB | 12.917 | 13.217 | 676 | 0 | 0 | 0 | True |
| RJ-A | 13.91 | 14.682 | 678 | 0 | 0 | 0 | True |
| RJ-B | 13.043 | 13.406 | 893 | 0 | 0 | 0 | True |
| RJ-C1 | 4.987 | 2.917 | 1127 | 98 | 0 | 0 | True |
| RJ-C2 | 8.937 | 7.016 | 1005 | 0 | 0 | 0 | True |

Every route's through track and every stop are outside the sourced markers. None needed the "not verifiable" fallback.

RJ-C1 has 98 points in bearing gaps between marker clusters, east and south of the city. They were checked against the bracketing markers. There the track runs 21–36 km from the centre, against markers at 12–15 km.

Station sites:

| site | distance to nearest marker board | HHR km from `hhr:makkah` | note |
|---|---|---|---|
| gateway SW (21.324792 N, 39.593409 E; on HHR) | 5.3 km | 23.1 | 6.0 km of HHR beyond the HHR boundary board |
| gateway NW (21.476317 N, 39.482905 E; on HHR near Bahrah) | 17.8 km | 45.5 | — |
| Al-Jumum (announced stop, proxy) | 17.7 km | not on HHR | 24.45 km from `hhr:makkah` |

Sources: `siting.json` `stations` and `hhr_km_from_makkah`; A-rj-003.

**Siting recommendation (siting only; not a recommendation to build).** If a Makkah-area call is wanted on a through Riyadh–Jeddah alignment, the gateway should sit on the HHR alignment outside the boundary, with the through track continuing to Jeddah outside the boundary and HHR remaining the branch into Makkah. The two sites routed here bracket the choice:
- **SW site.** On HHR about 6 km beyond the HHR boundary board, 23.1 km along HHR from `hhr:makkah`. It gives the shortest HHR link, but it needs the south-around descent from Taif (RJ-C1).
- **NW site.** Near Bahrah, 45.5 km along HHR, with a wider clearance (17.8 km). It sits on the shorter north-around route (RJ-C2).

Either site needs a new HHR stop to make the interchange. That stop is not modelled: the interchange rules and the access model are unchanged (A-r4-acc-004).

The announced Al-Jumum site is outside the boundary but has no HHR interchange.

Figure: `docs/study-rj/rj-haram-siting.png`, "Through Riyadh–Jeddah alignments relative to the Haram boundary (siting constraint)".

## 5. Travel-time envelope

**Method.** The R4 running-time model (`access.running_time`: acceleration, cruise, braking, dwell by station class, UIC recovery) runs on each routed alignment. Station km-posts are chainages on the routed path. Curve limits use v = √(R(E+I)/11.8) on the radius of the joined path (A-align-012), so waypoint joins count. The result is multiplied by the generic timetable factor exactly as `network.evaluate` does for hypothetical corridors (A-r4-rt-011, `runs/access/running_time/factors-s1/factors.json`): P10 / P50 / P90 = kinematic × 1.164 / 1.281 / 2.134.

Grades are not in the model (A-r4-rt-007); the timetable factor stands in for that. No new formula is used. Output: `runs/study/rj/times-s1/times.csv`, with per-stop minute costs in `stop_costs.csv`.

**Speed classes (each sourced; test records are not design cases):**

| class | value | source | used here |
|---|---|---|---|
| Landbridge-class | 220 km/h operating / 250 km/h design | S-058 (secondary); S-054; A-r4-rt-003, A-r4-rt-012 | yes (`intercity_250` stock) |
| HHR-class | 300 km/h in service (320/360 design in secondary sources, C-004 open) | S-cp2-501; S-003 | yes (`hsr_talgo350`) |
| Shinkansen (Tohoku E5/H5), TGV (LGV Est), ICE 3 | 320, 320, 300 km/h in Germany | S-rj-015, S-rj-016, S-rj-017 | context (same band as 300) |
| fastest commercial steel-wheel | 350 km/h, China CR400 Fuxing (Beijing–Shanghai) | S-rj-010 (secondary) | yes (`hsr_talgo350` kinematics, vmax 350; A-rj-005) |
| Shanghai Maglev (reference only) | 431 km/h commercial until May 2021, 300 km/h since; about 30 km airport line | S-rj-011, S-rj-021 (secondary) | no |
| Chuo Shinkansen SCMaglev (reference only) | 505 km/h planned; not open, Tokyo–Nagoya at least 2036 | S-rj-013, S-rj-023 (secondary) | no |
| SCMaglev L0 test (reference only) | 603 km/h manned test, 21 Apr 2015, Yamanashi test line; not in passenger service | S-rj-012, S-rj-024 (secondary) | no |
| steel-wheel test record (reference only) | 574.8 km/h, French TGV, 3 Apr 2007 (the V150 run; the cited page does not name the train) | S-rj-014 (secondary) | no |

Japan is the usual guess for the fastest trains. Japan holds the overall rail speed record with a maglev on a test line (603 km/h). In passenger service, its Shinkansen top speed of 320 km/h sits in the same band as TGV and ICE 3. The fastest steel-wheel trains in commercial service run at 350 km/h in China.

**Bounds.** On the announced 900 km (S-054), Tariq's lower bound of 2 hours needs about 450 km/h *average*, including acceleration, braking and any stops. That is maglev territory, above every commercial steel-wheel service listed above. It becomes less plausible again with intermediate stops or an escarpment crossing. His upper bound of 9 hours is about 100 km/h average. (900 / 2 = 450 and 900 / 9 = 100; `runs/study/rj/times-s1/air.json` `bounds_reference`.)

In the model, the fastest case (RJ-A at 350 km/h, non-stop) has a kinematic floor of 2:57 and a P10 of 3:27. No route and speed class reaches 2 hours even at its kinematic floor. Every P50 is inside the 2–9 h envelope. The P90 exceeds 9 h for the 220/250 km/h classes on the longer routes; that is the high timetable factor (2.134) at work.

**Air comparison.**
- Tariq's stated upper bound for a Riyadh–Jeddah flight is **1:50 airborne** (110 min).
- Airline figures of about 100–115 min appear only in search snippets: S-rj-018, **unverified/secondary**. A model-based 2 h 25 min estimate (S-rj-025) is not a timetable.
- The repo's air block-time model gives 30 + 851.6 km / 12 km per min = **101 min** (A-mode-029, airports from `economic_nodes.parquet`).

Air's advantage is line-haul: no rail case here comes close to 1:50 in-vehicle.

The fair comparison is **door-to-door**, city centre to city centre, using the existing access-model parameters unchanged:
- **Rail:** access 20 + expected wait (headway / 2, capped at 30) + in-vehicle + egress 20 min (A-mode-028, A-access-010, A-r4-acc-003 / A-demand-049 headways).
- **Air:** access 60 (including check-in and security) + block + egress 30 min (A-mode-028). This gives **3:11** with the block model and **3:20** with the 1:50 bound; the range over the A-mode-028 ranges is 2:41–3:50 (`air.json`).

Rail door-to-door P50 in the model:
- best case, RJ-A at 350 km/h: 4:57;
- RJ-A at 300 km/h: 5:29;
- the S1 Landbridge as R4 models it (250 km/h, non-stop): 6:17.

On this indicative basis, air stays ahead door-to-door on Riyadh–Jeddah in every rail case modelled. Rail's comparison rests on intermediate stops (Taif, a Makkah-area gateway, Dawadmi, Muwai, Al-Jumum) and on city-centre stations, not on line-haul speed. The terminal sites are placeholders, so the door-to-door minutes are indicative only.

All rows (non-stop = `riyadh – jeddah`; the others call at every listed stop):

| route | speed class (km/h) | stops called | routed km | kinematic floor | in-vehicle P10 / P50 / P90 (h:mm) | door-to-door P50 (h:mm) |
|---|---|---|---|---|---|---|
| RJ-LB | 220 | riyadh – dawadmi – muwai – al-jumum – jeddah | 967.4 | 5:07 | 5:58 / 6:34 / 10:56 | 7:44 |
| RJ-LB | 220 | riyadh – jeddah | 967.4 | 4:59 | 5:48 / 6:22 / 10:37 | 7:32 |
| RJ-LB | 250 | riyadh – dawadmi – muwai – al-jumum – jeddah | 967.4 | 4:37 | 5:23 / 5:55 / 9:52 | 7:05 |
| RJ-LB | 250 | riyadh – jeddah | 967.4 | 4:29 | 5:13 / 5:44 / 9:33 | 6:54 |
| RJ-A | 220 | riyadh – jeddah | 887.2 | 4:27 | 5:11 / 5:42 / 9:30 | 6:52 |
| RJ-A | 250 | riyadh – jeddah | 887.2 | 3:57 | 4:36 / 5:03 / 8:25 | 6:13 |
| RJ-A | 300 | riyadh – jeddah | 887.2 | 3:22 | 3:55 / 4:19 / 7:12 | 5:29 |
| RJ-A | 350 | riyadh – jeddah | 887.2 | 2:57 | 3:27 / 3:47 / 6:19 | 4:57 |
| RJ-B | 220 | riyadh – taif – jeddah | 965.0 | 4:57 | 5:46 / 6:21 / 10:35 | 7:31 |
| RJ-B | 220 | riyadh – jeddah | 965.0 | 4:55 | 5:43 / 6:18 / 10:30 | 7:28 |
| RJ-B | 250 | riyadh – taif – jeddah | 965.0 | 4:26 | 5:09 / 5:40 / 9:27 | 6:50 |
| RJ-B | 250 | riyadh – jeddah | 965.0 | 4:23 | 5:06 / 5:37 / 9:22 | 6:47 |
| RJ-B | 300 | riyadh – taif – jeddah | 965.0 | 3:51 | 4:29 / 4:56 / 8:13 | 6:06 |
| RJ-B | 300 | riyadh – jeddah | 965.0 | 3:49 | 4:26 / 4:53 / 8:08 | 6:03 |
| RJ-B | 350 | riyadh – taif – jeddah | 965.0 | 3:27 | 4:01 / 4:25 / 7:22 | 5:35 |
| RJ-B | 350 | riyadh – jeddah | 965.0 | 3:25 | 3:58 / 4:22 / 7:17 | 5:32 |
| RJ-C1 | 220 | riyadh – taif – gateway-sw – jeddah | 975.9 | 5:09 | 6:00 / 6:36 / 11:00 | 7:46 |
| RJ-C1 | 220 | riyadh – jeddah | 975.9 | 5:04 | 5:54 / 6:30 / 10:49 | 7:40 |
| RJ-C1 | 250 | riyadh – taif – gateway-sw – jeddah | 975.9 | 4:39 | 5:24 / 5:57 / 9:54 | 7:07 |
| RJ-C1 | 250 | riyadh – jeddah | 975.9 | 4:34 | 5:18 / 5:50 / 9:44 | 7:00 |
| RJ-C1 | 300 | riyadh – taif – gateway-sw – jeddah | 975.9 | 4:05 | 4:45 / 5:14 / 8:42 | 6:24 |
| RJ-C1 | 300 | riyadh – jeddah | 975.9 | 4:00 | 4:39 / 5:07 / 8:32 | 6:17 |
| RJ-C1 | 350 | riyadh – taif – gateway-sw – jeddah | 975.9 | 3:40 | 4:17 / 4:42 / 7:50 | 5:52 |
| RJ-C1 | 350 | riyadh – jeddah | 975.9 | 3:35 | 4:11 / 4:36 / 7:40 | 5:46 |
| RJ-C2 | 220 | riyadh – taif – gateway-nw – jeddah | 967.4 | 5:02 | 5:52 / 6:27 / 10:45 | 7:37 |
| RJ-C2 | 220 | riyadh – jeddah | 967.4 | 4:57 | 5:46 / 6:21 / 10:34 | 7:31 |
| RJ-C2 | 250 | riyadh – taif – gateway-nw – jeddah | 967.4 | 4:30 | 5:15 / 5:46 / 9:37 | 6:56 |
| RJ-C2 | 250 | riyadh – jeddah | 967.4 | 4:25 | 5:09 / 5:40 / 9:26 | 6:50 |
| RJ-C2 | 300 | riyadh – taif – gateway-nw – jeddah | 967.4 | 3:55 | 4:34 / 5:01 / 8:22 | 6:11 |
| RJ-C2 | 300 | riyadh – jeddah | 967.4 | 3:50 | 4:28 / 4:54 / 8:10 | 6:04 |
| RJ-C2 | 350 | riyadh – taif – gateway-nw – jeddah | 967.4 | 3:30 | 4:05 / 4:29 / 7:29 | 5:39 |
| RJ-C2 | 350 | riyadh – jeddah | 967.4 | 3:25 | 3:59 / 4:23 / 7:18 | 5:33 |
| S1-landbridge (R4 as-is) | 250 | riyadh – jeddah | 899.7 | 4:00 | 4:39 / 5:07 / 8:32 | 6:17 |
| S1-landbridge (R4 as-is) | 250 | riyadh – dawadmi – muwai – al-jumum – jeddah | 899.7 | 4:12 | 4:54 / 5:23 / 8:58 | 6:33 |

**Time penalty of the via-Taif routes for through Riyadh–Jeddah passengers.** Non-stop P50 minus RJ-A non-stop P50, same speed class (`summary.json`):

| route | 220 | 250 | 300 | 350 km/h |
|---|---|---|---|---|
| RJ-B | +35.7 | +33.9 | +33.9 | +35.1 |
| RJ-C1 | +47.2 | +47.1 | +48.1 | +48.7 |
| RJ-C2 | +38.3 | +36.4 | +35.3 | +35.4 |
| RJ-LB (mixed sketch) | +40.2 | +40.9 | — | — |

Each stop then adds its own minute cost on top (`stop_costs.csv`, P50): Taif about 3.0 min, gateway SW about 3.4 min, gateway NW about 3.6 min, and Dawadmi / Muwai / Al-Jumum 4.0 / 3.8 / 3.2 min at 250 km/h.

Chart: `docs/study-rj/rj-travel-times.png`.

## 6. Economic note (order of magnitude; no judge)

**Method.** Capex comes from the existing cost register through `costs.estimate`. The input is built by `network.evaluate.costing_input` from each routed alignment's measured terrain and structure shares (A-align-041/042/060), with double-track electrified (A-r4-cost-001/002). Waypoints are not stations.

Base capex is the register estimate. The uplifted figure applies the reference-class uplift of the line type (A-rcf-004; contingency is reported but not added, A-cost-008). Output: `runs/study/rj/costs-s1/capex.csv`. SAR billion, 2025 prices, undiscounted:

| route | line type | routed km | tunnel km | viaduct km | earthworks km | stations | base capex P10 / P50 / P90 | uplifted capex P10 / P50 / P90 | uplift |
|---|---|---|---|---|---|---|---|---|---|
| RJ-LB | mixed | 967.4 | 24.9 | 25.9 | 106.3 | 5 | 45.3 / 57.1 / 70.1 | 36.4 / 68.2 / 260.3 | U-capex-rail-sobc |
| RJ-A | hsr | 887.2 | 14.7 | 17.8 | 132.7 | 2 | 69.2 / 82.3 / 95.5 | 63.1 / 106.6 / 366.2 | U-capex-hsr-sobc |
| RJ-B | hsr | 965.0 | 21.9 | 21.1 | 147.6 | 3 | 77.9 / 93.2 / 108.9 | 71.0 / 120.7 / 417.3 | U-capex-hsr-sobc |
| RJ-C1 | hsr | 975.9 | 25.1 | 25.9 | 148.4 | 4 | 82.0 / 98.7 / 115.9 | 74.7 / 127.8 / 444.4 | U-capex-hsr-sobc |
| RJ-C2 | hsr | 967.4 | 24.3 | 22.2 | 154.5 | 4 | 80.8 / 97.0 / 113.8 | 73.7 / 125.7 / 436.1 | U-capex-hsr-sobc |

The public Landbridge cost figures (SR 100 bn programme vs USD 7 bn, C-001) are not used. RJ-LB is our terrain sketch priced in the mixed class with the rail uplift, so its gap to the hsr routes is mostly line type and uplift class, not terrain.

**Differences against RJ-A**, the speed-oriented hsr route (`summary.json`, base P50):
- **RJ-B via Taif:** +77.8 routed km, +7.2 km tunnel, +3.3 km viaduct; base P50 +10.9 bn SAR (+13.2 %).
- **RJ-C2** (via Taif, gateway NW): +80.2 km, +9.6 km tunnel, +4.4 km viaduct; +14.7 bn SAR (+17.9 %).
- **RJ-C1** (via Taif, gateway SW, south-around): +88.7 km, +10.4 km tunnel, +8.1 km viaduct; +16.3 bn SAR (+19.8 %).

Most of the extra structure is on the Taif descent leg (section 3).

**Trade-offs, without advocacy.**
- **Through passengers vs cities served.** In the model, the via-Taif routes add about 34–49 minutes to a non-stop Riyadh–Jeddah run and about 13–20 % to base capex. In exchange they put Taif (a metro anchor) and, for RJ-C1/C2, a Makkah-area gateway with an HHR interchange on the line. Whether that is worth it depends on demand between those pairs, which this study does not model. The layouts were not scored. (Section 8 now scores them as Landbridge replacements.)
- **Competition with air** is a door-to-door question (section 5), not "the train beats 1:50". On line-haul time air is ahead in every case here. Rail's case would rest on stations in city centres and on intermediate markets.
- **Different products.**
  - The announced Landbridge is a mixed passenger/freight line: passengers at about 250 km/h design / 220 km/h operating and freight at about 120 km/h operating (S-058). It is routed here at the 1.25 % mixed grade cap.
  - The via-Taif alternatives are routed as passenger-only high-speed lines at 2.5 %. That is a different product. A freight-capable line via Taif would need the 1.25 % cap. The minimum descent length would double: about 1,224 m of ground fall from Taif to the north waypoint needs about 49 km at 2.5 % and about 98 km at 1.25 %. It was not routed or priced.
- **Ranges.** The uplifted P90 of every route is roughly three to four times its P50. Every figure here is an order-of-magnitude screening range on a sketch alignment, not a budget.

## 7. Figures and files (study only; not in the R8 figure index)

- `docs/study-rj/all-families-map.png`: S1 plus all 72 library corridors (comparison layout, not the recommended programme).
- `docs/study-rj/rj-routes-map.png`: the five routed Riyadh–Jeddah sketches beside the S1 Landbridge sketch.
- `docs/study-rj/rj-haram-siting.png`: through Riyadh–Jeddah alignments relative to the Haram boundary markers.
- `docs/study-rj/rj-travel-times.png`: the travel-time envelope against 2 h, 9 h, the 1:50 airborne bound and air door-to-door.
- Study scenarios: `scenarios/study/all-families.yaml` and `scenarios/study/rj-{lb,a,b,c1,c2}.yaml`. Each RJ file is S1 plus one sketch, never combined.
- Alignments: `cities/ksa/alignments-study/` (README with credits; ODbL as for `cities/ksa/alignments/`).
- Replacement packages (section 8): `scenarios/study/replace-rj-{a,b,c1,c2,lb}.yaml` (S1* plus one sketch, with a `score:` block); runs in `runs/study/rj/score/`.

Every map credits © OpenStreetMap contributors (ODbL) and carries both labels.

## 8. Full-judge score (STUDY_RJ_SCORE, 6 Nov 2026)

**Labels: study sketch, not the recommended programme; synthetic demand, uncalibrated: scenario comparison, not a forecast.** Write "in the model, X changes by", never "will". Money is SAR million, 2025 prices, PV 2026 (A-cba-301); capex is undiscounted and uplifted.

**Alignment limitation:** alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty (`docs/alignments.md` §0, §4).

**What was scored (Tariq, 6 Nov 2026; `prompts/STUDY_RJ_SCORE.md`).** Five replacement packages, each with one sketch **instead of** the committed Landbridge:

- **S1\*** = S1 without the committed Landbridge: the existing lines (HHR, SAR North, SAR East) + the Riyadh Rail Link + the Saudi GCC section.
- Package = S1\* + one sketch (RJ-A, RJ-B, RJ-C1, RJ-C2 or RJ-LB), opened in 2030, the first R6 investment phase (construction start 2027, A-r6-002; A-rj-008). The announced Landbridge target is 2034 (S-rj-022, secondary).
- Every headline figure is an **increment versus S1\***, not versus published S1. These are not the same kind of increment as S6-L1…L5, which are extras on top of S1 with the Landbridge, so they are not tabled beside them.
- RJ-LB, our terrain-routed chain of the announced stops, is the like-for-like comparator. The public SR 100 bn / USD 7 bn figures (C-001) and the S1 great-circle sketch are not used.
- S1.yaml, the committed Landbridge and every published S1, L1–L5, S6-L6 and R8 figure are unchanged. The stacked files `scenarios/study/rj-*.yaml` (S1 plus a sketch drawn beside the Landbridge) stay as they were: not scored.

**How (judge unchanged).** Judge `v3-variants`, sha256 `d9fef643…` (verified intact before and after), seed 1, 10,000 draws, `--all-cases` (3 horizons × 5 rate cases × 3 population cases = 45 appraisal rows), the same adapter path as S6_L6_SCORE. Robust NPV = minimum over the population cases at P50 cost (A-r6-001).
- The Landbridge is omitted only inside the study entry `study/rj_judge.py`, and only when its study replacement marker (`study_rj_replace`) is present. There the judge's own S1 reference run is S1\*, so its increments are versus S1\*. Each run's `meta.json` records `landbridge_omitted: true` and the marker. Without the marker the entry changes nothing; a test checks that S1 and a published top-5 layout build byte-identical line lists with the Landbridge.
- The S1\* reference values come from the same judge runs (identical in all five; `runs/study/rj/score/_s1-star/s1_star.json`). No published S1 number is used as the S1\* baseline. S1\* in the model, 2050 medium: 14.45 M rail trips, 2,537 M passenger-km, HHR 11.04 M.
- Each sketch is scored on its routed alignment, not the straight end-to-end distance in the corridor files (RJ-A 887.2 km, not 844.2). Chainage, curve speed limits (recomputed on the joined path at the class line speed: hsr 300, mixed 250 km/h) and the generic timetable factor are the section 5 inputs; the judge's end-to-end in-vehicle minutes equal the section 5 P50 all-stop rows (RJ-A 259.1, RJ-B 296.1, RJ-C1 313.6, RJ-C2 301.1, RJ-LB 355.2; `inputs/check.json`). Costing is the section 6 cost run: electrified double track, the same spec and costing files, re-run with the judge's own `costs.estimate` and identical draw for draw.
- Service per class defaults (A-rj-009): hsr headway 60 min (A-r4-acc-003), mixed 120 min (A-demand-049, the Landbridge's own value), fare 0.30 SAR/km (A-mode-037).
- The two gateway stops had no station skim in the frozen judge; their rows were added with the judge's own skim method (A-rj-007; three existing stations recomputed match exactly).

**Access model.** The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not rail-graph interchanges.
- The RJ terminals use the same Riyadh and Jeddah town-centroid placeholders as `landbridge.yaml`. For scoring they take the Landbridge's A-r4-acc-004 placements of those placeholders (Jeddah with HHR Al-Sulaimaniyah, Riyadh with the SAR Riyadh station), so each sketch meets the network where the S1 Landbridge does (A-rj-006). The corridor files keep the placeholders; `access_network.yaml` is unchanged.
- The gateways have no HHR stop (not modelled; interchange rules unchanged), so in the model they are reached by road only.

### 8a. Score table (full judge v3; increments versus S1\*)

| sketch | class, routed km | robust NPV (min over population cases, at P50 cost) | NPV at P50 cost (low / medium / high) | NPV at P90 cost (low / medium / high) | BCR P10 / P50 / P90 (medium) | capex P10 / P50 / P90 |
|---|---|---|---|---|---|---|
| RJ-A | hsr, 887.2 | −84,338 | −84,338 / −80,264 / −76,158 | −271,115 / −266,885 / −262,869 | 0.05 / 0.23 / 0.80 | 63,119 / 106,611 / 366,237 |
| RJ-B | hsr, 965.0 | −102,845 | −102,845 / −99,291 / −95,644 | −317,096 / −313,231 / −309,235 | 0.04 / 0.18 / 0.62 | 71,028 / 120,699 / 417,314 |
| RJ-C1 | hsr, 975.9 | −100,036 | −100,036 / −95,547 / −90,850 | −329,422 / −324,563 / −319,466 | 0.05 / 0.23 / 0.79 | 74,707 / 127,770 / 444,346 |
| RJ-C2 | hsr, 967.4 | −99,640 | −99,640 / −95,247 / −90,685 | −324,058 / −319,625 / −314,767 | 0.05 / 0.22 / 0.77 | 73,681 / 125,690 / 436,091 |
| RJ-LB | mixed, 967.4 | −67,724 | −67,724 / −64,603 / −61,385 | −217,763 / −214,583 / −211,288 | 0.06 / 0.24 / 0.79 | 36,351 / 68,166 / 260,302 |

The robust case is the low population case for all five. Every NPV at P50 cost and at P90 cost is negative in every population case.

Demand, reach and loads (2050, WPP medium unless stated; there is no Landbridge in these packages, so the load reported is the sketch's own):

| sketch | added rail trips | added rail passenger-km (M) | sketch load | HHR load (vs S1\* 11.04 M) | five-metro 120-min gain (A-r6-007) | national reach 120, reported only (A-r6-104; S1\* 25.79 M) | CO2 PV P50 (medium) |
|---|---|---|---|---|---|---|---|
| RJ-A | +3.94 M | +3,351 | 3.63 M | 11.52 M (+0.48 M) | 0.00 M | +0.00 M (25.79 M) | 13,649 |
| RJ-B | +3.92 M | +2,970 | 4.08 M | 11.07 M (+0.04 M) | 0.00 M | +0.23 M (26.02 M) | 11,007 |
| RJ-C1 | +5.00 M | +3,623 | 7.28 M | 8.92 M (−2.11 M) | 0.09 M | +0.23 M (26.02 M) | 14,679 |
| RJ-C2 | +4.80 M | +3,552 | 5.46 M | 10.61 M (−0.43 M) | 0.00 M | +0.23 M (26.02 M) | 13,986 |
| RJ-LB | +3.45 M | +2,391 | 3.48 M | 11.27 M (+0.24 M) | 0.11 M | +0.31 M (26.10 M) | 11,107 |

Sources: `runs/study/rj/score/<package>/score.json` (the judge's own file is kept as `score.judge.json`), `score.csv`, `scorecard.csv`; national reach from `optimise/reach.py` run under the same marker. The five-metro gains are all in the Jeddah anchor (gateway SW for RJ-C1, Al-Jumum for RJ-LB). RJ-A adds no national reach because both of its stations sit at existing S1\* stations.

### 8b. Judge capex versus the section 6 register table

| sketch | judge capex P10 / P50 / P90 | section 6 uplifted P10 / P50 / P90 | judge base P50 | section 6 base P50 | largest gap |
|---|---|---|---|---|---|
| RJ-A | 63,119 / 106,611 / 366,237 | 63,119 / 106,609 / 366,240 | 82,316 | 82,315 | 3.0 |
| RJ-B | 71,028 / 120,699 / 417,314 | 71,028 / 120,697 / 417,318 | 93,193 | 93,193 | 3.8 |
| RJ-C1 | 74,707 / 127,770 / 444,346 | 74,707 / 127,768 / 444,350 | 98,653 | 98,653 | 4.5 |
| RJ-C2 | 73,681 / 125,690 / 436,091 | 73,681 / 125,687 / 436,095 | 97,047 | 97,046 | 3.9 |
| RJ-LB | 36,351 / 68,166 / 260,302 | 36,351 / 68,165 / 260,307 | 57,095 | 57,095 | 4.7 |

They match: both use the same 10,000 draws on the routed sidecars (the judge's cost run is identical draw for draw to `runs/study/rj/costs-s1/`). The only difference is the percentile rule. The judge takes the nearest draw (`economics.cba.pct`); `costs.estimate`'s summary, behind the section 6 table, interpolates. The largest gap is 4.7 SAR m (under 0.01 %).

### 8c. The via-Taif trade-off in the model (against RJ-A)

| sketch | robust NPV vs RJ-A | capex P50 vs RJ-A | added trips vs RJ-A | sketch load vs RJ-A | HHR vs S1\* | national reach 120 (reported only) | five-metro 120-min gain |
|---|---|---|---|---|---|---|---|
| RJ-B (via Taif) | −18,508 | +14,089 | −0.02 M | +0.45 M | +0.04 M | +0.23 M | 0.00 M |
| RJ-C2 (Taif + gateway NW) | −15,302 | +19,079 | +0.86 M | +1.83 M | −0.43 M | +0.23 M | 0.00 M |
| RJ-C1 (Taif + gateway SW) | −15,698 | +21,160 | +1.07 M | +3.65 M | −2.11 M | +0.23 M | +0.09 M |

- **Via Taif alone (RJ-B).** In the model, the Taif stop adds 0.23 M national reach (reported only), but total rail trips are flat against RJ-A (−0.02 M) and passenger-km fall by 381 M (Riyadh–Jeddah with the Taif stop is 37 minutes longer at the class speed, section 5). The extra capex is not recovered: robust NPV −18,508 against RJ-A.
- **With a Makkah-area gateway (RJ-C1/C2).** In the model, trips rise by 0.86–1.07 M against RJ-A and the sketch load by 1.83–3.65 M. HHR's 2050 load falls by 0.43 M (C2) and 2.11 M (C1) against S1\*. The shift by origin–destination pair was not decomposed. Robust NPV is 15.3–15.7 bn SAR below RJ-A, because the added capex (+19.1 to +21.2 bn at P50) outweighs the added benefits.
- **RJ-LB (mixed, announced-stop chain).** It has the least negative robust NPV (−67,724; +16,613 against RJ-A), with capex P50 38.4 bn below RJ-A and 0.49 M fewer added trips. Its gap to the hsr sketches is mostly product and cost class (mixed stock at 250 km/h, 120-min headway, the rail uplift; section 6), not terrain.
- **None of the five** has a positive NPV at P50 or P90 cost in any population case; BCR P50 is 0.18–0.24.

**Siting language (unchanged from section 4).** The through track of every sketch, and every through station, stays outside the Haram boundary; HHR remains the branch into Makkah, and a gateway on the HHR alignment would need a new HHR stop, which is not modelled.

**Files.** Scenarios `scenarios/study/replace-rj-{a,b,c1,c2,lb}.yaml`, each with a `score:` block matching `score.json`. Runs `runs/study/rj/score/<package>/` (`score.json`, `score.judge.json`, `meta.json` with judge hash, seed, layout hash, `landbridge_omitted`, git describe; `national_reach.json`; `scorecard.csv`; `inputs/`), `_s1-star/`, `_skims/`. Reproduce:

```
uv run python -m study.rj score-scenarios && uv run python -m study.rj score-inputs --seed 1
uv run python -m study.rj score-skims && uv run python -m study.rj score --seed 1 && uv run python -m study.rj score-summary --seed 1
```

Assumptions A-rj-006…009 (`docs/study-rj/assumptions.md`). Nothing from this section is in the R8 report, the summaries, the policy brief, the figure index or the dashboard.
