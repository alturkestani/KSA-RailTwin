> **Document version:** docs/publish/figure-inputs/README.md v1.1 | 12 Nov 2026 | Author: PUBLISH_EXPORT (main; Tariq's answer Q8; v1.1: L1 score.json added after the clean-clone figure-test run) | Status: draft

# Figure inputs: the run outputs that the published figures are drawn from

Every modelled output here is **synthetic demand, uncalibrated: scenario comparison, not a forecast**. Costs and benefits are P10/P50/P90 ranges.

This folder holds the subset of the author's gitignored `runs/` that `uv run python -m common.figures build` reads to draw the 16 report figures (`docs/report/figures/fig01…fig16`, SVG and PNG, plus `figures-index.csv`) and the 16 deck figures (`docs/deck-figures/`, plus `figures.csv`). Tariq's answer Q8 (12 Nov 2026): ship only the figure inputs; the full `runs/` archive (about 5.0 GB) and the frozen appraisal-model copies go to Zenodo (DOI placeholder in [`../reproduce.md`](../reproduce.md)).

The paths mirror `runs/`, so the files sit outside `runs/` in the repository (rule 8 keeps `runs/` untracked) and are copied into place to use them. `SHA256SUMS` lists every file.

## How the set was chosen and checked (PUBLISH_EXPORT, 12 Nov 2026)

1. Traced every file and directory under `runs/` that the figure build opens, lists or globs (a Python audit hook plus wrappers on the parquet, CSV and GeoJSON readers), during `common.figures build --out <tmp> --deck <tmp>` on the author's full `runs/`: 105 files. One more file is added: `runs/r6/top5/L1/score.json` (64,957 bytes), the run file that fig06's decision-framing numbers come from. The build does not open it, but `tests/test_report_figures.py` checks fig06's numbers against it, and without it that test failed instead of skipping in the clean clone. Total: 106 files, 21,647,100 bytes.
2. Copied only those 105 files into a fresh `git archive` tree with no other `runs/` content and rebuilt: all 33 report outputs (32 figure files plus `figures-index.csv`) and all 33 deck outputs (32 figure files plus `figures.csv`) were **byte-identical** to the committed ones (`cmp`).
3. Scanned them for home or volume paths, email addresses and private names: none.

## Use

From the repository root, after `make setup`:

```bash
mkdir -p runs && cp -R docs/publish/figure-inputs/runs/. runs/
(cd docs/publish/figure-inputs && shasum -a 256 -c SHA256SUMS)   # optional integrity check
uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
git status --short docs/report/figures docs/deck-figures                # expect: no output (byte-identical)
```

Copying them into `runs/` also makes the figure tests run instead of skipping: in a clean clone of the public export, `tests/test_report_figures.py` and `tests/test_report_build.py` gave 45 passed, 7 skipped, 0 failed. Tests that need other `runs/` outputs keep skipping. The set rebuilds the figures only. The report text, the dashboard data and the other run-scoped checks need the full archive.

## Licence and attribution

These are outputs of this study's code (Apache-2.0). Files derived from OpenStreetMap through the road and rail networks (the isochrones under `runs/access/`, the reach tables and the corridor geometry behind the CBA cases) are derived databases under the **ODbL 1.0, (c) OpenStreetMap contributors**, and stay ODbL. Population and jobs figures come from GASTAT (General Authority for Statistics; derived, not official statistics) and WorldPop (CC BY 4.0), as credited in [`../../../NOTICE`](../../../NOTICE) and [`../../credits.md`](../../credits.md). Licence register row: "KSA Rail Twin figure inputs (run-output subset)" in `docs/licences.md`.

## Files

| file (under `docs/publish/figure-inputs/`) | bytes |
|---|---:|
| `runs/access/S0/jeddah/isochrone_door_to_door.geojson` | 11,339 |
| `runs/access/S0/reached.parquet` | 10,133 |
| `runs/access/S1/dammam/isochrone_door_to_door.geojson` | 2,581 |
| `runs/access/S1/jeddah/isochrone_door_to_door.geojson` | 15,208 |
| `runs/access/S1/meta.json` | 1,632 |
| `runs/access/S1/reached.parquet` | 10,337 |
| `runs/access/S5-station_addition-dhahran/dammam/isochrone_door_to_door.geojson` | 13,031 |
| `runs/access/S5-station_addition-dhahran/reached.parquet` | 10,890 |
| `runs/cba/CBA-S1-committed-programme/draws.parquet` | 11,093,472 |
| `runs/cba/CBA-S1-committed-programme/meta.json` | 3,467 |
| `runs/cba/CBA-S1-committed-programme/results.json` | 133,252 |
| `runs/cba/CBA-S1-committed-programme/switching_values.json` | 656 |
| `runs/cba/CBA-S1-committed-programme/tornado.csv` | 1,641 |
| `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-bisha/results.json` | 133,452 |
| `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-najran/results.json` | 133,551 |
| `runs/cba/CBA-S2-trunk_gap-al-jubayl-hafar-al-batin/results.json` | 133,158 |
| `runs/cba/CBA-S2-trunk_gap-al-kharj-bisha/results.json` | 133,646 |
| `runs/cba/CBA-S2-trunk_gap-ar-rass-ha-il/results.json` | 133,470 |
| `runs/cba/CBA-S2-trunk_gap-arar-hafar-al-batin/results.json` | 133,378 |
| `runs/cba/CBA-S2-trunk_gap-buraidah-ha-il/results.json` | 133,310 |
| `runs/cba/CBA-S2-trunk_gap-buraidah-hafar-al-batin/results.json` | 133,266 |
| `runs/cba/CBA-S2-trunk_gap-dammam-khobar-dhahran-al-kharj/results.json` | 133,223 |
| `runs/cba/CBA-S2-trunk_gap-jazan-najran/results.json` | 133,460 |
| `runs/cba/CBA-S2-trunk_gap-jeddah-yanbu/results.json` | 133,102 |
| `runs/cba/CBA-S2-trunk_gap-madinah-ar-rass/results.json` | 133,064 |
| `runs/cba/CBA-S2-trunk_gap-madinah-ha-il/results.json` | 132,994 |
| `runs/cba/CBA-S2-trunk_gap-madinah-yanbu/results.json` | 133,037 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-al-jubayl/results.json` | 133,063 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-bisha/results.json` | 133,436 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-dammam-khobar-dhahran/results.json` | 133,097 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-hafar-al-batin/results.json` | 132,891 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-jeddah/results.json` | 132,988 |
| `runs/cba/CBA-S2-trunk_gap-sakaka-ha-il/results.json` | 133,684 |
| `runs/cba/CBA-S2-trunk_gap-tabuk-sakaka/results.json` | 133,510 |
| `runs/cba/CBA-S2-trunk_gap-tabuk-yanbu/results.json` | 133,707 |
| `runs/cba/CBA-S2-trunk_gap-taif-bisha/results.json` | 133,272 |
| `runs/cba/CBA-S3-branch_spur-al-jubayl/results.json` | 132,219 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/results.json` | 132,264 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json` | 653 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/tornado.csv` | 1,622 |
| `runs/cba/CBA-S3-branch_spur-al-ula/results.json` | 133,378 |
| `runs/cba/CBA-S3-branch_spur-ar-rass/results.json` | 132,697 |
| `runs/cba/CBA-S3-branch_spur-arar/results.json` | 133,353 |
| `runs/cba/CBA-S3-branch_spur-at-ta-if/results.json` | 132,647 |
| `runs/cba/CBA-S3-branch_spur-az-zulfi/results.json` | 133,267 |
| `runs/cba/CBA-S3-branch_spur-badr-hunayn/results.json` | 132,954 |
| `runs/cba/CBA-S3-branch_spur-bisha/results.json` | 133,363 |
| `runs/cba/CBA-S3-branch_spur-duruma/results.json` | 132,624 |
| `runs/cba/CBA-S3-branch_spur-hafar-al-batin/results.json` | 133,216 |
| `runs/cba/CBA-S3-branch_spur-hawtat-sudayr/results.json` | 133,776 |
| `runs/cba/CBA-S3-branch_spur-khaybar/results.json` | 133,214 |
| `runs/cba/CBA-S3-branch_spur-rabigh/results.json` | 133,968 |
| `runs/cba/CBA-S3-branch_spur-rafha/results.json` | 133,783 |
| `runs/cba/CBA-S3-branch_spur-rumah/results.json` | 133,140 |
| `runs/cba/CBA-S3-branch_spur-sakaka/results.json` | 132,939 |
| `runs/cba/CBA-S3-branch_spur-tayma/results.json` | 134,142 |
| `runs/cba/CBA-S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind/results.json` | 133,063 |
| `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-045/results.json` | 133,303 |
| `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-135/results.json` | 133,244 |
| `runs/cba/CBA-S4-commuter_belt-buraidah-090/results.json` | 133,002 |
| `runs/cba/CBA-S4-commuter_belt-buraidah-180/results.json` | 132,376 |
| `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-180/results.json` | 132,818 |
| `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-315/results.json` | 132,458 |
| `runs/cba/CBA-S4-commuter_belt-jazan-090/results.json` | 132,469 |
| `runs/cba/CBA-S4-commuter_belt-jazan-315/results.json` | 132,599 |
| `runs/cba/CBA-S4-commuter_belt-jeddah-000/results.json` | 133,438 |
| `runs/cba/CBA-S4-commuter_belt-jeddah-315/results.json` | 133,615 |
| `runs/cba/CBA-S4-commuter_belt-madinah-045/results.json` | 133,035 |
| `runs/cba/CBA-S4-commuter_belt-madinah-225/results.json` | 133,225 |
| `runs/cba/CBA-S4-commuter_belt-makkah-045/results.json` | 132,661 |
| `runs/cba/CBA-S4-commuter_belt-makkah-090/results.json` | 132,783 |
| `runs/cba/CBA-S4-commuter_belt-makkah-315/results.json` | 133,430 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-000/results.json` | 132,855 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-090/results.json` | 132,715 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-135/results.json` | 132,859 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-225/results.json` | 132,627 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-270/results.json` | 132,910 |
| `runs/cba/CBA-S5-station_addition-al-jarn/results.json` | 131,373 |
| `runs/cba/CBA-S5-station_addition-al-jubayl-royal-commission/results.json` | 131,662 |
| `runs/cba/CBA-S5-station_addition-al-jubayl/results.json` | 131,693 |
| `runs/cba/CBA-S5-station_addition-al-oyun/results.json` | 131,349 |
| `runs/cba/CBA-S5-station_addition-al-qarah/results.json` | 131,393 |
| `runs/cba/CBA-S5-station_addition-al-umran/results.json` | 131,393 |
| `runs/cba/CBA-S5-station_addition-az-zulfi/results.json` | 130,901 |
| `runs/cba/CBA-S5-station_addition-dhahran/results.json` | 130,588 |
| `runs/cba/CBA-S5-station_addition-duruma/results.json` | 131,001 |
| `runs/cba/CBA-S5-station_addition-jubail-two-stations/results.json` | 131,626 |
| `runs/cba/CBA-S5-station_addition-thuwal/results.json` | 131,893 |
| `runs/r2/long-list/counts.json` | 893 |
| `runs/r2/score/meta.json` | 731 |
| `runs/r2/score/scores.parquet` | 34,044 |
| `runs/r2/score/summary.json` | 4,409 |
| `runs/r6/l6/meta.json` | 706 |
| `runs/r6/l6/score/S6-L6.csv` | 3,784 |
| `runs/r6/l6/score/meta.json` | 1,056 |
| `runs/r6/l6/search.json` | 161,163 |
| `runs/r6/pareto_front.csv` | 3,138 |
| `runs/r6/top5/L1.layout.yaml` | 268 |
| `runs/r6/top5/L1/meta.json` | 976 |
| `runs/r6/top5/L1/score.json` | 64,957 |
| `runs/r6/top5/L2.layout.yaml` | 224 |
| `runs/r6/top5/L3.layout.yaml` | 269 |
| `runs/r6/top5/top5.csv` | 6,017 |
| `runs/r7/fiscal/fiscal.json` | 333,726 |
| `runs/r7/fiscal/meta.json` | 719 |
| `runs/r7/vfm/vfm.json` | 21,046 |
| **total: 106 files** | **21,647,100** |
