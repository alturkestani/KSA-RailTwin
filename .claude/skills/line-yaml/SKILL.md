---
name: line-yaml
description: Schema and validation for line and timetable YAML files under cities/ksa/lines/ and cities/ksa/corridors/ (identity, layer, source and date, stations with km-posts and coordinates, design speed, stopping patterns, headways, sampled fares, running-time model parameters). Use when creating, editing or reading any rail line, existing, committed or hypothetical.
---
> **Document version:** skills/line-yaml/SKILL.md v1.2 | 6 Nov 2026 | Author: coordinator; FIX_HHR_JEDDAH (station siting, branch parts); FIX_HHR_REROUTE (A-station-001 adopted) | Status: active

# Line YAML

Validated by `uv run python -m rail.lines validate <file or dir>` against `LineSpec` in `common/schemas.py`. Every behavioural number carries `source:` or `assumption:`.

```yaml
id: hhr-haramain                      # unique, kebab-case; corridors use S<n>-<family>-<slug>
name_en: Haramain High Speed Railway
name_ar: قطار الحرمين السريع
layer: existing                       # existing | committed | hypothetical | historical
operator: SAR / HHR                   # or null
status: in_service                    # in_service | announced | design | procurement | construction | abandoned | generated
source: S-012                         # the line facts; committed/hypothetical also need `source_date`
source_date: 2026-10-31
accessed: 2026-10-31
line_type: hsr                        # hsr | conventional_passenger | mixed | commuter | metro | upgrade
design_speed_kmh: 300                 # source S-012
track: double                         # single | double | multiple
electrified: true
gauge_mm: 1435
length_km: 453                        # source S-012; hypothetical: computed from alignment
alignment: cities/ksa/lines/hhr-haramain.geojson   # ODbL credit in README
stations:                             # in running order; km_post from the first station
  - {id: makkah, name_en: Makkah (Rusaifah), name_ar: مكة المكرمة (الرصيفة), km_post: 0,   lat: 21.43, lon: 39.80, class: terminal, source: S-012}
  - {id: jeddah, name_en: Jeddah (Sulaymaniyah), name_ar: جدة (السليمانية), km_post: 77,  lat: 21.55, lon: 39.19, class: major, source: S-012}
  - {id: kaia,   name_en: KAIA, name_ar: مطار الملك عبدالعزيز, km_post: 94, lat: 21.70, lon: 39.17, class: airport, source: S-012}
  - {id: kaec,   name_en: KAEC (Rabigh), name_ar: مدينة الملك عبدالله الاقتصادية, km_post: 188, lat: 22.47, lon: 39.09, class: intermediate, source: S-012}
  - {id: madinah, name_en: Madinah, name_ar: المدينة المنورة, km_post: 449, lat: 24.49, lon: 39.59, class: terminal, source: S-012}
services:                             # stopping patterns and frequencies (sampled timetable, with the date)
  - {id: all_stop, stops: all, headway_min: 60, span: "06:00-23:00", sampled: 2026-10-31, source: S-013}
  - {id: express, stops: [makkah, jeddah, madinah], headway_min: 120, sampled: 2026-10-31, source: S-013}
fares_sar:                            # sampled, with the date; ranges where classes differ
  - {from: makkah, to: jeddah, economy: {low: 40, high: 60}, business: {low: 80, high: 120}, sampled: 2026-10-31, source: S-014}
running_time_model:                   # used by access.running_time; hypothetical lines take defaults from cities/ksa/assumptions/running_time.yaml
  accel_ms2: {value: 0.5, source: S-015}
  decel_ms2: {value: 0.6, source: S-015}
  cruise_kmh: {value: 300, source: S-012}
  dwell_s: {value: 120, assumption: "typical HSR intermediate dwell 90-180 s", assumption_id: A-access-003}
  turnaround_min: {value: 15, assumption_id: A-access-004}
observed_performance:                 # existing lines only; the reality check
  - {pair: [makkah, jeddah], minutes: 43, implied_avg_kmh: 107, source: S-013}
notes: "Makkah-Jeddah 77 km in about 43 min; test every 30-minute claim against this."
```

## Rules
- `layer: existing` requires `operator`, `status: in_service` and an operator source; `committed` requires `status`, `source_date` and `uncertainty_km` on the alignment file; `hypothetical` requires `generated_from` and the rules hash (`corridor-generator`).
- Station coordinates and km-posts are checked against the alignment (`validate` reports any station more than 2 km off the line or with non-monotonic km-posts).
- Fares and timetables are perishable: `sampled` dates are mandatory and are re-sampled before CP6.
- The coordinates above are illustrative placeholders for the schema; real files take them from OSM/operator sources with `S-xxx`.
- **Station siting (A-station-001, adopted by Tariq, 6 Nov 2026; `docs/stations-siting.md`).** In Tariq's words: do not colocate main stations on airport land; follow the pattern the Haramain already uses, a **city station** that serves the urban catchment (`hhr:jeddah`, Al-Sulimaniyah, class `major`) and, when the line passes an airport, a **separate airport station on a short branch** (`hhr:kaia`, class `airport`, `branch: true`). An airport stop is an extra halt, not a substitute for the city station. Mark such a halt `class: airport` and `branch: true` in the spec. The alignment is then written as a MultiLineString with parts `main` and `branch`, never as one LineString joined back to the main line. Check new stations with `uv run python -m rail.station_inventory`.
