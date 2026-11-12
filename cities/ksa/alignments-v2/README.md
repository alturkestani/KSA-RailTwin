> **Document version:** cities/ksa/alignments-v2/README.md v1.0 | 4 Nov 2026 | Author: FIX_R7 builder | Status: draft

# Routed alignments under weights v2 (FIX_R7): a parallel set, not adopted

Hypothetical layer (ours): indicative engineering sketches, not designs. Label: screening input, not a forecast.

Same schema as `cities/ksa/alignments/` (`<id>.json` sidecar plus `<id>.geojson`), routed with the frozen **weights v2** `cities/ksa/assumptions/align_weights_v2.yaml` (hash in `align_weights_v2.sha256`). Each sidecar adds `weights_file`. They hold only the two routed CP7 corridors, `S3-branch_spur-al-kharj` and `S4-commuter_belt-riyadh-225`. `S5-station_addition-duruma` is a station addition and is not routed.

Produced by `uv run python -m network.align_v2 route --ids S3-branch_spur-al-kharj,S4-commuter_belt-riyadh-225 --seed 1` (runs `runs/align/corridors-v2-s1/`). They feed the R7 sensitivity only (`funding.r7v2`, `docs/alignments.md` §4c). The corridor generator, the judge and every R4–R7 base figure keep reading `cities/ksa/alignments/` (v1). Map data © OpenStreetMap contributors (ODbL); Copernicus GLO-30 DEM; ESA WorldCover 2021 v200 (CC BY 4.0), as in `docs/alignments.md` §2.
