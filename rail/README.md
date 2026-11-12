> **Document version:** rail/README.md v1.2 | 6 Nov 2026 | Author: R0 builder; FIX_HHR_JEDDAH (branches, station siting); FIX_HHR_REROUTE (A-station-001 adopted) | Status: draft

# `rail/` (W1, R1a)

Will own the national rail layers (PROJECT.md section 5, W1): OSM rail relations plus SAR/HHR published lines, stations, timetables and fares (with the dates sampled), and planned lines digitised with source and uncertainty, written as line YAML (`line-yaml` skill) and GeoJSON under `cities/ksa/lines/`. The three layers `existing`, `committed/under procurement` and `hypothetical (ours)` never mix; planned lines are "announced/planned", never "existing". Owners: `rail-data-scout`, `gis-network-engineer`.

Status at R0: skeleton only (`uv run python -m rail.cli version`). No methods are implemented or chosen here yet; the owning milestone decides them under the rules in `CLAUDE.md`, and every real-world constant it introduces lives in YAML with `source:` or `assumption:` and a row in `docs/assumptions.md`. Modelled outputs carry the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".

## Branch lines and station siting (FIX_HHR_JEDDAH, 6 Nov 2026)

- `rail.lines build` writes a line with a branch station (`branch: true` in `rail/specs/<id>.yaml`) as a **MultiLineString** with properties `parts` (`main`, `branch`), `part_to` and `part_km`. The branch part starts at the junction. Before this fix the branch was appended to the main LineString, and HHR carried a 17.3 km straight chord from KAIA back to Al-Sulaimaniyah (`docs/network.md` §HHR geometry). km-posts are unchanged. Check: `uv run python -m rail.hhr_check --before-rev 0cc369e`.
- **Station siting rule (A-station-001, adopted by Tariq, 6 Nov 2026; `docs/stations-siting.md`).** In Tariq's words: do not colocate main stations on airport land. Follow the Haramain pattern: a city station that serves the urban catchment and, when the line passes an airport, a separate airport station on a short branch. An airport stop is an extra halt, not a substitute for the city station. Inventory: `uv run python -m rail.station_inventory --out runs/fix-hhr/stations-inventory.csv`.
