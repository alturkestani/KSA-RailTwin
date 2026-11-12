> **Document version:** docs/geo-verify.md v0.6 | 31 Oct 2026 | Author: GEO_VERIFY builder (track r1a); §changes-after-UTM-fix, §11 GASTAT back-test and §12 primary-city back-test by CP2_PREP | Status: draft

# Geospatial verification and estimation (GEO_VERIFY)

Method: `.claude/skills/geo-verify/SKILL.md` (standing method, 31 Oct 2026). Code: `screening/geo_verify/`. Every derived value here is a **second, independent line of evidence**: it never replaces an official or relayed figure, and no `population` value was written or changed. Population estimates are derived evidence, not a forecast; the modelled screening outputs they feed stay **synthetic demand, uncalibrated: scenario comparison, not a forecast**.

**Headline.** Both population estimators **fail the back-test gate** (median absolute error 67 % for the grid method and 59 % for buildings × occupancy, against a 30 % gate). Their values are therefore **record-only**: they appear in register `notes` and the method logs, never in `population`, and nothing ranks on them. Two freight terminals were located (OSM spur end + Sentinel-2); the Al-Sulaymaniyah HHR station was confirmed on imagery. The served list did not change (8 before, 8 after). The Wikidata point for Al-Qarā lies 1,010 km outside its governorate polygon. All 19 Qassim register points sit inside their governorate polygon.

## 1. Reproduce

```
R="uv run --with rasterio python -m screening.geo_verify.cli"   # rasterio not yet in pyproject (integration)
$R backtest --seed 1
$R estimate --seed 1 --which no-pop          # then --which secondary; optional --region <slug>
$R stations --seed 1                          # imagery windows + method log; --apply --no-imagery-check writes stations.geojson
$R seat --seed 1 --lat <lat> --lon <lon> --governorate-ar "<name_ar>" --label <label>
$R validate-geocodes --seed 1
$R served-rerun --seed 1
$R apply-notes --seed 1                       # register notes + the C-geo table in docs/sources/conflicts.md
```

The full sequence is `screening/geo_verify/scripts/geo-clean-rerun.sh` (tracked since CP2_PREP; it was `logs/geo-clean-rerun.sh`, gitignored, O9; run log `logs/geo-clean-rerun.log`, gitignored); it was run from a clean tree and reruns are byte-identical (`git status` clean afterwards). Since the UTM fix (section 10) the outputs differ from that first run. Run outputs: `runs/geo_verify/<command>/` with `meta.json` (seed, config hash, data hash, code version) and append-only `method_log*.jsonl` (id, method, inputs, parameters, value, band, run id). One entry was appended by hand after the run: `geo-seat-b5d5f703` (Wadi ad-Dawasir imagery reading, section 5); a rerun of `seat` deletes it, so it is copied in full in `docs/sources/conflicts.md` C-geo-W1.

## 2. Sources, parameters and gates

| item | use | manifest id(s) | licence row |
|---|---|---|---|
| WorldPop 2020 100 m constrained UN-adjusted (Saudi Arabia) | estimator 1 (grid sum over the extent) | worldpop-sau-2020-100m-unadj-constrained | `docs/licences.md` (CC BY 4.0) |
| Microsoft Global ML Building Footprints, release 2026-02-03 | extents (DBSCAN) and estimator 2 | msbuildings-dataset-links-2026-02-03; msbuildings-ksa-<quadkey>-<part> (201 files, 593 MB; cited as group `msbuildings-ksa-2026-02-03` in the method logs) | CDLA-Permissive-2.0 (corrected from ODbL after the verifier, F1) |
| Copernicus Sentinel-2 L2A COGs (AWS open data, Earth Search STAC) | visual confirmation windows, streamed (no file kept in the repo; PNG windows in the gitignored cache only) | sentinel-2-l2a-cogs-<window> (10 rows, one per cached window, with the scene COG URL; group id `sentinel-2-l2a-cogs` in the method logs) | Copernicus terms ("Contains modified Copernicus Sentinel data 2026") |
| OSM GCC extracts (rail, places, admin) | station evidence, seats, polygons | osm-ksa-rail-extract-2026-10-14, osm-gcc-places-extract-2026-10-14, osm-gcc-admin-extract-2026-10-14 | ODbL 1.0 |
| Qassim pilot raw geocodes (Nominatim responses) | use case d | pilot-qassim-geocode-01 … 40 | ODbL 1.0 |

Not used: GHS-POP and GHS-BUILT-S (the 10° tiles were not needed once the footprints were cached; `extents.morph_close` is implemented and tested and is applied to the footprint mask), VIIRS (download needs an account: rule 7), Google Maps (no visual check was made; nothing Google-derived is in the repo).

Parameters (all assumptions, `docs/assumptions.md` A-geo-001…010; values in `screening/geo_verify/params.yaml`): DBSCAN eps 100 m, min_samples 5, snap 1,500 m, close kernel 3 cells, minimum footprint 20 m², household size 4.8 (Census 2022 average Saudi household; non-Saudi 2.7: S-geo-001 below), dwellings per building 1.0, residential share 0.8 (persons per building 3.84), window ±25 km, back-test cap 1,000,000.

Extent rule: the DBSCAN clusters of footprint centroids that have a building within the snap radius of the settlement point; rasterised on the WorldPop 100 m grid and closed. Metric CRS by longitude (UTM 36N–40N, zone = floor((lon + 180) / 6) + 1, EPSG 326<zone>; corrected by CP2_PREP, section 10); geodesic distances on WGS84 (`geom.py`).

Gates: free disk at start 54 GiB, at the end 54 GiB (`df -h ~`, 31 Oct 2026, 10:29 and 11:04; gate 15 GiB never approached). Geo cache `data/ksa/geo/`: 790 MB at the end (cap 5 GB). Microsoft tiles are fetched per quadkey only where a settlement window needs them; because 186 register rows span the country, 201 of the 306 Saudi files were fetched (593 of 610 MB). They are vector tiles read per window, not a raster mosaic.

Source added: **S-geo-001**: Census 2022 average household size: "The total number of Saudi households was 4.2 million, with an average size of 4.8 individuals per household"; "The average size of non-Saudi family members was 2.7 individuals per household". Saudipedia, "Saudi Census 2022", https://saudipedia.com/en/saudi-census-2022, page dated 15 Jul 2022 (results announced 31 May 2023), accessed 31 Oct 2026; secondary (relays GASTAT). Primary to find: GASTAT Census 2022 household tables. For integration into `docs/sources/index.csv`.

## 3. Back-test (gate)

Sample: 10 register settlements with a Census 2022 figure (all relayed by citypopulation.de crediting GASTAT, `secondary`), drawn with seed 1 within four strata (2 of 500k–1M, 3 of 50–500k, 3 of 10–50k, 2 below 10k; settlements above 1M excluded, A-geo-010). Run `runs/geo_verify/backtest/` (`backtest.csv`, `summary.json`, `method_log.jsonl`).

| stratum | settlement | Census 2022 (source) | buildings in extent | grid estimate | buildings estimate | extent km² | grid abs % error | buildings abs % error |
|---|---|---|---|---|---|---|---|---|
| 500k–1M | Hofuf (Al-Hufuf–Al-Mubarraz) | 729,606 (S-eastern-001) | 107,108 | 640,520 | 411,295 | 190 | 12 | 44 |
| 500k–1M | Aṭ-Ṭa'if | 563,282 (S-makkah-001) | 32,937 | 195,117 | 126,478 | 60 | 65 | 78 |
| 50–500k | Sakaka | 204,174 (S-al_jouf-001) | 9,978 | 45,072 | 38,316 | 22 | 78 | 81 |
| 50–500k | Ahad Rafidah | 79,202 (S-asir-001) | 6,056 | 23,141 | 23,255 | 14 | 71 | 71 |
| 50–500k | Al-Majma'ah | 70,243 (S-riyadh-008) | 9,590 | 33,783 | 36,826 | 22 | 52 | 48 |
| 10–50k | Al-Qaisumah | 27,307 (S-eastern-001) | 3,434 | 8,709 | 13,187 | 5 | 68 | 52 |
| 10–50k | Samtah | 43,301 (S-jazan-002) | 7,112 | 16,723 | 27,310 | 9 | 61 | 37 |
| 10–50k | Hawtat Bani Tamim | 30,720 (S-cp1-020) | 2,289 | 9,676 | 8,790 | 7 | 69 | 71 |
| below 10k | Mawqaq | 3,148 (S-hail-001) | 1,319 | 5,580 | 5,065 | 4 | 77 | 61 |
| below 10k | Al-Ghat | 8,683 (S-cp1-014) | 3,575 | 7,764 | 13,728 | 7 | 11 | 58 |

**Median absolute % error: grid 67 %, buildings 59 %. Gate 30 %: neither method may rank.** Both run low in 8 of 10 cases: the cluster extent captures only part of the census locality (Taif: 33k buildings for 563k people; Sakaka: 10k for 204k), and the footprint layer has coverage gaps (section 6).

Sensitivity (declared ranges only; `runs/geo_verify/backtest/sweep.csv`, `uv run --with rasterio python -m screening.geo_verify.scripts.geo_sweep`, formerly `logs/geo_sweep.py`), median abs % error grid / buildings:

| eps (m) | min_samples | snap (m) | grid | buildings | census per footprint (median) |
|---|---|---|---|---|---|
| 100 | 5 | 1,500 (declared) | 67 | 59 | 7.64 |
| 150 | 5 | 3,000 | 45 | 53 | 4.44 |
| 200 | 3 | 3,000 | 42 | 53 | 4.00 |
| 200 | 5 | 3,000 | 42 | 52 | 4.02 |

(12 combinations in the file.) No combination inside the declared ranges reaches 30 %. The declared parameters were kept (no post-hoc tuning on the test sample); a validation sample with another seed was not drawn, because no setting passed. Decision: **both estimators record-only**. A re-test needs a better extent (GHS-BUILT-S or a census-locality boundary) and gap-free footprints.

## 4. Use case a: stations (`runs/geo_verify/stations/method_log.jsonl`; sites and evidence in `screening/geo_verify/station_sites.yaml`)

All windows are 3 × 3 km Sentinel-2 TCI (10 m), the newest scene with < 5 % cloud between 1 Jun and 30 Oct 2026. What was seen is a visual reading.

| station | point | scene (date, cloud %) | seen | result | method log |
|---|---|---|---|---|---|
| hhr:jeddah Al-Sulaymaniyah | 21.517643, 39.245363 (OSM way 485762503) | S2B_37QED_20261027_0_L2A (27 Oct, 0.013) | station roof and platform canopies at the centre beside the HHR alignment | **confirmed** (already located; unchanged) | geo-stn-d5536837 |
| sar-north-freight:al-jalamid (proxy) | 31.224245, 39.969887 | S2B_37REQ_20261030_0_L2A (30 Oct, 2.04) | single track through desert; no yard or plant | proxy is not the terminal | geo-stn-6e3aab20 |
| sar-north-freight:al-jalamid (OSM spur end node 8879771880) | 31.4884683, 39.9250479 | same scene | curved rail loop/embankment and plant buildings | **located**, `osm_spur_end:node/8879771880+imagery:sentinel-2`, confidence medium, ±2 km, `site_status: inferred_imagery` | geo-stn-622f20a7 |
| sar-north-freight:al-baithah (proxy) | 27.653479, 44.002713 | S2C_38RLR_20261029_0_L2A (29 Oct, 0.007) | track and roads only | proxy is not the terminal | geo-stn-c564133c |
| sar-north-freight:al-baithah (OSM spur end node 5396737260) | 27.6650136, 43.9942105 | same scene | balloon loading loop and a fenced compound | **located**, `osm_spur_end:node/5396737260+imagery:sentinel-2`, confidence medium, ±1 km | geo-stn-ad964120 |
| sar-north-freight:ras-al-khair | 27.49239, 49.213979 | S2B_39RUL_20261028_0_L2A (28 Oct, 0.92) | rail wye and loops in the industrial city; which loop is the terminal is not determinable at 10 m | unlocated (unchanged) | geo-stn-9db3aff0 |
| sar-east-freight-legacy:riyadh-dry-port | 24.642673, 46.743604 | S2A_38RPN_20261025_0_L2A (25 Oct, 0.36) | window on the scene edge (west half empty); paved yard with sidings ~1 km NW | unlocated (consistent, not confirmed) | geo-stn-02205814 |
| sar-east-freight-legacy:dammam-port | 26.428741, 50.121524 | S2C_39RVK_20261030_0_L2A (30 Oct, 2.05) | urban fabric, cloud over the east half | unlocated (inconclusive) | geo-stn-f05a29b8 |
| sar-east-freight-legacy:al-ahsa | 25.390704, 49.565712 | S2C_39RUJ_20261030_0_L2A (30 Oct, 0.11) | window cached, not inspected in the time-box | unlocated | geo-stn-17a01bf2 |

The 10 committed/planned stops (GCC railway 3, Landbridge 5 incl. Al-Jumum, Riyadh Rail Link 2) were **not** attempted on imagery: no site is published, and imagery cannot locate a station that is not built. They stay `unlocated:town_centroid_proxy` (no site guessed). Count: 16 unlocated before, **14 after**; 2 located (Al-Jalamid, Al-Ba'ithah freight terminals); 1 existing station confirmed.

Served test (`runs/geo_verify/served-rerun/`; `network.distances register` then `screening.funnel long-list`, seed 1): long list 157, served **8 before and 8 after**, same names (Abqaiq, Al-Madinah, Al-Majma'ah, Dammam, Hofuf, Jiddah, Makkah, Riyadh). The two new sites are mine terminals far from any register town within the served radius. Note for integration: `stations.geojson` is also written by `rail.lines build` (not owned here); a rebuild would drop the two sites unless `station_sites.yaml` is re-applied (`stations --apply`).

## 5. Use case b: Al-Qarā and Wadi ad-Dawasir (Al-Khamasin)

Full tables in `docs/sources/conflicts.md` C-geo-Q1 and C-geo-W1.
- **Al-Qarā**: the Wikidata/Wikipedia point is outside the governorate polygon by 1,010.29 km (geo-seat-8bc6e532); the OSM label node, the OSM seat (Al Tawilah) and the citypopulation point are inside, 6.92, 5.83 and 9.93 km from the boundary. The OSM seat sits in a 900-building cluster of 3.2 km². Derived estimate (record-only): central 1,562, band 235–5,512 (geo-est-d2649867).
- **Wadi ad-Dawasir**: the register point is OSM city node 2632133047; the Al-Khamasin village node lies 4.17 km NW; both inside the governorate polygon. Sentinel-2 shows one continuous built-up area spanning both (geo-seat-b5d5f703). The footprint layer has no buildings there (gap west of 44.824 E). Seat identity: open (no source states the name relation).

## 6. Use case c: estimates (`runs/geo_verify/estimate/{no-pop,secondary}/`)

- **22 rows without a population**: 13 received an estimate (2 from one method only: Rijal Almaa and Abanat, where the grid gave 0); 9 got none (no footprint cluster within the snap radius: Ghāmid az-Zinād, Al-Amwah, Balqarn, Bariq, Al-Udayd, Al-Bayda, Ar Rayth, Harub, Fayfa). Values and bands are in each row's `notes` and in `estimates-no-pop.csv`.
- **164 rows with a relayed (secondary) figure**: 127 received an estimate, 37 none. The median ratio of derived central to relayed figure is 0.51; 103 rows diverged by more than 25 % (93 below, 10 above) at the first run and are logged as C-geo-001…103 in `docs/sources/conflicts.md`, as weak evidence only (the estimators failed the gate); after the UTM fix 102 do (92 below, 10 above; 'Unaīzah moved from −26.6 % to −23.4 %; section 10).
- Every row carries `GEO_VERIFY 31 Oct 2026: …` in `notes` (central, band, both method values, "record-only", `primary_to_find`, method-log id). `population`, `pop_type`, `pop_source_status` and `primary_to_find` were **not** changed: the skill keeps derived values out of `population` while the back-test fails. `cities/ksa/candidates-pilot.parquet` was re-merged (`screening.merge`; only `notes` differ) and `cities/ksa/zones/candidates-pilot-r1a.parquet` refreshed.
- Band rule: central = geometric mean of the non-zero method values; band = min–max widened by each method's back-test median error (so a band can be wider than the spread of the methods).

**Footprint coverage gaps** (finding): several tiles hold buildings only in part of their area (e.g. tile 122311131 has none west of 44.824 E, across Wadi ad-Dawasir town), and many Asir and Jazan mountain towns have no cluster at all. Together with partial extents, this explains the low bias. The gap map was not built in the time-box.

## 7. Use case d: Qassim geocodes (`runs/geo_verify/validate-geocodes/`)

- Register: all **19/19** `pilot-qassim` points are inside the governorate polygon named in their row (names matched after unifying alef, taa marbuta and alef maqsura spellings); distance to the boundary 2.32–47.30 km (2.33–47.55 km before the UTM fix). No flag.
- Raw files: the 40 files in `data/ksa/pilot-qassim/raw/geocode/` are now in the manifest (`pilot-qassim-geocode-01…40`, ODbL, accessed 2026-10-30 = pilot run date). 39 are Nominatim responses (1 is an Overpass rail extract): 25 return a hit, every one inside a Qassim governorate polygon; 14 are empty responses. No point falls outside Qassim.

## 8. Not done in the time-box

GHS-POP as a third estimator; a validation sample with a second seed; Al-Ahsa freight window inspection; a footprint coverage-gap map; spot imagery checks of derived extents beyond the back-test; the `red-team-verifier` spot-check of 10 derived values (VERIFY_R1 covers it).

## 9. Verifier fixes (31 Oct 2026, after `docs/status/verify-GEO_VERIFY.md`)

- F1: the Microsoft footprints licence is **CDLA-Permissive-2.0** (README "License" section), not ODbL; corrected in `docs/licences.{md,csv}`, the 202 `msbuildings-*` manifest rows and `footprints.py`. No share-alike obligation applies. Not owned here, for the coordinator: the geo-verify skill (section 1) and `NOTICE` should say CDLA-Permissive-2.0 too.
- F2: 10 Sentinel-2 window rows added to the manifest (`sentinel-2-l2a-cogs-*`, SHA-256 of the cached PNG render, the scene COG URL, Copernicus terms).
- O1: the run metas' `data_hash` predates these manifest rows (the runs were not repeated after the registry-only fix).

## 10. Changes after the UTM fix (CP2_PREP item 3, 31 Oct 2026)

**Fix.** `geom.utm_epsg` picked one zone east of the EPSG definition (37N west of 36° E, 38N for 36–42° E, 39N east of 42° E; verify-GEO_VERIFY O10). It now returns EPSG 326<zone> with zone = floor((lon + 180) / 6) + 1: 36N west of 36° E, 37N 36–42° E, 38N 42–48° E, 39N 48–54° E, 40N 54–60° E. Checked against pyproj `query_utm_crs_info` (EPSG database) at Jeddah 39.2° E (32637), Riyadh 46.7° E (32638) and Dammam 50.1° E (32639), and at the boundaries 35.999/36.0/36.001, 41.999/42.0/42.001 and 47.999/48.0/48.001° E (`tests/test_cp2_item3_utm.py`; the two wrong asserts in `tests/test_geo_verify.py` corrected). Rows at 48–54° E (zone 39N) kept their zone. The old zone overstated planar lengths by 0 to 1.00 % (median 0.44 %) at the 140 estimated points (meridional scale factor old/new, `scale_old_over_new_minus_1` in the diff), so areas by up to about 2 %; DBSCAN (eps 100 m) and the snap radius saw slightly longer distances than the true ones.

**Re-run** (seed 1; cached tiles only, no download; about 45 s in total): `backtest`, the sweep, `estimate --which no-pop`, `estimate --which secondary` (together every register row, the same set as `--which all`), `validate-geocodes` and the six `seat` checks of `geo-clean-rerun.sh` (computed in `runs/cp2_prep/item3/after/seat/` and merged into `runs/geo_verify/seat/method_log.jsonl`, which keeps the hand entry geo-seat-b5d5f703). The pre-fix outputs are kept in `runs/cp2_prep/item3/before/`; the cell-by-cell diff is `runs/cp2_prep/item3/utm-diff.csv` (`uv run python -m screening.geo_verify.scripts.utm_diff`). The `meta.json` files then carried the manifest hash of that moment (`data_hash` 5b358a95…). At the CP2_PREP close the whole `geo-clean-rerun.sh` sequence (including `stations`, `served-rerun` and `apply-notes`) was re-run from the clean commit 2c00ac2 with the 284-row manifest: no tracked file changed, the hand entry geo-seat-b5d5f703 survived, and every run meta except `merge` (not part of the script) now records code version `r1-8-g2c00ac2` and `data_hash` 3f33846c… (O1 closed for these runs; log `logs/cp2-geo-clean-rerun.log`). `stations` and `served-rerun` do not use `geom.utm_epsg` and were not re-run.

| output | rows with a value | rows changed | max abs relative change | median abs relative change (all rows / changed rows) |
|---|---|---|---|---|
| estimate central (no-pop 13 + secondary 127) | 140 | 74 | 91.2 % (Al Harth, 665 → 1,272) | 0.006 % / 0.061 % |
| estimate band low and high | 140 | 140 (the back-test errors that widen the band moved) | 92.9 % / 89.6 % | 0.037 % / 0.038 % |
| grid (WorldPop sum) | 138 non-zero | 46 | 92.9 % | 0.000 % / 0.216 % |
| buildings in extent | 140 | 71 (66 up, 5 down) | 89.5 % | 0.002 % / 0.066 % |
| extent km² | 140 | 55 | 68.8 % | 0.000 % / 0.362 % |
| back-test settlements | 10 | 5 (Ta'if, Ahad Rafidah, Al-Majma'ah, Samtah, Mawqaq) | 0.37 % (Mawqaq extent) | n/a |
| seat km to boundary | 6 | 5 | 0.50 % (Al-Khamasin 43.73 → 43.51 km) | n/a |
| Qassim geocodes km to boundary | 19 | 19 | 0.87 % | n/a |

The 46 rows without an estimate (9 no-pop, 37 secondary) still have none. Large changes are DBSCAN threshold effects, not scale errors: shorter true distances join clusters that were just apart at eps 100 m (Al Harth 305 → 578 buildings; Al Aydabi +11 %; Layla +8 %); five rows lost buildings (largest Al-Quwayiyah 2,656 → 2,392, −10 %), which is not traced in this run (border points join the first core neighbour's cluster and the snap selection can change; to check before any re-test). Divergence > 25 % against the relayed figure: **102 rows** (92 below, 10 above), was 103; 'Unaīzah moved from −26.6 % to −23.4 % and drops out. Median ratio derived / relayed 0.51 (0.5116 → 0.5099).

**Gate decision unchanged.** Back-test median absolute error grid 66.74 % → 66.73 %, buildings 59.44 % → 59.50 % (rounded 67 % and 59 % as in section 3); `may_rank` false for both before and after. The sweep's best setting is still 42.3 % (eps 200, min_samples 3, snap 3,000; was 42.3 %), so no declared setting reaches the 30 % gate. Both estimators stay **record-only**; nothing ranks on them.

**Follow-up done by the builder:** `uv run --with rasterio python -m screening.geo_verify.cli apply-notes --seed 1` rewrote the register `notes` and the C-geo table in `docs/sources/conflicts.md` from the new estimates in the same commit as this section (2d1e43b; C-geo-001…102), and the GEO_VERIFY run metas were refreshed on the clean tree 2c00ac2 (`docs/status/main.md`, CP2_PREP block).


## 11. WorldPop back-test against the GASTAT Census 2022 totals (CP2_PREP item 1 addendum, 31 Oct 2026)

Report only; nothing here changes a population in the base case. Run: `uv run python -m screening.gastat backtest --seed 1` → `runs/gastat/backtest/` (`governorates.csv`, `cities.csv`, `summary.json`, `meta.json`). Raster: WorldPop 2020, 100 m, constrained, UN-adjusted (manifest `worldpop-sau-2020-100m-unadj-constrained`, the grid fallback of `network.zones`). Reference: the GASTAT Census 2022 governorate and city totals relayed by DataPulse (S-cp2-gastat-001), checked against the primary region tables TA1/TA9 (S-cp2-gastat-002/S-cp2-gastat-003; all 13 regions match). Ratio = grid / census.

| test | n | median ratio | IQR | median abs % error | within 30 % |
|---|---|---|---|---|---|
| grid summed inside each OSM governorate polygon (149 of 150; Al Amoah has no polygon, C-r1a-20) | 149 | **1.280** | 1.018–1.682 | 37.3 | 66 |
| settlement allocation for the 60 cities (A-r1a-004 radius circle, nearest settlement; 59 targets, Al-Hofuf + Al-Mubarraz combined) | 59 | **0.480** | 0.307–0.727 | 55.0 | 16 |
| earlier: settlement allocation on the 164 tabulated rows (A-r1a-004; `docs/network.md`) | 164 | 0.637 | 0.332–1.104 | — | — |

Reading (analysis): over whole governorates the UN-adjusted 2020 grid over-counts (it sums to 34.7 M inside the polygons against 32.2 M in the census; median by region from 0.94 in Ḥā'il to 1.67 in Qassim); at the settlement level the fixed circles miss most of a city's built extent (Abha 0.03; Al-Kharj 0, a pilot-only row without an OSM node, so no grid allocation) or collect neighbours (Al-Lith 1.84, Dhahran 1.62). Neither reaches the 30 % gate (§3), so the grid stays a gap-fill under the P1a gate, never a replacement. The settlement ratio is the one that applies to the gap-fill rows: the item 1.2 sensitivity now divides grid-only populations by **0.48** (A-screen-036; the earlier 0.64, A-screen-034, is kept as a comparison run). Results: `docs/screening-pilot.md` §7.

The addendum's third corroboration method (Census 2010 city > 5,000 grown at its governorate's 2010→2022 ratio, A-screen-035) was back-tested on the same day against the 138 official 2022 city figures it matches: median absolute error 16.9 % (IQR 7.1–36.6 %), 96 within 30 % (`runs/gastat/apply/summary.json`). It is an allowed corroboration method, not a population source.

## 12. WorldPop back-test against the primary GASTAT cities of 5,000 or more (CP2_PREP item 1 addendum 2, 31 Oct 2026)

Report only; nothing here changes a population in the base case. Run: `uv run python -m screening.gastat primary --seed 1` → `runs/gastat/primary/backtest_cities.csv` and `summary.json` (`backtest_cities`). Reference: the primary Census 2022 TA1 city table exported from the GASTAT dashboard (S-cp2-gastat-008; it supersedes the relayed file, which matches it exactly, C-gastat-001). Extent: the settlement's WorldPop allocation (A-r1a-004 radius by place class, nearest settlement), the same measure as §11, because no built-up or admin polygon exists for most of the 271 cities; for the 202 matched cities (201 settlements; Alhufuf + Almubriz combined) the ratio is grid allocation / primary figure.

| primary city size | n | median ratio | IQR | median abs % error | within 30 % |
|---|---|---|---|---|---|
| 5,000–9,999 | 68 | 1.058 | 0.633–1.529 | 44.4 | 26 |
| 10,000–29,999 | 60 | 0.779 | 0.460–1.318 | 48.1 | 19 |
| 30,000–99,999 | 44 | 0.550 | 0.291–0.747 | 46.4 | 12 |
| ≥ 100,000 | 29 | 0.375 | 0.238–0.600 | 62.5 | 4 |
| **all** | **201** | **0.710** | **0.370–1.157** | **49.6** | **61** |

Old and new values: the settlement ratio was 0.637 on the 164 tabulated rows (A-screen-034), 0.480 on the 60 relayed cities (§11, A-screen-036) and is **0.710** on the 201 primary-matched settlements (A-screen-039). The shift comes from the sample: the 60-city sample was dominated by large cities whose extent spills far beyond the 10 km circle (≥ 100,000: median 0.375), while the primary table adds 128 towns under 30,000, where the circle catches the town and often its neighbours (5,000–9,999: median 1.058). Extremes: Al Kharj, Turubah (Makkah) and Dariyah get 0 (pilot-only rows with no OSM place node, so no grid allocation); Dakhnh 6.10 and An Nabiyah 5.27 collect neighbouring villages. The size dependence means a single ratio is a crude correction; the sensitivity in `docs/screening-pilot.md` §7 uses ÷ 0.71 for grid-only rows (all under 5,000 in the census sense, or unmatched), never in the base case. The gate decision of the geo-verify estimators (§3, record-only) is unaffected.
