> **Document version:** cities/ksa/alignments/README.md v1.0 | 1 Nov 2026 | Author: R4_ALIGN builder | Status: draft

# Routed alignments (R4_ALIGN): sidecars for the corridor generator

Hypothetical layer (ours): indicative engineering sketches, not designs. Label: screening input, not a forecast.

- `<id>.geojson`: the routed alignment (simplified to about 20 m) and the straight sketch through the same stations.
- `<id>.json`: the run summary (length, detour ratio, tunnel/viaduct/earthworks km, cut/fill, speed restrictions, terrain shares, stations key, weights hash, run folder). `screening.corridors generate --alignments cities/ksa/alignments` reads it.
- `summary.csv`: one row per corridor.
- `alternatives/`: trunk pairs not generated in R2 (dominated or not a speed gap), routed only for the detour test (A-corr-005).

Produced by `network.align route-all` + `network.align apply` with the frozen weights `cities/ksa/assumptions/align_weights.yaml` (hash in `align_weights.sha256`). Method: `docs/alignments.md`.

**Licence and credits.** These files are derived from:
- Copernicus DEM GLO-30. Credit: produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA; all rights reserved.
- ESA WorldCover 2021 v200 (CC BY 4.0).
- OpenStreetMap data, (c) OpenStreetMap contributors, ODbL 1.0.

Treat them as ODbL (share-alike) until Tariq decides otherwise. Whether they are a Produced Work or a Derivative Database of OSM is an open release question (`docs/licences.md`).
