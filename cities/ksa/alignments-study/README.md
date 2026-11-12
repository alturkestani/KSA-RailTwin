> **Document version:** cities/ksa/alignments-study/README.md v1.0 | 6 Nov 2026 | Author: STUDY_RJ_FAMILIES (main track builder) | Status: draft

# Riyadh–Jeddah study alignments (STUDY_RJ_FAMILIES)

Hypothetical alignments (ours), user-proposed by Tariq on 6 Nov 2026 (CP7-6): indicative engineering sketches, not designs. They are a research study, not the recommended programme, and they are not scored. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

These files are kept apart from `cities/ksa/alignments/` and the corridor library, so no R6/R7 input changes. S1, the Landbridge line file and HHR are unchanged.

- `corridors/<id>.yaml`: the route inputs, written by `study.rj corridors` from `cities/ksa/assumptions/rj_study.yaml`. Stations and waypoints are listed; a waypoint is a routing timing point, not a station (A-rj-002).
- `<id>.geojson` and `<id>.json`: the routed alignment and its summary, from `network.align.route_corridor` under the frozen v1 weights (hash `2b718ecb…` in each file). They are copied from `runs/study/rj/align-s1/<id>/` by `study.rj sidecars`.
- `haram_markers.geojson`: 49 Haram boundary marker boards as mapped in OpenStreetMap (S-rj-001; manifest row `osm-haram-markers-extract-2026-10-14`). These are points, not a boundary. No open official GIS boundary was found (S-rj-002), and no polygon is drawn.

Routes: RJ-LB (the announced proxies, routed by us in the mixed class), RJ-A (speed-oriented), RJ-B (via Taif), and RJ-C1/RJ-C2 (via Taif with a Makkah-area gateway outside the Haram boundary). See `docs/rj-routes-study.md`.

**Licence and credits.** These files are derived from:
- Copernicus DEM GLO-30. Credit: produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA; all rights reserved.
- ESA WorldCover 2021 v200 (CC BY 4.0).
- OpenStreetMap data, (c) OpenStreetMap contributors, ODbL 1.0.

Treat them as ODbL (share-alike), the same as `cities/ksa/alignments/`. The licence register is not changed by this study: every input is already in it.
